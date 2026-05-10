# DEMO_SCRIPT.md

## Objectif de la démo

Montrer une plateforme produit cohérente, fonctionnelle et crédible pour le pré-diagnostic NPK à partir d'images de sol. Démontrer que le système fonctionne, qu'il propose une aide à la décision responsable, et qu'il a du potentiel startup.

## Durée totale

5-7 minutes de démo guidée + 3-5 minutes de discussion/questions.

## Avant de commencer

- Backend et frontend sont lancés.
- Navigateurs: landing page (http://localhost:3000), prêt à naviguer.
- Données démo: 4 comptes, 3 parcelles, 6 analyses existantes.
- Son activé pour la fluidité narrative.

---

## Minute 0: Landing Page (30-45 secondes)

**Afficher**: `http://localhost:3000`

**À dire**:

- "Voici SoilAI, une plateforme de pré-diagnostic NPK pour les agriculteurs."
- "Le problème: les analyses de sol au labo sont fiables, mais lentes, coûteuses et peu fréquentes."
- "Notre réponse: une estimation rapide basée sur la vision par ordinateur, directement depuis une image de sol."
- "Important: ce n'est pas un remplacement du labo. C'est une aide à la décision et un suivi parcellaire."

**Points visuels**:

- Montrer le héros: promesse claire, palette verte et professionnelle.
- Montrer les stats: 9 parcelles, X analyses enregistrées, Y utilisateurs potentiels.
- Montrer les features: analyses rapides, exports, suivi, historique.

---

## Minute 1: Analytics Page (1-1.5 minutes)

**Naviguer vers**: `/analytics`

**À dire**:

- "Voici nos résultats réels d'entraînement. Nous avons testé plusieurs architectures."
- "Les meilleurs résultats viennent d'EfficientNetV2L, avec une F1 macro solide et une accuracy fiable."
- "DenseNet201 reste une excellente comparaison: très stable, très expliquable."
- "Ces seuils sont appliqués en direct pour chaque prédiction."

**Points visuels**:

- Montrer le modèle best: EfficientNetV2L, les courbes de performance.
- Montrer les détails de la matrice de confusion ou des courbes ROC si dispo.
- Mentionner les limitations: dataset fini, conditions d'éclairage variables.

---

## Minute 2.5: Dashboard (1 minute)

**Naviguer vers**: `/dashboard` (protégé, s'authentifier avec démo account si needed)

**À dire**:

- "Chaque utilisateur a son propre dashboard de suivi parcellaire."
- "On peut voir en un coup d'œil l'état des analyses récentes par parcelle."
- "Les données sont persistées et accessibles 24h/24 pour aider à la décision."

**Points visuels**:

- Montrer les cartes synthétiques: nombre d'analyses, dates, confiances.
- Montrer la réactivité UI (pas de lags).

---

## Minute 3.5: Upload et Analyse (1.5-2 minutes)

**Naviguer vers**: `/upload`

**À dire**:

- "Maintenant, regardons comment on lance une analyse pratiquement."
- "On sélectionne une parcelle, on upload une image, et le système prédit K, N, P en moins d'une seconde."

**Actions**:

- Remplir le formulaire d'upload (sélectionner une parcelle, dummy image ou accepter le mock).
- Cliquer "Analyser" ou "Mock Predict".
- Attendre le résultat (< 2 secondes en mode mock).

**À dire après résultat**:

- "Le résultat: K0, N2, P1 avec 87% de confiance. Le système donne aussi une interprétation et une recommandation."
- "Si la confiance est basse, on recommande une confirmation labo."
- "Si la confiance est haute, le résultat est déjà une base d'action."

**Points visuels**:

- Montrer les nutriments NPK sous forme visuelle (badges colorés).
- Montrer la barre de confiance.
- Montrer l'interprétation et la recommandation lisibles, prudentes.

---

## Minute 5: Historique et Détail (1.5-2 minutes)

**Naviguer vers**: `/history`

**À dire**:

- "Toutes les analyses sont enregistrées et consultables par utilisateur."
- "On peut filtrer par parcelle, exporter en CSV ou PDF, et consulter un détail complet pour chaque analyse."

**Actions**:

- Montrer la liste d'historique: plusieurs analyses, dates, confiances, NPK.
- Cliquer sur une analyse pour voir le détail.

**À dire au détail**:

- "Voici le détail d'une analyse: image, date, parcelle, résultat NPK, confiance, interprétation, recommandation."
- "On peut relancer une analyse pour la même parcelle, exporter le rapport, ou revenir à l'historique."
- "En bas, une mini galerie de l'historique parcellaire nous permet de voir les tendances."

**Points visuels**:

- Montrer la carte premium: héro sombre, image visuelle, résultats en gros, badges colorés NPK.
- Montrer les actions clés (exports, relance, parcelle liée).
- Montrer la mini galerie: autres analyses de la même parcelle.

---

## Minute 6.5: Récapitulatif et Conclusion (30-45 secondes)

**À dire**:

- "En résumé: SoilAI centralise le suivi NPK, aide à la décision rapide, et reste humble face au labo."
- "Le produit est modulaire: on peut swapper les modèles, enrichir les données, ajouter des capteurs."
- "L'architecture est scalable: plus d'utilisateurs, plus de parcelles, plus d'analyses."
- "C'est une base solide pour une startup agritech orientée aide à la décision."

**Points clés à ne pas oublier**:

- Souligner l'humilité scientifique: pas de substitution au labo.
- Souligner la responsabilité: recommandations prudentes.
- Souligner le potentiel: produit, données, communauté agricole.

---

## Pièges à éviter

- ❌ Ne pas dire "le système remplace totalement le laboratoire".
- ❌ Ne pas promettre une précision absolue ou des résultats garantis.
- ❌ Ne pas ignorer les résultats à faible confiance.
- ❌ Ne pas sur-vendre l'IA comme solution magique.
- ❌ Ne pas oublier de montrer que le code/l'interface fonctionnent fluidement.

## Points forts à souligner

- ✓ Interface propre et professionnelle (SaaS agritech).
- ✓ Backend robuste et testable (FastAPI, Pydantic, auth).
- ✓ Frontend fluide (Next.js, TypeScript, design système).
- ✓ Données réelles entraînées et seuils appliqués.
- ✓ Architecture modulaire et scalable.
- ✓ Prudence scientifique et recommandations responsables.

---

## Q&A attendues et réponses

### "Comment ça marche avec les images réelles?"

**R**: "En production, le modèle inférerait une vraie image uploadée. Là, nous sommes en mode mock pour la démo, mais l'API est prête à recevoir des images réelles et à lancer l'inférence complète."

### "Pourquoi EfficientNetV2L plutôt qu'autre chose?"

**R**: "C'est celui qui donne le meilleur F1 macro et la meilleure stabilité sur notre dataset. DenseNet201 est aussi bon mais un peu moins efficace. En prod, on pourrait en avoir plusieurs et les comparer."

### "Comment gérez-vous la faible confiance?"

**R**: "Quand la confiance est < 70%, nous recommandons une confirmation laboratoire. Au-dessus, c'est une base d'action directe mais toujours vérifiable."

### "Scalabilité?"

**R**: "Backend: FastAPI scale horizontalement, DB SQLite peut passer à PostgreSQL. Frontend: Next.js avec CDN et cache. Inférence: on peut utiliser un worker queue (Celery) ou un service d'inférence (TorchServe, TensorFlow Serving)."

### "Données?"

**R**: "On utilise 9 parcelles et ~300 images entraînées de vraies photos terrain. Les paires parcelle-image-résultat sont persistées pour le suivi."

---

## Comptes démo

- **Compte simple**: `alice` / `alice123` → Voir l'historique "alice" avec 1 analyse.
- **Compte jury**: `jury` / `jury123` → Voir l'historique "jury" avec 2 analyses.
- **Créer un compte perso**: Cliquer "Créer un compte" sur la page de login.

## Comptes de test avancé (optionnel)

Si vous voulez faire des analyses fresh pendant la démo:

1. S'enregistrer avec un nouveau compte.
2. Créer une parcelle.
3. Uploader une image et lancer "Predict Mock".
4. Voir le résultat et l'export CSV/PDF en direct.
