import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export function ContactForm() {
  return (
    <section className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <Card>
          <div className="text-sm uppercase tracking-[0.2em] text-soil-500">Partenariat</div>
          <h2 className="mt-3 text-3xl font-semibold text-soil-900">Discuter d’une démo, d’un pilote ou d’un partenariat</h2>
          <p className="mt-3 text-sm leading-6 text-soil-600">
            Le formulaire ci-dessous est déjà prêt pour une intégration backend ultérieure. Il permet de présenter la solution aux incubateurs,
            coopératives, jurys et partenaires techniques.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {['Nom', 'Email', 'Organisation', 'Type de collaboration'].map((field) => (
              <label key={field} className="space-y-2 text-sm font-medium text-soil-700">
                <span>{field}</span>
                <input className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder={field} />
              </label>
            ))}
            <label className="space-y-2 text-sm font-medium text-soil-700 md:col-span-2">
              <span>Message</span>
              <textarea className="min-h-[150px] w-full rounded-3xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Décrivez votre besoin, votre contexte ou votre intérêt pour un pilote." />
            </label>
          </div>

          <div className="mt-6 flex justify-end">
            <Button>Envoyer la demande</Button>
          </div>
        </Card>
      </div>
    </section>
  );
}
