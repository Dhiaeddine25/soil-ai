import { ContactForm } from '@/components/sections/contact-form';
import { SectionTitle } from '@/components/sections/section-title';

export default function ContactPage() {
  return (
    <div className="space-y-8">
      <div className="px-4 pt-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <SectionTitle
            eyebrow="Contact"
            title="Partenariat, pilote, mémoire ou incubation"
            description="Ce formulaire est préparé pour recevoir des demandes d’universités, d’incubateurs, de coopératives ou de partenaires techniques."
          />
        </div>
      </div>
      <ContactForm />
    </div>
  );
}
