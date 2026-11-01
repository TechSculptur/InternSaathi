# Internship Saathi

Internship Saathi is a local internship recommendation prototype inspired by the PM Internship Scheme. The project helps a student move from an education profile, skill preferences, sector interests, and location/work-mode preferences to a ranked list of internship opportunities that are the most suitable.

The objective is not to replace an official government portal. It is a demo system that uses synthetic sample internship data and a transparent recommendation engine to explain why one listing is ranked above another.

> [!IMPORTANT]
> This is a demonstration prototype using sample internship records stored locally in the repository. It is not an official government application, and it does not perform live verification of government eligibility or application status.

---

## What the Project Is About

The project is a full-stack recommendation application that collects a learner profile through a web wizard and then returns an ordered list of internships.

The user journey is:

1. Choose education level.
2. Select or upload skills.
3. Choose sectors of interest.
4. Choose preferred state, district, and work mode.
5. Submit the profile to the backend recommendations API.

The backend reads the internship dataset from the local SQLite database, filters eligible opportunities, and ranks them using a deterministic hybrid matching system.

---

## Why This Exists

The project solves a real problem for students who need help finding internships that match their:

- education background
- skill knowledge
- preferred sector
- state, district or relocation willingness
- preferred work mode such as remote, hybrid, or on-site

Instead of showing a plain list, the application explains the reasons behind the ranked result with matched skills, sectors, location rules, and text similarity.

---

## Project Architecture

The system has three main layers:

### 1. Frontend Layer

The user interface is built using React + TypeScript + Vite.

Important frontend files:

- `frontend/src/pages/WizardPage.tsx` handles the four-step profile-building flow.
- `frontend/src/services/api.ts` sends request payloads to the backend and normalizes errors.
- `frontend/src/pages/RecommendationsPage.tsx` renders the ranked internship cards.

### 2. Backend Layer

The backend is built using FastAPI and Python.

Important backend files:

- `backend/app/routes.py` receives the candidate profile and returns a recommendation response.
- `backend/app/schemas.py` defines the profile payload and response models.
- `backend/app/services/recommender.py` contains the scoring engine.
- `backend/app/services/normalization.py` normalizes skills, sectors, education, and text inputs.
- `backend/app/services/embeddings.py` manages the sentence-embedding model and embedding cache.

### 3. Data Layer

The data is stored locally and seeded into SQLite.

Important data files:

- `backend/app/data/internships.json` contains sample internship records.
- `backend/app/data/taxonomy.json` contains taxonomy and labels.
- `backend/app/data/embeddings.npy` stores precomputed internship embedding vectors.
- `backend/app/data/embedding_ids.json` stores the internship IDs corresponding to the vectors.

---

## Workflow: From Profile to Internship Match

The complete recommendation procedure is:

### Step 1: Candidate Profile Creation

The user answers the wizard questions in the frontend:

- education
- skills
- sectors
- state
- district
- preferred work mode
- willingness to relocate
- optional resume text extracted from a file upload

This profile becomes a `CandidateProfile` request object.

### Step 2: Backend Validation

The recommendation route validates the request before scoring:

- education must be supported
- mandatory fields must be parsed correctly
- the request body must use the defined schema

If validation passes, the backend sends the normalized profile into the recommender.

### Step 3: Eligibility Filtering

The recommender loads active internships and applies hard filters:

- education compatibility
- work mode compatibility
- location compatibility
- relocation compatibility if required
- active listing checks

Only eligible internships are included in the ranking process.

### Step 4: Text & Skill Normalization

The recommender normalizes:

- skill codes such as `python` and `python_programming`
- sector codes
- state and district strings
- resume text and internship descriptions

This prevents inconsistent spelling or case differences from breaking the matching logic.

### Step 5: Hybrid Scoring

Each eligible internship receives a score from four components:

1. `Skill score`:
   - measures how closely the candidate skills overlap with the internship required skills
   - uses IDF weighting, so rare skills contribute stronger evidence

2. `Sector score`:
   - compares the selected sectors to the internship sector

3. `Location score`:
   - compares district, state, remote/hybrid/on-site preferences, and relocation willingness

4. `Text score`:
   - combines TF-IDF vector similarity and sentence embedding similarity

The final ranking is built from the weighted sum of these signals.

### Step 6: Reason Generation

The system explains the match using structured reason codes such as:

- `SECTOR_INTEREST`
- `SAME_DISTRICT`
- `NO_PRIOR_SKILLS_REQUIRED`
- `LIMITED_PROFILE_EXPLORATION`

Those reasons are returned to the frontend and shown in the recommendation cards.

### Step 7: Sort and Return Results

The recommender sorts by:

1. highest total score
2. earliest deadline
3. stable internship ID

The final response contains the top ranked internships and an explainable summary.

---

## What the Transformer Model `all-MiniLM-L6-v2` Does

The project uses the sentence-transformers model `all-MiniLM-L6-v2` in the embedding service.

That model converts text into a fixed-length dense vector called an embedding. In this project, the embedding model is used for semantic matching:

- the candidate query text is generated from selected skills, sectors, and optional resume text
- internship descriptions are converted into sentence vectors based on titles, sectors, descriptions, skills, and work mode
- the engine compares the direction and meaning of these vectors to estimate semantic similarity

The role of the model is not to decide eligibility directly. Instead, it enriches the text relevance component and helps catch meaning that simple keyword overlap might miss.

For example:

- a resume mentions �data science workflow�
- an internship description mentions �machine learning project lifecycle�

A pure keyword method might miss the semantic overlap, but the embedding model can represent both phrases in a vector space where similar meanings are closer.

The model is loaded lazily in the embedding service, and if the model fails to load, the project falls back to TF-IDF rather than stopping the app.

---

## Embeddings in This Project

Embeddings are vector representations of text that keep semantic meaning in numeric form.

In this repository:

- `all-MiniLM-L6-v2` is the transformer model used for sentence embeddings.
- `backend/app/services/embeddings.py` defines the service that loads the model, encodes text, and caches internship embeddings.
- `backend/app/data/embeddings.npy` stores the saved embedding matrix.
- `backend/app/data/embedding_ids.json` stores the IDs matched to those vectors.

The project also has a cache-based behavior:

- if cached internship embeddings already exist, the recommender uses them
- if not, it computes missing embeddings, stores them, and saves them on disk

That makes the semantic similarity branch faster across future runs.

---

## Recommendation Technique Used

The project uses a hybrid recommendation technique.

It combines:

- skill matching
- sector matching
- location and work-mode compatibility
- TF-IDF lexical matching
- transformer embedding similarity

This combination is deliberate. It balances explainability and ranking quality:

- `skill` and `sector` signals are easy for the user to understand.
- `location` and `work mode` reflect practical constraints.
- `text` signals provide a semantic layer using both word overlap and meaning similarity.

The final score is normalized and clipped to a `0.0` to `1.0` range and then transformed into a match tier:

- `strong` for scores above `0.75`
- `good` for scores above `0.50`
- `moderate` for scores above `0.25`
- `exploratory` below that

---

## Why the Project Uses a Hybrid Model

A pure TF-IDF approach sees words and phrase overlap, but it does not understand deeper semantic similarity.

A pure transformer embedding approach can understand meaning but can be slower and harder to explain.

The project combines both:

- use `TF-IDF` for lexical explainability and fast sparse similarity
- use `all-MiniLM-L6-v2` for semantic embedding similarity
- use structured domain rules for skills, sectors, location, and education eligibility

This results in a ranking engine that is both explainable and semantic-aware.

---

## Demo Scope and Data

The project uses synthetic sample internship listings rather than live public data.

The sample data was generated by the repo's seeding utilities and stored locally. It is suitable for a classroom, prototype, or local demo environment.

---

## Quick Start

### Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe seed.py
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Run the Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Run the Frontend

```powershell
cd frontend
npm run dev
```

---

## API Endpoints

The application exposes the API at the `/api/v1` prefix:

- `GET /api/v1/health`
- `GET /api/v1/options`
- `POST /api/v1/recommendations`
- `POST /api/v1/resume/parse`

---

## Testing

Backend tests and frontend tests are provided in the project.

Example:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

```powershell
cd frontend
npm run test
```

---

## Summary

Internship Saathi is a local internship recommendation engine for the PM Internship Scheme-inspired domain. It receives a student profile from a four-step React wizard, validates and normalizes the profile, filters internships by eligibility, scores them through a hybrid system, and returns a ranked list of internship opportunities with reasons.

The project uses `all-MiniLM-L6-v2` as its sentence-transformer embedding model to generate semantic embeddings and perform semantic text matching. These embeddings are stored in the `backend/app/data` cache files and used together with TF-IDF, skill overlap, sector alignment, and location scoring to produce the final recommendation list.


## JD-based resume tailoring (optional LLM feature)

The app includes a Resume Tailoring page at `/tailor-resume`. Users can upload a PDF/DOCX resume, select a sample internship when its description is available or paste a custom job description, review/edit the suggested content, and download an approved DOCX. The original resume is not overwritten.

To enable generation, add a Groq API key to `backend/.env` (created from `.env.example` during setup):

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Restart the backend after editing `.env`. Get a key from https://console.groq.com/. Without a key, the existing internship recommendation and resume parsing features continue to work, but resume tailoring returns a clear configuration error. Resume text is sent to the configured LLM provider for tailoring; users are warned in the UI and should upload only documents they are comfortable processing this way. Review generated content carefully before using it.
