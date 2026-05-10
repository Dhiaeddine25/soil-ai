export function SectionTitle({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="max-w-3xl">
      <div className="mb-3 inline-flex rounded-full border border-leaf-200 bg-leaf-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-leaf-700">
        {eyebrow}
      </div>
      <h2 className="text-3xl font-semibold tracking-tight text-soil-900 sm:text-4xl">{title}</h2>
      <p className="mt-4 text-base leading-7 text-soil-600">{description}</p>
    </div>
  );
}
