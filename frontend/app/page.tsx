"use client";

import { useEffect, useMemo, useState, useRef } from "react";
import { useI18n } from "@/components/i18n/i18n-provider";

const CREDITS_KEY = "soilCredits";
const TRIAL_KEY = "freeTrialUsed";

export default function HomePage() {
  const [credits, setCredits] = useState(0);
  const [creditPulse, setCreditPulse] = useState(false);
  const [freeTrialUsed, setFreeTrialUsed] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [showStripeModal, setShowStripeModal] = useState(false);
  const [pendingCredits, setPendingCredits] = useState(0);
  const [pendingPrice, setPendingPrice] = useState(0);
  const [email, setEmail] = useState("");
  const [cardName, setCardName] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvc, setCardCvc] = useState("");

  useEffect(() => {
    const storedCredits = Number(window.localStorage.getItem(CREDITS_KEY) ?? "0");
    setCredits(Number.isFinite(storedCredits) ? storedCredits : 0);
    setFreeTrialUsed(window.localStorage.getItem(TRIAL_KEY) === "true");
  }, []);

    // i18n
    // `I18nProvider` is mounted at the root layout, use the hook here
    // to read localized messages so the language switch affects this page.
    // Import lazily to keep the file simple in dev environments.
    // eslint-disable-next-line @typescript-eslint/consistent-type-imports
    // (the import is static below)
  
    // Note: useI18n is a client hook exported from the provider.
    // We import it at the top of the file.

  useEffect(() => {
    window.localStorage.setItem(CREDITS_KEY, String(credits));
  }, [credits]);

  const initialMountRef = useRef(true);
  useEffect(() => {
    if (initialMountRef.current) {
      initialMountRef.current = false;
      return;
    }
    setCreditPulse(true);
    const t = setTimeout(() => setCreditPulse(false), 900);
    return () => clearTimeout(t);
  }, [credits]);

  useEffect(() => {
    window.localStorage.setItem(TRIAL_KEY, String(freeTrialUsed));
  }, [freeTrialUsed]);

  const plans = useMemo(
    () => [
      { name: "Petit jardinier", credits: 5, price: 800, color: "#f7faf5" },
      { name: "Technicien", credits: 10, price: 1400, color: "#eef6ea" },
      { name: "Expert", credits: 25, price: 3000, color: "#e4f0de" },
    ],
    [],
  );

  const { messages, locale, supportedLocales, setLocale } = useI18n();

  function cycleLocale() {
    const idx = supportedLocales.indexOf(locale);
    const next = supportedLocales[(idx + 1) % supportedLocales.length];
    setLocale(next);
  }

  function addCredits(amount: number) {
    setCredits((value) => value + amount);
  }

  function handleFreeTrial() {
    try {
      const target = document.getElementById('pricing');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // also set hash as a fallback for some browsers
        try { history.replaceState(null, '', '#pricing'); } catch (e) { location.hash = '#pricing'; }
        return;
      }
    } catch (e) {
      // ignore DOM errors and fallback to modal
    }
    if (freeTrialUsed) return;
    setShowEmailModal(true);
  }

  function confirmFreeTrial() {
    if (!email.trim()) return;
    setFreeTrialUsed(true);
    addCredits(1);
    setShowEmailModal(false);
    setEmail("");
  }

  function openStripeModal(creditsToAdd: number, price: number) {
    setPendingCredits(creditsToAdd);
    setPendingPrice(price);
    setShowStripeModal(true);
  }

  function confirmPayment() {
    addCredits(pendingCredits);
    setShowStripeModal(false);
    setPendingCredits(0);
    setPendingPrice(0);
    setCardName("");
    setCardNumber("");
    setCardExpiry("");
    setCardCvc("");
  }

  return (
    <>
      <style jsx global>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
          background: linear-gradient(180deg, #ffffff 0%, #f7fbf4 100%);
          color: #172317;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        .page {
          min-height: 100vh;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 18px 28px;
          border-bottom: 1px solid rgba(66, 99, 53, 0.14);
          background: rgba(255, 255, 255, 0.88);
          backdrop-filter: blur(10px);
          position: sticky;
          top: 0;
          z-index: 20;
          gap: 16px;
          flex-wrap: wrap;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 14px;
        }

        .logo {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          background: #111111;
          color: #fff;
          display: grid;
          place-items: center;
          font-weight: 700;
          letter-spacing: 0.02em;
        }

        .brand-text strong {
          display: block;
          font-size: 1rem;
          color: #111827;
        }

        .brand-text span {
          font-size: 0.86rem;
          color: #6b7280;
        }

        .private-badge {
          border: 1px solid rgba(66, 99, 53, 0.18);
          color: #446144;
          background: #f4f8ef;
          padding: 8px 14px;
          border-radius: 999px;
          font-size: 0.9rem;
          font-weight: 600;
          white-space: nowrap;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-left: auto;
          flex-wrap: wrap;
        }

        .lang-btn,
        .ghost-btn,
        .primary-btn,
        .signin-btn,
        .pricing-btn,
        .trial-btn,
        .modal-btn {
          border: none;
          border-radius: 999px;
          cursor: pointer;
          font-weight: 700;
          transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
        }

        .lang-btn {
          background: #fff;
          color: #111827;
          border: 1px solid rgba(17, 24, 39, 0.14);
          padding: 10px 16px;
          min-width: 90px;
        }

        .credit-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: #ecf5e5;
          color: #264b23;
          border: 1px solid rgba(51, 105, 47, 0.18);
          padding: 10px 16px;
          border-radius: 999px;
          font-weight: 700;
          white-space: nowrap;
        }

        .credit-pill.pulse {
          animation: credit-pulse 900ms ease;
        }

        @keyframes credit-pulse {
          0% { transform: translateY(0) scale(1); box-shadow: 0 0 0 rgba(38,75,35,0); }
          30% { transform: translateY(-3px) scale(1.06); box-shadow: 0 8px 20px rgba(38,75,35,0.12); }
          100% { transform: translateY(0) scale(1); box-shadow: 0 0 0 rgba(38,75,35,0); }
        }

        .signin-btn {
          background: #111111;
          color: #ffffff;
          padding: 12px 20px;
        }

        .hero {
          max-width: 1180px;
          margin: 0 auto;
          padding: 78px 24px 28px;
          display: grid;
          gap: 28px;
          text-align: center;
        }

        .hero h1 {
          font-size: clamp(2.2rem, 4vw, 4.4rem);
          line-height: 1.05;
          letter-spacing: -0.04em;
          color: #102010;
          max-width: 900px;
          margin: 0 auto;
        }

        .hero p {
          font-size: 1.05rem;
          line-height: 1.7;
          color: #5c6a5b;
          max-width: 760px;
          margin: 0 auto;
        }

        .hero-actions {
          display: flex;
          justify-content: center;
          gap: 14px;
          flex-wrap: wrap;
          margin-top: 10px;
        }

        .primary-btn,
        .trial-btn,
        .pricing-btn,
        .ghost-btn,
        .modal-btn {
          padding: 14px 22px;
        }

        .primary-btn,
        .trial-btn {
          background: #111111;
          color: white;
          box-shadow: 0 12px 28px rgba(17, 17, 17, 0.12);
        }

        .ghost-btn,
        .pricing-btn {
          background: #fff;
          color: #111111;
          border: 1px solid rgba(17, 17, 17, 0.14);
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 14px;
          margin-top: 12px;
        }

        .stat {
          background: rgba(255, 255, 255, 0.8);
          border: 1px solid rgba(74, 103, 65, 0.12);
          border-radius: 24px;
          padding: 18px;
          text-align: left;
        }

        .stat strong {
          display: block;
          font-size: 1.2rem;
          margin-bottom: 6px;
        }

        .stat span {
          color: #667567;
          line-height: 1.5;
          font-size: 0.95rem;
        }

        .section {
          max-width: 1180px;
          margin: 0 auto;
          padding: 48px 24px;
        }

        .section-title {
          display: grid;
          gap: 10px;
          margin-bottom: 24px;
          text-align: left;
        }

        .section-title h2 {
          font-size: clamp(1.7rem, 2.5vw, 2.6rem);
          letter-spacing: -0.03em;
        }

        .section-title p {
          max-width: 760px;
          color: #617160;
          line-height: 1.7;
        }

        .steps,
        .pricing-grid {
          display: grid;
          gap: 16px;
          grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .card {
          background: rgba(255, 255, 255, 0.95);
          border: 1px solid rgba(66, 99, 53, 0.12);
          border-radius: 26px;
          padding: 24px;
          box-shadow: 0 18px 40px rgba(9, 30, 7, 0.04);
        }

        .card h3 {
          font-size: 1.1rem;
          margin-bottom: 12px;
        }

        .card p,
        .card li {
          color: #5f6d5d;
          line-height: 1.65;
          font-size: 0.96rem;
        }

        .card ul {
          margin-top: 12px;
          padding-left: 18px;
        }

        .trust-badges {
          display: flex;
          gap: 12px;
          justify-content: center;
          flex-wrap: wrap;
          margin-top: 8px;
        }

        .trust-badge {
          background: #f4f8ef;
          border: 1px solid rgba(74, 103, 65, 0.12);
          color: #3b5838;
          border-radius: 999px;
          padding: 10px 14px;
          font-weight: 600;
          font-size: 0.92rem;
        }

        .price {
          font-size: 2rem;
          font-weight: 800;
          letter-spacing: -0.03em;
          margin-bottom: 8px;
        }

        .price small {
          font-size: 0.95rem;
          color: #6f7f6f;
          font-weight: 600;
        }

        .price-note {
          color: #617160;
          margin-bottom: 16px;
        }

        .pricing-btn {
          width: 100%;
          margin-top: 8px;
        }

        .footer {
          max-width: 1180px;
          margin: 0 auto;
          padding: 24px;
          color: #6d7c6c;
          display: flex;
          justify-content: space-between;
          gap: 16px;
          flex-wrap: wrap;
          border-top: 1px solid rgba(66, 99, 53, 0.12);
        }

        .modal-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(15, 23, 16, 0.5);
          display: grid;
          place-items: center;
          z-index: 50;
          padding: 24px;
        }

        .modal {
          width: min(100%, 520px);
          background: white;
          border-radius: 28px;
          padding: 28px;
          box-shadow: 0 30px 70px rgba(0, 0, 0, 0.25);
        }

        .modal h3 {
          font-size: 1.45rem;
          margin-bottom: 12px;
        }

        .modal p {
          color: #607060;
          line-height: 1.65;
          margin-bottom: 16px;
        }

        .field-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }

        .field,
        .input {
          width: 100%;
        }

        .input {
          border: 1px solid rgba(17, 17, 17, 0.14);
          border-radius: 16px;
          padding: 13px 14px;
          font: inherit;
          margin-bottom: 12px;
        }

        .modal-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          flex-wrap: wrap;
        }

        .secondary-text {
          color: #6c7a6b;
          font-size: 0.95rem;
          margin-top: 14px;
        }

        @media (max-width: 900px) {
          .stats-row,
          .steps,
          .pricing-grid {
            grid-template-columns: 1fr;
          }

          .header {
            justify-content: center;
          }

          .header-actions {
            margin-left: 0;
            justify-content: center;
          }

          .section-title,
          .footer {
            text-align: center;
            justify-content: center;
          }

          .field-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <div className="page">

        {/* kept original site shell login button; removed duplicate */}

        <main>
          <section className="hero">
            <div className="trust-badges">
              <span className="trust-badge">{messages.landing.eyebrow}</span>
              <span className="trust-badge">{messages.landing.note}</span>
              <span className="trust-badge">{messages.landing.steps[0]}</span>
            </div>

            <h1>{messages.landing.title}</h1>
            <p>{messages.landing.subtitle}</p>

            <div className="hero-actions">
              <button className="primary-btn" type="button" onClick={handleFreeTrial}>
                {messages.landing.primary}
              </button>
            </div>

            {/* hero credit removed to keep single header credit */}

            <div className="stats-row">
              {messages.landing.steps.slice(0, 3).map((step, i) => (
                <div className="stat" key={i}>
                  <strong>{`${i + 1}. ${step}`}</strong>
                  <span>{messages.landing.note}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="section" id="how-it-works">
            <div className="section-title">
              <h2>{messages.landing.stepsTitle}</h2>
              <p>{messages.landing.note}</p>
            </div>

            <div className="steps">
              {messages.landing.steps.map((s, i) => (
                <div className="card" key={i}>
                  <h3>{`${i + 1}. ${s}`}</h3>
                  <p>{s}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="section" id="pricing">
            <div className="section-title">
              <h2>{messages.landing.pricing?.title}</h2>
              <p>{messages.landing.pricing?.description}</p>
            </div>

            <div className="pricing-grid">
              {plans.map((plan) => (
                <div className="card" key={plan.name} style={{ background: plan.color }}>
                  <h3>{plan.name}</h3>
                  <div className="price">
                    {plan.price.toLocaleString("fr-FR")} DA <small>/ {plan.credits} analyses</small>
                  </div>
                  <div className="price-note">
                    Soit {Math.round(plan.price / plan.credits).toLocaleString("fr-FR")} DA l’analyse
                  </div>
                  <ul>
                    {messages.landing.pricing?.featureList.map((f, idx) => (
                      <li key={idx}>{f}</li>
                    ))}
                  </ul>
                  <button
                    className="pricing-btn"
                    type="button"
                    onClick={() => openStripeModal(plan.credits, plan.price)}
                  >
                    {messages.landing.pricing?.buyText} {plan.credits} {messages.landing.pricing?.creditsLabel}
                  </button>
                </div>
              ))}
            </div>
          </section>
        </main>

        <footer className="footer">
          <div>© 2026 {messages.shell.appName}</div>
          <div>{messages.shell.appTagline}</div>
        </footer>
      </div>

      {showEmailModal && (
        <div className="modal-backdrop" onClick={() => setShowEmailModal(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <h3>{messages.landing.primary}</h3>
            <p>{messages.landing.trialModalText}</p>
            <input className="input" type="email" placeholder={messages.landing.emailPlaceholder} value={email} onChange={(event) => setEmail(event.target.value)} />
            <div className="modal-actions">
              <button className="ghost-btn" type="button" onClick={() => setShowEmailModal(false)}>
                {messages.landing.modalCancel}
              </button>
              <button className="modal-btn primary-btn" type="button" onClick={confirmFreeTrial}>
                {messages.landing.trialButton}
              </button>
            </div>
          </div>
        </div>
      )}

      {showStripeModal && (
        <div className="modal-backdrop" onClick={() => setShowStripeModal(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <h3>{messages.landing.paymentTitle}</h3>
            <p>
              {pendingCredits} {messages.landing.pricing?.creditsLabel} pour {pendingPrice.toLocaleString("fr-FR")} DA.
            </p>
            <div className="field-grid">
              <input className="input" type="text" placeholder={messages.landing.cardNamePlaceholder} value={cardName} onChange={(event) => setCardName(event.target.value)} />
              <input className="input" type="text" placeholder={messages.landing.cardExpiryPlaceholder} value={cardExpiry} onChange={(event) => setCardExpiry(event.target.value)} />
            </div>
            <input className="input" type="text" placeholder={messages.landing.cardNumberPlaceholder} value={cardNumber} onChange={(event) => setCardNumber(event.target.value)} />
            <input className="input" type="text" placeholder={messages.landing.cardCvcPlaceholder} value={cardCvc} onChange={(event) => setCardCvc(event.target.value)} />
            <div className="modal-actions">
              <button className="ghost-btn" type="button" onClick={() => setShowStripeModal(false)}>
                {messages.landing.modalCancel}
              </button>
              <button className="modal-btn primary-btn" type="button" onClick={confirmPayment}>
                {messages.landing.paymentConfirm}
              </button>
            </div>
            <p className="secondary-text">{messages.landing.paymentNote}</p>
          </div>
        </div>
      )}
    </>
  );
}
