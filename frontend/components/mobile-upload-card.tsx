'use client';

import { useEffect, useState, useRef } from 'react';
import { CameraCapture } from '@/components/camera-capture';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';

interface MobileUploadCardProps {
  onAnalyze: (imageBlob: Blob) => void;
  onError: (error: string) => void;
}

export function MobileUploadCard({ onAnalyze, onError }: MobileUploadCardProps) {
  const { messages } = useI18n();
  const [imageBlob, setImageBlob] = useState<Blob | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const cameraRef = useRef<HTMLDivElement>(null);

  const handleImageReady = (blob: Blob) => {
    setImageBlob(blob);
    setIsCameraOpen(false);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageBlob(file);
    }
  };

  const handleAnalyzeClick = () => {
    if (!imageBlob) {
      onError('Veuillez sélectionner ou capturer une image.');
      return;
    }
    onAnalyze(imageBlob);
  };

  const reset = () => {
    setImageBlob(null);
    if (cameraRef.current) {
      // Reset camera if open
      setIsCameraOpen(false);
    }
  };

  return (
    <Card className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-soil-900">{messages.analysis.upload}</h3>
        <p className="mt-1 text-sm text-soil-600">{messages.analysis.chooseParcel}</p>
      </div>

      {/* Image Preview */}
      {imageBlob ? (
        <div className="relative aspect-[4/3] w-full rounded-xl overflow-hidden bg-stone-50">
          <img
            src={URL.createObjectURL(imageBlob)}
            alt="Image sélectionnée"
            className="object-cover w-full h-full"
          />
          <button
            onClick={reset}
            className="absolute top-2 right-2 rounded-full bg-white/70 backdrop-blur-sm hover:bg-white/80 transition-colors p-1"
            aria-label="Supprimer l'image"
          >
            <svg className="h-4 w-4 text-soil-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ) : (
        <div className="aspect-[4/3] w-full rounded-xl bg-stone-50 flex items-center justify-center">
           <svg className="h-8 w-8 text-soil-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16v-2a2 2 0 012-2h2a2 2 0 012 2v2m-4 0h.01M17 16v-2a2 2 0 00-2-2h-2a2 2 0 00-2 2v2m4 0h.01M12 12a3 3 0 110-6 3 3 0 010 6zm0 0v2.25a.75.75 0 01-1.5 0V12a.75.75 0 011.5 0zm4.5 0a.75.75 0 100-1.5.75.75 0 000 1.5z" />
           </svg>
           <p className="mt-2 text-sm text-soil-500">{messages.analysis.noImageSelected}</p>
        </div>
      )}

      {/* Controls */}
      <div className="space-y-3">
        {/* Camera Button */}
          <Button onClick={() => setIsCameraOpen(true)} variant="outline" className="w-full">
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664.89l.812 1.22a2 2 0 011.206 1.206l1.22.812a2 2 0 00.89 1.664h1.342a2 2 0 012 2v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-1zm4 0a2 2 0 012-2h.93a2 2 0 001.664.89l.812 1.22a2 2 0 011.206 1.206l1.22.812a2 2 0 00.89 1.664h1.342a2 2 0 012 2v1a1 1 0 01-1 1h-.47a1 1 0 00-1.447-.37l-.372-.558a1 1 0 01-.37-1.447V9z" />
            </svg>
            {messages.analysis.takePhoto}
          </Button>

        {/* File Input */}
        <label className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-soil-200 bg-stone-50 p-6 text-center cursor-pointer hover:border-leaf-400 hover:bg-leaf-50">
          <svg className="h-6 w-6 text-leaf-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16v-2a2 2 0 012-2h2a2 2 0 012 2v2m-4 0h.01M17 16v-2a2 2 0 00-2-2h-2a2 2 0 00-2 2v2m4 0h.01M12 12a3 3 0 110-6 3 3 0 010 6zm0 0v2.25a.75.75 0 01-1.5 0V12a.75.75 0 011.5 0zm4.5 0a.75.75 0 100-1.5.75.75 0 000 1.5z" />
          </svg>
          <span className="mt-2 text-sm font-medium text-soil-700">{messages.analysis.selectImage}</span>
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
        </label>

        {/* Analyze Button */}
          <Button onClick={handleAnalyzeClick} disabled={!imageBlob} className="w-full bg-leaf-600 text-white hover:bg-leaf-700">
            {imageBlob ? messages.analysis.launch : messages.analysis.chooseParcel}
          </Button>
      </div>

      {/* Camera Modal */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="relative w-full max-w-lg">
            <div className="bg-white rounded-xl shadow-xl p-4">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-soil-900">{messages.analysis.cameraTitle}</h3>
                <button onClick={() => setIsCameraOpen(false)} className="text-soil-500 hover:text-soil-700">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div ref={cameraRef} className="mb-3">
                <CameraCapture
                  onCapture={handleImageReady}
                  onError={onError}
                />
              </div>
              <Button onClick={() => setIsCameraOpen(false)} variant="ghost" className="w-full">
                {messages.analysis.cancel}
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}