export type Locale = 'fr' | 'en' | 'ar';
export type Direction = 'ltr' | 'rtl';

export const supportedLocales: Locale[] = ['fr', 'en', 'ar'];
export const defaultLocale: Locale = 'fr';
export const localeStorageKey = 'soilai_locale';

const localeDirections: Record<Locale, Direction> = {
  fr: 'ltr',
  en: 'ltr',
  ar: 'rtl',
};

export function getDirection(locale: Locale): Direction {
  return localeDirections[locale] ?? 'ltr';
}

export function normalizeLocale(value?: string | null): Locale {
  const normalized = value?.toLowerCase().split('-')[0];
  if (normalized === 'en' || normalized === 'ar' || normalized === 'fr') {
    return normalized;
  }
  return defaultLocale;
}

export type TranslationTable = {
  shell: {
    appName: string;
    appTagline: string;
    login: string;
    openApp: string;
    newAnalysis: string;
    dashboard: string;
    parcels: string;
    analysis: string;
    history: string;
    reports: string;
    account: string;
    language: string;
    languageFrench: string;
    languageEnglish: string;
    languageArabic: string;
    logout: string;
  };
  landing: {
    eyebrow: string;
    title: string;
    subtitle: string;
    primary: string;
    secondary: string;
    note: string;
    stepsTitle: string;
    steps: [string, string, string];
  };
  auth: {
    backHome: string;
    loginTitle: string;
    registerTitle: string;
    loginSubtitle: string;
    registerSubtitle: string;
  };
  dashboard: {
    title: string;
    subtitle: string;
    quickActions: string;
    recentAnalyses: string;
    openAnalysis: string;
    goToHistory: string;
    goToParcels: string;
    nextStep: string;
  };
  analysis: {
    title: string;
    subtitle: string;
    chooseParcel: string;
    upload: string;
    launch: string;
    clear: string;
    result: string;
    recommendation: string;
    noParcel: string;
    goToParcels: string;
  };
  history: {
    title: string;
    subtitle: string;
    filter: string;
    exportCsv: string;
    exportPdf: string;
    empty: string;
    openDetail: string;
  };
  parcels: {
    title: string;
    subtitle: string;
    add: string;
    edit: string;
    delete: string;
    history: string;
  };
  profile: {
    title: string;
    subtitle: string;
    newAnalysis: string;
    logout: string;
  };
};

const messages: Record<Locale, TranslationTable> = {
  fr: {
    shell: {
      appName: 'SoilAI',
      appTagline: 'Outil privé de diagnostic sol',
      login: 'Connexion',
      openApp: 'Ouvrir l’espace',
      newAnalysis: 'Nouvelle analyse',
      dashboard: 'Tableau de bord',
      parcels: 'Parcelles',
      analysis: 'Analyse',
      history: 'Historique',
      reports: 'Rapports',
      account: 'Compte',
      language: 'Langue',
      languageFrench: 'Français',
      languageEnglish: 'English',
      languageArabic: 'العربية',
      logout: 'Déconnexion',
    },
    landing: {
      eyebrow: 'Outil privé',
      title: 'Analysez une parcelle sans vous perdre dans l’interface',
      subtitle: 'Choisissez une parcelle, ajoutez une image, lisez le résultat NPK et retrouvez votre historique en quelques secondes.',
      primary: 'Commencer',
      secondary: 'Voir l’espace privé',
      note: 'Conçu pour un usage simple sur mobile, tablette et ordinateur.',
      stepsTitle: 'Parcours rapide',
      steps: ['Choisir une parcelle', 'Lancer une analyse', 'Lire et exporter le résultat'],
    },
    auth: {
      backHome: 'Retour à l’accueil',
      loginTitle: 'Se connecter',
      registerTitle: 'Créer un compte',
      loginSubtitle: 'Accès simple à l’espace privé, aux parcelles et aux analyses.',
      registerSubtitle: 'Créer un compte pour gérer ses parcelles et ses résultats.',
    },
    dashboard: {
      title: 'Tableau de bord',
      subtitle: 'Les actions utiles seulement.',
      quickActions: 'Actions rapides',
      recentAnalyses: 'Analyses récentes',
      openAnalysis: 'Lancer une analyse',
      goToHistory: 'Ouvrir l’historique',
      goToParcels: 'Gérer les parcelles',
      nextStep: 'Prochaine étape',
    },
    analysis: {
      title: 'Analyse',
      subtitle: 'Parcelle, image, résultat.',
      chooseParcel: 'Parcelle',
      upload: 'Image du sol',
      launch: 'Lancer',
      clear: 'Effacer',
      result: 'Résultat',
      recommendation: 'Conseil',
      noParcel: 'Créer une parcelle pour commencer.',
      goToParcels: 'Aller aux parcelles',
    },
    history: {
      title: 'Historique',
      subtitle: 'Une liste simple, filtrable et exportable.',
      filter: 'Filtrer par parcelle',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'Aucune analyse enregistrée.',
      openDetail: 'Voir le détail',
    },
    parcels: {
      title: 'Parcelles',
      subtitle: 'Créer, modifier, supprimer, consulter l’historique lié.',
      add: 'Ajouter',
      edit: 'Modifier',
      delete: 'Supprimer',
      history: 'Historique lié',
    },
    profile: {
      title: 'Compte',
      subtitle: 'Réglages simples et accès à l’espace privé.',
      newAnalysis: 'Nouvelle analyse',
      logout: 'Déconnexion',
    },
  },
  en: {
    shell: {
      appName: 'SoilAI',
      appTagline: 'Private soil diagnostic tool',
      login: 'Sign in',
      openApp: 'Open workspace',
      newAnalysis: 'New analysis',
      dashboard: 'Dashboard',
      parcels: 'Parcels',
      analysis: 'Analysis',
      history: 'History',
      reports: 'Reports',
      account: 'Account',
      language: 'Language',
      languageFrench: 'Français',
      languageEnglish: 'English',
      languageArabic: 'العربية',
      logout: 'Sign out',
    },
    landing: {
      eyebrow: 'Private tool',
      title: 'Analyze a plot without a cluttered interface',
      subtitle: 'Pick a parcel, upload an image, read the NPK result, and find the history in seconds.',
      primary: 'Get started',
      secondary: 'Open private space',
      note: 'Built for fast use on mobile, tablet, and desktop.',
      stepsTitle: 'Quick flow',
      steps: ['Pick a parcel', 'Run an analysis', 'Read and export the result'],
    },
    auth: {
      backHome: 'Back home',
      loginTitle: 'Sign in',
      registerTitle: 'Create account',
      loginSubtitle: 'Simple access to the private workspace, parcels, and analyses.',
      registerSubtitle: 'Create an account to manage parcels and results.',
    },
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Only useful actions.',
      quickActions: 'Quick actions',
      recentAnalyses: 'Recent analyses',
      openAnalysis: 'Run an analysis',
      goToHistory: 'Open history',
      goToParcels: 'Manage parcels',
      nextStep: 'Next step',
    },
    analysis: {
      title: 'Analysis',
      subtitle: 'Parcel, image, result.',
      chooseParcel: 'Parcel',
      upload: 'Soil image',
      launch: 'Run',
      clear: 'Clear',
      result: 'Result',
      recommendation: 'Advice',
      noParcel: 'Create a parcel to start.',
      goToParcels: 'Go to parcels',
    },
    history: {
      title: 'History',
      subtitle: 'A simple, filterable and exportable list.',
      filter: 'Filter by parcel',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'No saved analysis yet.',
      openDetail: 'Open detail',
    },
    parcels: {
      title: 'Parcels',
      subtitle: 'Create, edit, delete, and view related history.',
      add: 'Add',
      edit: 'Edit',
      delete: 'Delete',
      history: 'Linked history',
    },
    profile: {
      title: 'Account',
      subtitle: 'Simple settings and access to the private workspace.',
      newAnalysis: 'New analysis',
      logout: 'Sign out',
    },
  },
  ar: {
    shell: {
      appName: 'SoilAI',
      appTagline: 'أداة خاصة لتحليل التربة',
      login: 'تسجيل الدخول',
      openApp: 'فتح المساحة',
      newAnalysis: 'تحليل جديد',
      dashboard: 'لوحة التحكم',
      parcels: 'القطع',
      analysis: 'تحليل',
      history: 'السجل',
      reports: 'التقارير',
      account: 'الحساب',
      language: 'اللغة',
      languageFrench: 'Français',
      languageEnglish: 'English',
      languageArabic: 'العربية',
      logout: 'تسجيل الخروج',
    },
    landing: {
      eyebrow: 'أداة خاصة',
      title: 'حلّل القطعة الزراعية بدون واجهة معقدة',
      subtitle: 'اختر قطعة، ارفع صورة، اقرأ نتيجة NPK، واعثر على السجل خلال ثوانٍ.',
      primary: 'ابدأ الآن',
      secondary: 'فتح المساحة الخاصة',
      note: 'مصمم للاستخدام السريع على الهاتف واللوحي والحاسوب.',
      stepsTitle: 'الخطوات السريعة',
      steps: ['اختر قطعة', 'ابدأ التحليل', 'اقرأ النتيجة وصدّرها'],
    },
    auth: {
      backHome: 'العودة للرئيسية',
      loginTitle: 'تسجيل الدخول',
      registerTitle: 'إنشاء حساب',
      loginSubtitle: 'وصول بسيط إلى المساحة الخاصة والقطع والتحليلات.',
      registerSubtitle: 'أنشئ حسابًا لإدارة القطع والنتائج.',
    },
    dashboard: {
      title: 'لوحة التحكم',
      subtitle: 'الخطوات المفيدة فقط.',
      quickActions: 'إجراءات سريعة',
      recentAnalyses: 'آخر التحليلات',
      openAnalysis: 'ابدأ تحليلًا',
      goToHistory: 'فتح السجل',
      goToParcels: 'إدارة القطع',
      nextStep: 'الخطوة التالية',
    },
    analysis: {
      title: 'تحليل',
      subtitle: 'القطعة، الصورة، النتيجة.',
      chooseParcel: 'القطعة',
      upload: 'صورة التربة',
      launch: 'ابدأ',
      clear: 'مسح',
      result: 'النتيجة',
      recommendation: 'التوصية',
      noParcel: 'أنشئ قطعة للبدء.',
      goToParcels: 'اذهب إلى القطع',
    },
    history: {
      title: 'السجل',
      subtitle: 'قائمة بسيطة مع فلترة وتصدير.',
      filter: 'تصفية حسب القطعة',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'لا توجد تحليلات محفوظة.',
      openDetail: 'فتح التفاصيل',
    },
    parcels: {
      title: 'القطع',
      subtitle: 'إضافة، تعديل، حذف، والسجل المرتبط.',
      add: 'إضافة',
      edit: 'تعديل',
      delete: 'حذف',
      history: 'السجل المرتبط',
    },
    profile: {
      title: 'الحساب',
      subtitle: 'إعدادات بسيطة مع الوصول إلى المساحة الخاصة.',
      newAnalysis: 'تحليل جديد',
      logout: 'تسجيل الخروج',
    },
  },
};

export function getMessages(locale: Locale): TranslationTable {
  return messages[locale] ?? messages[defaultLocale];
}
