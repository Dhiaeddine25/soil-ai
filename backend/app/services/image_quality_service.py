from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import logging
import numpy as np
from PIL import Image, ImageStat, UnidentifiedImageError

from app.core.config import Settings
from app.schemas.prediction_quality import QualityCheck


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageQualityMetrics:
    width: int
    height: int
    brightness: float
    contrast: float
    sharpness: float


@dataclass(frozen=True)
class PreparedImage:
    quality_check: QualityCheck
    image_224: np.ndarray | None = None


class ImageQualityService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, image_bytes: bytes | None) -> QualityCheck:
        return self.prepare_for_prediction(image_bytes).quality_check

    def prepare_for_prediction(self, image_bytes: bytes | None) -> PreparedImage:
        if not image_bytes:
            logger.info("[Quality] IMAGE RECEIVED: empty file")
            return PreparedImage(
                quality_check=QualityCheck(valid=False, status='image_non_exploitable', issues=['empty_file'])
            )

        logger.info("[Quality] IMAGE RECEIVED: bytes=%d", len(image_bytes))

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.load()
                image = image.convert('RGB')
                logger.info("[Quality] IMAGE SIZE: width=%d, height=%d", image.size[0], image.size[1])
                logger.info("[Quality] IMAGE MODE: %s", image.mode)
                width, height = image.size
                if width < self.settings.quality_min_width or height < self.settings.quality_min_height:
                    logger.info("[Quality] IMAGE TOO SMALL: width=%d < %d or height=%d < %d", 
                              width, self.settings.quality_min_width, height, self.settings.quality_min_height)
                    return PreparedImage(
                        quality_check=QualityCheck(
                            valid=False,
                            status='image_non_exploitable',
                            width=width,
                            height=height,
                            issues=['image_too_small'],
                        )
                    )

                metrics = self._measure(image)
                logger.info("[Quality] BLUR SCORE (sharpness): %.2f", metrics.sharpness)
                logger.info("[Quality] BRIGHTNESS SCORE: %.2f", metrics.brightness)
                logger.info("[Quality] CONTRAST SCORE: %.2f", metrics.contrast)

        except (UnidentifiedImageError, OSError, ValueError):
            logger.info("[Quality] INVALID IMAGE")
            return PreparedImage(
                quality_check=QualityCheck(valid=False, status='image_non_exploitable', issues=['invalid_image'])
            )

        issues: list[str] = []
        if metrics.brightness < 30.0:
            issues.append('too_dark')
            logger.info("[Quality] TOO DARK: brightness=%.2f < min=30.0", metrics.brightness)
        if metrics.brightness > 220.0:
            issues.append('too_bright')
            logger.info("[Quality] TOO BRIGHT: brightness=%.2f > max=220.0", metrics.brightness)
        if metrics.contrast < self.settings.quality_contrast_min:
            issues.append('low_contrast')
            logger.info("[Quality] LOW CONTRAST: contrast=%.2f < min=%.2f", 
                      metrics.contrast, self.settings.quality_contrast_min)
        if metrics.sharpness < 20.0:
            issues.append('blurry')
            logger.info("[Quality] BLURRY: sharpness=%.2f < min=20.0", metrics.sharpness)

        # Soil presence and bad framing are diagnostics only.
        soil_present = self._detect_soil_presence(image)
        logger.info("[Quality] SOIL PRESENCE: %.2f%% (threshold: 20%%)", soil_present * 100)
        bad_framing = self._detect_bad_framing(image)
        logger.info("[Quality] BAD FRAMING: %.2f%% (threshold: 40%%)", bad_framing * 100)

        valid = not issues
        logger.info("[Quality] VALIDITY CHECK: valid=%s, issues=%s", valid, issues)
        quality_check = QualityCheck(
            valid=valid,
            status='ok' if valid else 'image_non_exploitable',
            width=metrics.width,
            height=metrics.height,
            brightness=round(metrics.brightness, 2),
            contrast=round(metrics.contrast, 2),
            sharpness=round(metrics.sharpness, 2),
            issues=issues,
        )

        if not valid:
            return PreparedImage(quality_check=quality_check)

        image_224 = self._build_input_tensor(image, (224, 224))
        return PreparedImage(
            quality_check=quality_check,
            image_224=image_224,
        )

    def _build_input_tensor(self, image: Image.Image, size: tuple[int, int]) -> np.ndarray:
        resized = image.resize(size)
        img_array = np.array(resized).astype("float32") / 255.0
        logger.info("[Quality] IMAGE ARRAY MEAN: %.6f", float(np.mean(img_array)))
        logger.info("[Quality] IMAGE ARRAY STD: %.6f", float(np.std(img_array)))
        logger.info("[Quality] SHAPE BEFORE EXPAND: %s", img_array.shape)
        batch = np.expand_dims(img_array, axis=0)
        logger.info("[Quality] FINAL SHAPE: %s", batch.shape)
        return img_array

    def _detect_soil_presence(self, image: Image.Image) -> float:
        """
        Detect if image contains sufficient soil pixels.
        Returns the percentage of soil pixels (0.0 to 1.0).
        """
        # Convert to HSV
        hsv = image.convert('HSV')
        h, s, v = hsv.split()
        
        # Convert to numpy arrays
        h_arr = np.array(h, dtype=np.float32)
        s_arr = np.array(s, dtype=np.float32)
        v_arr = np.array(v, dtype=np.float32)
        
        # Normalize H to 0-360 scale (PIL H is 0-255)
        h_deg = h_arr * (360.0 / 255.0)
        
        # Soil color ranges in HSV (hue: 0-40° and 300-360° for browns/blacks, low saturation, medium value)
        # We'll accept a broader range to capture various soil types
        soil_mask = (
            ((h_deg >= 0) & (h_deg <= 40)) | 
            ((h_deg >= 300) & (h_deg <= 360))
        ) & (s_arr < 100) & (v_arr > 30) & (v_arr < 220)
        
        # Calculate percentage of soil pixels
        soil_percentage = float(np.mean(soil_mask))
        return soil_percentage

    def _detect_bad_framing(self, image: Image.Image) -> float:
        """
        Detect bad framing (e.g., too much sky at top).
        Returns the percentage of sky pixels in the top region (0.0 to 1.0).
        """
        # Convert to HSV
        hsv = image.convert('HSV')
        h, s, v = hsv.split()
        
        # Convert to numpy arrays
        h_arr = np.array(h, dtype=np.float32)
        v_arr = np.array(v, dtype=np.float32)
        
        # Normalize H to 0-360 scale
        h_deg = h_arr * (360.0 / 255.0)
        
        # Sky color ranges in HSV (hue: 100-140° for blues, high value/brightness)
        sky_mask = (h_deg >= 100) & (h_deg <= 140) & (v_arr > 200)
        
        # Focus on top 25% of image
        height = v_arr.shape[0]
        top_height = int(height * 0.25)
        if top_height == 0:
            return 0.0
            
        top_sky_mask = sky_mask[:top_height, :]
        
        # Calculate percentage of sky pixels in top region
        sky_percentage = float(np.mean(top_sky_mask))
        return sky_percentage

    def _measure(self, image: Image.Image) -> ImageQualityMetrics:
        grayscale = image.convert('L')
        stat = ImageStat.Stat(grayscale)
        brightness = float(stat.mean[0])
        contrast = float(stat.stddev[0])

        pixels = np.asarray(grayscale, dtype=np.float32)
        if pixels.shape[0] < 3 or pixels.shape[1] < 3:
            sharpness = 0.0
        else:
            laplacian = (
                -4 * pixels[1:-1, 1:-1]
                + pixels[:-2, 1:-1]
                + pixels[2:, 1:-1]
                + pixels[1:-1, :-2]
                + pixels[1:-1, 2:]
            )
            sharpness = float(np.var(laplacian)) ** 0.5

        width, height = image.size
        return ImageQualityMetrics(width=width, height=height, brightness=brightness, contrast=contrast, sharpness=sharpness)