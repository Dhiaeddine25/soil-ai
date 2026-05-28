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
    features?: { title: string; description: string }[];
    pricing?: {
      title: string;
      description: string;
      featureList: string[];
      buyText: string;
      creditsLabel?: string;
    };
    trialButton?: string;
    paymentConfirm?: string;
    modalCancel?: string;
    paymentTitle?: string;
    cardNamePlaceholder?: string;
    cardExpiryPlaceholder?: string;
    cardNumberPlaceholder?: string;
    cardCvcPlaceholder?: string;
    paymentNote?: string;
    trialModalText?: string;
    emailPlaceholder?: string;
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
    takePhoto?: string;
    selectImage?: string;
    noImageSelected?: string;
    cameraTitle?: string;
    cancel?: string;
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
      features: [
        { title: 'Accès sécurisé', description: 'Compte protégé et session privée pour chaque utilisateur.' },
        { title: 'Analyse rapide', description: 'Importez une image et lancez l’analyse en quelques secondes.' },
        { title: 'Résultats lisibles', description: 'Historique, conseils et score terrain centralisés.' },
      ],
      eyebrow: 'Outil privé',
      title: 'Analysez une parcelle sans vous perdre dans l’interface',
      subtitle: 'Choisissez une parcelle, ajoutez une image, lisez le résultat NPK et retrouvez votre historique en quelques secondes.',
      primary: 'Commencer',
      secondary: 'Voir l’espace privé',
      note: 'Conçu pour un usage simple sur mobile, tablette et ordinateur.',
      stepsTitle: 'Parcours rapide',
      steps: ['Choisir une parcelle', 'Lancer une analyse', 'Lire et exporter le résultat'],
      pricing: {
        title: 'Tarifs en DZD',
        description: 'Choisissez le pack qui correspond à votre usage. Les crédits sont ajoutés immédiatement après paiement simulé.',
        featureList: ['Accès immédiat aux crédits', 'Idéal pour tester ou travailler en lot', "Historique et recommandations conservés"],
        buyText: 'Acheter',
        creditsLabel: 'crédits',
      },
      trialButton: 'Recevoir 1 crédit',
      paymentConfirm: 'Confirmer',
      modalCancel: 'Annuler',
      paymentTitle: 'Paiement sécurisé',
      cardNamePlaceholder: 'Nom sur la carte',
      cardExpiryPlaceholder: 'MM/AA',
      cardNumberPlaceholder: 'Numéro de carte',
      cardCvcPlaceholder: 'CVC',
      paymentNote: 'Paiement simulé pour la démonstration.',
    },
    auth: {
      backHome: 'Retour à l’accueil',
      loginTitle: 'Se connecter',
      registerTitle: 'Créer un compte',
      loginSubtitle: 'Accès simple à l’espace privé, aux parcelles et aux analyses.',
      registerSubtitle: 'Créer un compte pour gérer ses parcelles et ses résultats.',
      emailLabel: 'Email',
      emailPlaceholder: 'you@example.com',
      passwordLabel: 'Mot de passe',
      passwordPlaceholder: '********',
      fullNameLabel: 'Nom complet',
      fullNamePlaceholder: 'Nom et prénom',
      loginButton: 'Se connecter',
      registerButton: 'Créer le compte',
      noAccountPrompt: "Pas encore de compte ?",
      alreadyRegisteredPrompt: 'Déjà inscrit ?',
      loginError: 'Connexion impossible. Vérifie ton email et ton mot de passe.',
      registerError: 'Inscription impossible. Vérifie les informations et la longueur du mot de passe.',
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
      takePhoto: 'Prendre une photo',
      selectImage: 'Sélectionner une image',
      noImageSelected: 'Aucune image sélectionnée',
      cameraTitle: 'Caméra',
      cancel: 'Annuler',
      accessError: 'Impossible d\'accéder à la caméra. Veuillez vérifier les permissions.',
      cameraNotReady: 'La caméra n\'est pas prête.',
      internalCanvasError: 'Erreur interne : canvas non disponible.',
      captureError: 'Impossible de capturer l\'image.',
      captureUnavailable: "La capture d'image n'est pas disponible sur cet appareil.",
      captureAriaLabel: 'Capturer une image',
      stopAriaLabel: 'Arrêter la caméra',
      startCameraLabel: 'Démarrer la caméra',
      restartError: 'Impossible de redémarrer la caméra.',
    },
    history: {
      title: 'Historique',
      subtitle: 'Une liste simple, filtrable et exportable.',
      filter: 'Filtrer par parcelle',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'Aucune analyse enregistrée.',
      openDetail: 'Voir le détail',
      refusalTips: ['Reprendre une photo nette, sans ombre forte.', 'Cadrer le sol de pres, sans vegetation.', 'Eviter le flou en tenant le telephone stable.'],
      statusStable: 'Sol stable',
      statusWatch: 'A surveiller',
      statusPriority: 'Prioritaire',
      imageNotProvided: 'Image non renseignee',
      adviceFallback: 'Conseil indicatif.',
      adviceDisclaimerFallback: 'Analyse indicative basee sur une image.',
      exportError: "Impossible d'exporter cet historique pour le moment.",
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
      features: [
        { title: 'Secure access', description: 'Protected account and private session for every user.' },
        { title: 'Fast analysis', description: 'Upload an image and run the analysis in seconds.' },
        { title: 'Readable results', description: 'History, advice and field scores in one place.' },
      ],
      eyebrow: 'Private tool',
      title: 'Analyze a plot without a cluttered interface',
      subtitle: 'Pick a parcel, upload an image, read the NPK result, and find the history in seconds.',
      primary: 'Get started',
      secondary: 'Open private space',
      note: 'Built for fast use on mobile, tablet, and desktop.',
      stepsTitle: 'Quick flow',
      steps: ['Pick a parcel', 'Run an analysis', 'Read and export the result'],
      pricing: {
        title: 'Pricing (DZD)',
        description: 'Choose the pack that fits your usage. Credits are added immediately after simulated payment.',
        featureList: ['Immediate credits', 'Good for testing or batch work', 'History and recommendations saved'],
        buyText: 'Buy',
        creditsLabel: 'credits',
      },
      trialButton: 'Get 1 credit',
      paymentConfirm: 'Confirm',
      modalCancel: 'Cancel',
      paymentTitle: 'Secure payment',
      cardNamePlaceholder: 'Name on card',
      cardExpiryPlaceholder: 'MM/YY',
      cardNumberPlaceholder: 'Card number',
      cardCvcPlaceholder: 'CVC',
      paymentNote: 'Payment simulated for demo purposes.',
    },
    auth: {
      backHome: 'Back home',
      loginTitle: 'Sign in',
      registerTitle: 'Create account',
      loginSubtitle: 'Simple access to the private workspace, parcels, and analyses.',
      registerSubtitle: 'Create an account to manage parcels and results.',
      emailLabel: 'Email',
      emailPlaceholder: 'you@example.com',
      passwordLabel: 'Password',
      passwordPlaceholder: '********',
      fullNameLabel: 'Full name',
      fullNamePlaceholder: 'First and last name',
      loginButton: 'Sign in',
      registerButton: 'Create account',
      noAccountPrompt: "No account yet?",
      alreadyRegisteredPrompt: 'Already registered?',
      loginError: 'Sign in failed. Check your email and password.',
      registerError: 'Registration failed. Check your details and password length.',
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
      takePhoto: 'Take a photo',
      selectImage: 'Select an image',
      noImageSelected: 'No image selected',
      cameraTitle: 'Camera',
      cancel: 'Cancel',
      accessError: 'Unable to access the camera. Please check permissions.',
      cameraNotReady: 'Camera is not ready.',
      internalCanvasError: 'Internal error: canvas not available.',
      captureError: 'Unable to capture image.',
      captureUnavailable: "Image capture is not available on this device.",
      captureAriaLabel: 'Capture image',
      stopAriaLabel: 'Stop camera',
      startCameraLabel: 'Start camera',
      restartError: 'Unable to restart the camera.',
    },
    history: {
      title: 'History',
      subtitle: 'A simple, filterable and exportable list.',
      filter: 'Filter by parcel',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'No saved analysis yet.',
      openDetail: 'Open detail',
      refusalTips: ['Retake a sharp photo without strong shadows.', 'Frame the soil closely, without vegetation.', 'Avoid blur by holding the phone steady.'],
      statusStable: 'Stable soil',
      statusWatch: 'Monitor',
      statusPriority: 'Priority',
      imageNotProvided: 'Image not provided',
      adviceFallback: 'Indicative advice.',
      adviceDisclaimerFallback: 'Indicative analysis based on an image.',
      exportError: "Unable to export this history right now.",
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
      features: [
        { title: 'وصول آمن', description: 'حساب محمي وجلسة خاصة لكل مستخدم.' },
        { title: 'تحليل سريع', description: 'ارفع صورة وابدأ التحليل خلال ثوانٍ.' },
        { title: 'نتائج قابلة للقراءة', description: 'السجل والتوصيات ونتيجة الحقل في مكان واحد.' },
      ],
      eyebrow: 'أداة خاصة',
      title: 'حلّل القطعة الزراعية بدون واجهة معقدة',
      subtitle: 'اختر قطعة، ارفع صورة، اقرأ نتيجة NPK، واعثر على السجل خلال ثوانٍ.',
      primary: 'ابدأ الآن',
      secondary: 'فتح المساحة الخاصة',
      note: 'مصمم للاستخدام السريع على الهاتف واللوحي والحاسوب.',
      stepsTitle: 'الخطوات السريعة',
      steps: ['اختر قطعة', 'ابدأ التحليل', 'اقرأ النتيجة وصدّرها'],
      pricing: {
        title: 'الأسعار (DZD)',
        description: 'اختر الباقة المناسبة. سيُضاف الرصيد فورياً بعد الدفع المحاكى.',
        featureList: ['رصيد فوري', 'مناسب للاختبار أو العمل بكميات', 'السجل والتوصيات محفوظة'],
        buyText: 'شراء',
        creditsLabel: 'اعتمادات',
        trialModalText: 'Entrez votre email pour recevoir un crédit gratuit.',
        emailPlaceholder: 'Email',
      },
      trialButton: 'الحصول على رصيد',
      paymentConfirm: 'تأكيد',
      modalCancel: 'إلغاء',
      paymentTitle: 'دفع آمن',
      cardNamePlaceholder: 'الاسم على البطاقة',
      cardExpiryPlaceholder: 'MM/AA',
      cardNumberPlaceholder: 'رقم البطاقة',
      cardCvcPlaceholder: 'CVC',
      paymentNote: 'دفع محاكى للعرض.',
    },
    auth: {
      backHome: 'العودة للرئيسية',
      loginTitle: 'تسجيل الدخول',
      registerTitle: 'إنشاء حساب',
      loginSubtitle: 'وصول بسيط إلى المساحة الخاصة والقطع والتحليلات.',
      registerSubtitle: 'أنشئ حسابًا لإدارة القطع والنتائج.',
      emailLabel: 'البريد الإلكتروني',
      emailPlaceholder: 'you@example.com',
      passwordLabel: 'كلمة المرور',
      passwordPlaceholder: '********',
      fullNameLabel: 'الاسم الكامل',
      fullNamePlaceholder: 'الاسم واللقب',
      loginButton: 'تسجيل الدخول',
      registerButton: 'إنشاء الحساب',
      noAccountPrompt: 'لا تملك حساباً؟',
      alreadyRegisteredPrompt: 'هل لديك حساب؟',
      loginError: 'فشل تسجيل الدخول. تحقق من البريد وكلمة المرور.',
      registerError: 'فشل التسجيل. تحقق من المعلومات وطول كلمة المرور.',
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
      takePhoto: 'التقاط صورة',
      selectImage: 'اختر صورة',
      noImageSelected: 'لم يتم اختيار صورة',
      cameraTitle: 'الكاميرا',
      cancel: 'إلغاء',
      accessError: 'تعذر الوصول إلى الكاميرا. تحقق من الأذونات.',
      cameraNotReady: 'الكاميرا غير جاهزة.',
      internalCanvasError: 'خطأ داخلي: اللوحة (canvas) غير متوفرة.',
      captureError: 'تعذر التقاط الصورة.',
      captureUnavailable: 'التقاط الصور غير متاح على هذا الجهاز.',
      captureAriaLabel: 'التقاط صورة',
      stopAriaLabel: 'إيقاف الكاميرا',
      startCameraLabel: 'تشغيل الكاميرا',
      restartError: 'تعذر إعادة تشغيل الكاميرا.',
    },
    history: {
      title: 'السجل',
      subtitle: 'قائمة بسيطة مع فلترة وتصدير.',
      filter: 'تصفية حسب القطعة',
      exportCsv: 'CSV',
      exportPdf: 'PDF',
      empty: 'لا توجد تحليلات محفوظة.',
      openDetail: 'فتح التفاصيل',
      refusalTips: ['التقاط صورة واضحة بدون ظلال قوية.', 'إطار التربة عن قرب، بدون نباتات.', 'تجنب الضبابية عن طريق تثبيت الهاتف.'],
      statusStable: 'تربة مستقرة',
      statusWatch: 'مراقبة',
      statusPriority: 'أولوية',
      imageNotProvided: 'لم يتم توفير صورة',
      adviceFallback: 'توصية إرشادية.',
      adviceDisclaimerFallback: 'تحليل تقريبي مبني على صورة.',
      exportError: 'تعذر تصدير السجل حالياً.',
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
