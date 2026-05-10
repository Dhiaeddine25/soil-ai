# SoilAI / Webbeck

Platforme agritech de pre-diagnostic NPK a partir d'images de sol, construite a partir des artefacts reels du projet `npk_90percent`.

## Ce que contient le projet

- `backend/` : API FastAPI avec mode mock realiste et preparation du branchement modele reel.
- `frontend/` : application Next.js avec landing page, dashboard, analytics et page d'analyse par upload.
- `data/` : dataset d'origine et fichiers de classes.
- `npk_models_*` : resultats, seuils, predictions et historiques produits par l'entrainement.

## Positionnement produit

- outil de pre-estimation et de suivi,
- aide a la decision,
- pas un remplacement du laboratoire,
- base produit credible pour memoire, soutenance, demo et incubation.

## Installation rapide

Avant tout:

- Python 3.10+ et venv créé dans `backend/.venv`
- Node.js 18+
- Deux terminaux PowerShell ouverts

### Terminal 1: Backend (FastAPI)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Vous verrez:

```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Le backend est prêt. Vérifiez: http://localhost:8000/docs (Swagger UI interactive).

### Terminal 2: Frontend (Next.js)

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000'
npm install  # première fois seulement
npm run dev
```

Vous verrez:

```
> ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Le système est prêt.** Ouvrir `http://localhost:3000` dans le navigateur.

## Routes principales

| Route                   | Description                                |
| ----------------------- | ------------------------------------------ |
| `/`                     | Landing page - promesse et positionnement  |
| `/login`                | Authentification                           |
| `/signup`               | Création de compte                         |
| `/dashboard`            | Aperçu parcelles et analyses (protégé)     |
| `/parcels`              | Gestion parcellaire (protégé)              |
| `/upload`               | Lancer une analyse (protégé)               |
| `/history`              | Consulter historique (protégé)             |
| `/history/[analysisId]` | Détail analyse avec mini galerie (protégé) |
| `/analytics`            | Résultats modèles et métriques             |
| `/admin`                | Panel admin (dev seulement)                |

## API Backend

| Endpoint                                    | Méthode | Description                                    |
| ------------------------------------------- | ------- | ---------------------------------------------- |
| `/health`                                   | GET     | Health check                                   |
| `/auth/register`                            | POST    | Créer compte                                   |
| `/auth/login`                               | POST    | Se connecter, retourne JWT                     |
| `/auth/me`                                  | GET     | Profil utilisateur (auth required)             |
| `/parcels`                                  | GET     | Lister parcelles (auth required)               |
| `/parcels`                                  | POST    | Créer parcelle (auth required)                 |
| `/predict/mock`                             | POST    | Prédiction mock (démo)                         |
| `/predict`                                  | POST    | Prédiction réelle avec image (auth required)   |
| `/history/{user_id}`                        | GET     | Historique (auth required, user_id == current) |
| `/history/{user_id}/analyses/{analysis_id}` | GET     | Détail analyse (auth required)                 |
| `/history/{user_id}/export/csv`             | GET     | Exporter CSV (auth required)                   |
| `/history/{user_id}/export/pdf`             | GET     | Exporter PDF (auth required)                   |

## Flux demo recommandé (5-7 min)

Voir [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) pour le script détaillé avec timing et points de parole.

Résumé:

1. **Landing** (30s): Poser le problème et la promesse.
2. **Analytics** (1.5 min): Montrer les résultats réels (EfficientNetV2L best, DenseNet201 comparaison).
3. **Dashboard** (1 min): Aperçu parcellaire et analyses récentes.
4. **Upload** (2 min): Lancer une analyse mock, montrer résultat NPK + confiance + interprétation.
5. **History & Detail** (2 min): Montrer l'historique, cliquer sur une analyse pour voir le détail avec mini galerie.
6. **Conclusion** (30s): Résumer: aide à décision, pas de substitution labo, potentiel startup.

## Comptes de démo

Créés automatiquement:

- **alice** / **alice123** → 1 analyse dans historique
- **jury** / **jury123** → 2 analyses dans historique

Données:

- 3 parcelles existantes (parcelle_1, parcelle_2, parcelle_3)
- 6 analyses réparties sur 5 utilisateurs
- Chaque analyse avec: K0-K2, N0-N2, P0-P1, confiance 0.59-0.98, interprétation, recommandation

## Documentation

- [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) : Script complet avec timing, talking points, Q&A attendues.
- [ARCHITECTURE.md](./ARCHITECTURE.md) : Architecture système, routes API, flux données, scalabilité.
- [README.md](./README.md) : Ce fichier (installation, routes, API, positionnement).

## Message a porter pendant la soutenance

- Le systeme ne remplace pas l'analyse laboratoire.
- Il donne une estimation rapide, orientative et exploitable terrain.
- Le produit centralise les observations et aide a prioriser les actions.
- Les meilleurs resultats actuels viennent d'EfficientNetV2L, DenseNet201 reste une comparaison solide.

## Architecture

- Frontend Next.js + TypeScript + design SaaS agritech.
- Backend FastAPI + Pydantic + mode mock + preparation inference.
- Reutilisation directe des resultats et seuils deja produits dans `npk_models_*`.
