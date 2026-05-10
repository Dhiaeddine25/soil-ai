from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, ImageStat, UnidentifiedImageError

from app.core.config import Settings
from app.schemas.prediction_quality import QualityCheck


@dataclass(frozen=True)
class ImageQualityMetrics:
    width: int
    height: int
    brightness: float
    contrast: float
    sharpness: float


class ImageQualityService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, image_bytes: bytes | None) -> QualityCheck:
        if not image_bytes:
            return QualityCheck(valid=False, status='image_non_exploitable', issues=['empty_file'])

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.load()
                width, height = image.size
                if width < self.settings.quality_min_width or height < self.settings.quality_min_height:
                    return QualityCheck(
                        valid=False,
                        status='image_non_exploitable',
                        width=width,
                        height=height,
                        issues=['image_too_small'],
                    )

                metrics = self._measure(image)
        except (UnidentifiedImageError, OSError, ValueError):
            return QualityCheck(valid=False, status='image_non_exploitable', issues=['invalid_image'])

        issues: list[str] = []
        if metrics.brightness < self.settings.quality_brightness_min:
            issues.append('too_dark')
        if metrics.brightness > self.settings.quality_brightness_max:
            issues.append('too_bright')
        if metrics.contrast < self.settings.quality_contrast_min:
            issues.append('low_contrast')
        if metrics.sharpness < self.settings.quality_sharpness_min:
            issues.append('blurry')

        valid = not issues
        return QualityCheck(
            valid=valid,
            status='ok' if valid else 'image_non_exploitable',
            width=metrics.width,
            height=metrics.height,
            brightness=round(metrics.brightness, 2),
            contrast=round(metrics.contrast, 2),
            sharpness=round(metrics.sharpness, 2),
            issues=issues,
        )

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