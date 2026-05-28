'use client';

import { useEffect, useRef, useState } from 'react';
import { useI18n } from '@/components/i18n/i18n-provider';

interface CameraCaptureProps {
  onCapture: (blob: Blob) => void;
  onError: (error: string) => void;
}

export function CameraCapture({ onCapture, onError }: CameraCaptureProps) {
  const { messages } = useI18n();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isStreamActive, setIsStreamActive] = useState(false);

    useEffect(() => {
    const startStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment', // Prefer rear camera
            width: { ideal: 640 },
            height: { ideal: 480 }
          }
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsStreamActive(true);
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
        onError(messages.analysis.accessError);
      }
    };

    if (typeof window !== 'undefined' && navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
      startStream();
    }

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, [onError]);

  const handleCapture = () => {
    if (!videoRef.current || !videoRef.current.srcObject || !isStreamActive) {
      onError(messages.analysis.cameraNotReady);
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) {
      onError(messages.analysis.internalCanvasError);
      return;
    }

    const context = canvas.getContext('2d');
    if (!context) {
      onError('Erreur interne : impossible de créer le contexte de dessin.');
      return;
    }

    // Set canvas dimensions to match video
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    // Draw video frame to canvas
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob((blob) => {
      if (blob) {
        onCapture(blob);
      } else {
        onError(messages.analysis.captureError);
      }
    }, 'image/jpeg', 0.9);
  };

  if (typeof window === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return (
      <div className="text-center py-8">
        <p className="text-sm text-amber-900 bg-amber-50 rounded-2xl p-4">{messages.analysis.captureUnavailable}</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full h-[300px] object-cover rounded-xl bg-stone-50"
      />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <div className="absolute bottom-4 left-1/2 -translate-x-2 flex space-x-3">
        <button
          onClick={handleCapture}
          className="w-12 h-12 rounded-full bg-leaf-600 text-white flex items-center justify-center hover:bg-leaf-700 transition-shadow shadow-lg"
          aria-label={messages.analysis.captureAriaLabel}
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
        <button
          onClick={() => {
            if (streamRef.current) {
              streamRef.current.getTracks().forEach(track => track.stop());
            }
            setIsStreamActive(false);
          }}
          className="w-10 h-10 rounded-full bg-amber-200 text-amber-800 flex items-center justify-center hover:bg-amber-300 transition-shadow shadow"
          aria-label={messages.analysis.stopAriaLabel}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      {!isStreamActive && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <button
            onClick={() => {
              setIsStreamActive(true);
              // Restart stream
              navigator.mediaDevices.getUserMedia({
                video: {
                  facingMode: 'environment',
                  width: { ideal: 640 },
                  height: { ideal: 480 }
                }
              }).then(stream => {
                streamRef.current = stream;
                if (videoRef.current) {
                  videoRef.current.srcObject = stream;
                }
              }).catch(err => {
                console.error('Error restarting camera:', err);
                onError(messages.analysis.restartError);
              });
            }}
            className="rounded-xl bg-white/90 backdrop-blur-sm px-6 py-3 text-leaf-800 font-medium hover:bg-white/80 transition-shadow shadow"
          >
            {messages.analysis.startCameraLabel}
          </button>
        </div>
      )}
    </div>
  );
}