export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">SoilAI</h1>
      <p className="mt-4 text-lg">Analyse de sol par intelligence artificielle</p>
    </main>
  );
}
          {messages.landing.steps.map((step, index) => (
            <div key={step} className="rounded-3xl border border-soil-200 bg-white p-5 shadow-sm">
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-soil-400">0{index + 1}</div>
              <div className="mt-3 text-lg font-semibold text-soil-900">{step}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}