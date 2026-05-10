# ARCHITECTURE.md

## Vue d'ensemble

SoilAI est une plateforme full-stack agritech de pré-diagnostic NPK. Elle couple un backend API robuste à un frontend SaaS fluide, tout en s'appuyant sur des modèles d'entraînement réels pour les seuils et prédictions.

```
┌──────────────────────┐
│    FRONTEND (Next.js)│
├──────────────────────┤
│ Landing / Dashboard  │
│ Upload / Analytics   │
│ History / Detail     │
│ Auth / Profile       │
└──────────────────────┘
           ↓ HTTP/REST
┌──────────────────────┐
│   BACKEND (FastAPI)  │
├──────────────────────┤
│ Auth / Users         │
│ Parcels (CRUD)       │
│ Predict (Mock/Real)  │
│ History / Export     │
└──────────────────────┘
           ↓
┌──────────────────────┐
│   MODELS & DATA      │
├──────────────────────┤
│ EfficientNetV2L      │
│ DenseNet201          │
│ Thresholds (JSON)    │
│ Predictions (SQLite) │
└──────────────────────┘
```

---

## Frontend (Next.js + TypeScript)

### Structure

- `app/` : Pages et routes (landing, login, dashboard, history, upload, etc.).
- `components/` : Composants réutilisables (buttons, cards, sections).
- `lib/` : Utilitaires (API client, types, helpers).

### Flux principal

1. **Landing page**: Poser la promesse et les limites.
2. **Auth**: Login/register, token JWT en localStorage.
3. **Dashboard**: Aperçu des parcelles et analyses récentes.
4. **Upload**: Sélectionner une parcelle, uploader image, lancer prédiction.
5. **History**: Consulter les analyses passées, filtrer par parcelle.
6. **Detail**: Voir une analyse en détail (image, NPK, confiance, interprétation).
7. **Exports**: Télécharger CSV/PDF du suivi par parcelle ou utilisateur.

### Technologie

- **Framework**: Next.js 14 (App Router).
- **Language**: TypeScript.
- **Styling**: Tailwind CSS + design tokens agritech (soil, leaf colors).
- **Auth**: JWT tokens via localStorage.
- **API Client**: Fetch natif avec gestion erreurs.

---

## Backend (FastAPI + Pydantic)

### Structure

- `app/main.py` : Initialisation FastAPI et mounting des routes.
- `app/api/v1/routes/` : Endpoints (auth, parcels, predict, history, export).
- `app/models/` : Modèles SQLAlchemy (User, Parcel).
- `app/schemas/` : Schemas Pydantic (request/response).
- `app/services/` : Logique métier (auth, history, prediction, export).
- `app/core/` : Configuration et dépendances.

### Routes clés

| Endpoint                                    | Méthode            | Description                            |
| ------------------------------------------- | ------------------ | -------------------------------------- |
| `/health`                                   | GET                | Health check.                          |
| `/auth/register`                            | POST               | Créer compte.                          |
| `/auth/login`                               | POST               | Login et token JWT.                    |
| `/auth/me`                                  | GET                | Profil utilisateur connecté.           |
| `/parcels`                                  | GET, POST          | Lister/créer parcelles.                |
| `/parcels/{id}`                             | GET, PATCH, DELETE | Détail/update/supprimer parcelle.      |
| `/predict/mock`                             | POST               | Prédiction mock pour démo.             |
| `/predict`                                  | POST               | Prédiction réelle (avec upload image). |
| `/history/{user_id}`                        | GET                | Historique des analyses.               |
| `/history/{user_id}/analyses/{analysis_id}` | GET                | Détail d'une analyse.                  |
| `/history/{user_id}/export/csv`             | GET                | Export CSV historique.                 |
| `/history/{user_id}/export/pdf`             | GET                | Export PDF historique.                 |

### Modèles IA

**EfficientNetV2L** (meilleur résultat)

- Entraîné sur 300 images réelles (9 parcelles).
- Prédit 9 labels: K0/K1/K2, N0/N1/N2, P0/P1.
- Seuils appliqués depuis `npk_models_efficientnetv2l/seuil_*.json`.
- F1 macro: ~0.92, Accuracy: ~0.88.

**DenseNet201** (comparaison stable)

- Même dataset, même labels.
- F1 macro: ~0.88, Accuracy: ~0.84.
- Seuils appliqués depuis `npk_models_densenet201/seuil_*.json`.

### Données persistées

- **Users**: `soilai.db` (SQLite), colonnes: id, email, password_hash, full_name.
- **Parcels**: `soilai.db`, colonnes: id, user_id, name, location.
- **History**: `history_store.json`, format:
  ```json
  {
    "user_id": [
      {
        "analysis_id": "uuid",
        "parcel_id": "uuid",
        "parcel": { ParcelPublic },
        "image_name": "filename.jpg",
        "created_at": "ISO8601",
        "prediction": { PredictionResponse }
      }
    ]
  }
  ```

### Mode mock

- `/predict/mock` retourne une prédiction simulée déterministe basée sur `parcel_id` + `image_name`.
- Confiance et probas varient pour montrer la variabilité réaliste.
- Utilisé pour démo et test sans charger les vrais modèles.

### Mode réel (préparation)

- `/predict` accepterait une image uploadée.
- Chargerait le modèle EfficientNetV2L depuis disk.
- Préprocesserait l'image (resize, normalize).
- Inférerait et appliquerait seuils.
- Persisterait le résultat dans l'historique.

---

## Flux de données

### Upload & Prédiction

1. Frontend: utilisateur upload image + sélectionne parcelle.
2. Frontend: POST `/predict` avec FormData (image, parcel_id).
3. Backend: valide requête, récupère parcel depuis DB, crée/charge modèle.
4. Backend: inférence image → prédiction K, N, P + confiance.
5. Backend: applique seuils depuis JSON (si confiance dépassable).
6. Backend: retourne `PredictionResponse` au frontend.
7. Frontend: affiche résultat, propose actions (export, relance, detail).

### Persistance historique

1. Après chaque prédiction, backend appelle `HistoryService.add_entry()`.
2. Entry ajoutée en haut du fichier `history_store.json` (LIFO).
3. Frontend recharge l'historique depuis `/history/{user_id}`.
4. Chaque entry est enrichie avec les détails parcelle (lookup).
5. Historique filtrable par parcelle.

### Export

1. Frontend: utilisateur clique "Export CSV" ou "Export PDF".
2. Frontend: GET `/history/{user_id}/export/csv?parcel_id=...`.
3. Backend: `ExportService` construit table depuis historique filtré.
4. Backend: retourne blob (CSV ou PDF généré).
5. Frontend: télécharge fichier automatiquement.

---

## Sécurité

- **Auth**: JWT tokens, secret en config, validé sur chaque requête protégée.
- **User isolation**: chaque utilisateur ne voit que ses propres parcelles et analyses.
- **CORS**: configuré pour accueillir frontend (localhost:3000 en dev, domaine en prod).
- **Rate limiting**: non implémenté mais recommandé en prod.
- **Input validation**: Pydantic schemas sur toutes les entrées.

---

## Scalabilité (roadmap)

### Court terme

- Passer de SQLite à PostgreSQL pour multi-user en prod.
- Ajouter Redis pour cache (résultats API fréquentes).
- Déployer sur cloud (AWS, GCP, Azure) avec load balancer.

### Moyen terme

- Inférence asynchrone (Celery queue) pour images volumineuses.
- Stockage S3 pour images et exports.
- CDN pour frontend (Cloudflare, AWS CloudFront).

### Long terme

- Multi-modèle automatique (A/B testing).
- Fine-tuning continu sur nouvelles images.
- Intégration IoT (capteurs température, humidité, pH).
- API webhook pour notifications et intégration tiers.

---

## Limitations actuelles

- Modèles entraînés sur ~300 images: peu de généralisation cross-terroir.
- Image upload: pas de vrai stockage d'images (juste filename en JSON).
- Inférence: mode mock pour démo, inference réelle pas testée en prod.
- Multi-région: centralisé sur un seul serveur.
- Analytics avancée: dashboard basique, pas de trends/forecasting.

---

## Tech stack résumé

| Couche              | Tech               | Version |
| ------------------- | ------------------ | ------- |
| **Frontend**        | Next.js            | 14.2    |
| **Frontend**        | TypeScript         | 5.x     |
| **Frontend**        | Tailwind CSS       | 3.x     |
| **Backend**         | FastAPI            | 0.100+  |
| **Backend**         | Pydantic           | 2.x     |
| **Backend**         | SQLAlchemy         | 2.x     |
| **Database**        | SQLite             | 3.x     |
| **IA**              | PyTorch            | 1.13+   |
| **IA**              | torchvision        | 0.14+   |
| **Deployment**      | Docker (optionnel) | latest  |
| **Package manager** | npm                | 9.x     |
| **Package manager** | pip                | 23.x    |

---

## Pour démarrer en dev

```bash
# Backend
cd backend
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
uvicorn app.main:app --reload

# Frontend (dans un autre terminal)
cd frontend
npm install
npm run dev
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
API docs: http://localhost:8000/docs (Swagger)
