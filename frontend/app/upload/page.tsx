import { ProtectedRoute } from '@/components/auth/protected-route';
import { UploadLab } from '@/components/sections/upload-lab';

export default function UploadPage({ searchParams }: { searchParams?: { parcel?: string; parcel_id?: string } }) {
  const initialParcelId = searchParams?.parcel ?? searchParams?.parcel_id ?? undefined;

  return (
    <ProtectedRoute>
      <UploadLab initialParcelId={initialParcelId} />
    </ProtectedRoute>
  );
}