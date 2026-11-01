# System Architecture - Internship Saathi

## 1. Overview

**Internship Saathi** is an accessible, offline-friendly prototype designed to demonstrate how first-time applicants—including individuals with limited digital literacy or no formal resume—can discover 3–5 relevant sample internships. It is inspired by the problem statement of the PM Internship Scheme.

> [!IMPORTANT]
> **Prototype Nature**: This is a local educational prototype. All 120 internships and partner organizations are synthetic demonstration records. It is not an official government portal and does not submit real applications or verify official eligibility.

---

## 2. High-Level Architecture Diagram

```
+-------------------------------------------------------------------------+
|                              User Browser                               |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                       React + TypeScript UI                       |  |
|  |   - Language Switcher (EN / HI)                                   |  |
|  |   - Candidate Profile Wizard (In-Memory State)                    |  |
|  |   - Recommendations View (Up to 5 Ranked Matches)                 |  |
|  |   - Detail View & Saved Opportunities (LocalStorage IDs)          |  |
|  |   - PWA Service Worker (Offline Shell Caching)                    |  |
|  +---------------------------------+---------------------------------+  |
+------------------------------------|------------------------------------+
                                     |
                         HTTP / Native Fetch (/api/v1)
                                     |
+------------------------------------v------------------------------------+
|                         FastAPI Backend Server                          |
|                       (Python 3.12, Uvicorn)                            |
|                                                                         |
|  +---------------------------+       +-------------------------------+  |
|  |    API Endpoints          |       |    Recommendation Engine      |  |
|  |  - /api/v1/health         | ----> |  - Pre-filtering (Education,  |  |
|  |  - /api/v1/options        |       |    Deadlines, Hard Filters)   |  |
|  |  - /api/v1/internships    |       |  - Deterministic Hybrid Match |  |
|  |  - /api/v1/recommendations|       |  - Scikit-Learn TF-IDF Corpus |  |
|  +---------------------------+       |  - Dynamic Renormalization    |  |
|                                      +-------------------------------+  |
|                                                      |                  |
|  +---------------------------------------------------v---------------+  |
|  |                     SQLAlchemy 2.0 ORM                            |  |
|  |      - Synchronous Session pattern (PRAGMA foreign_keys = ON)     |  |
|  |      - Models: Internship, Skill, Sector, EducationCategory       |  |
|  +---------------------------------------------------+---------------+  |
+------------------------------------------------------|------------------+
                                                       |
                                            File-based SQL Engine
                                                       |
+------------------------------------------------------v------------------+
|                            SQLite Database                              |
|                         (backend/data/app.db)                           |
+-------------------------------------------------------------------------+
```

---

## 3. Component Details

### 3.1 Frontend
- **Framework**: Vite + React 19 + TypeScript.
- **Styling**: Tailwind CSS v3 with accessible color palettes (emerald, civic slate, amber).
- **Internationalization**: `i18next` and `react-i18next` with bundled offline JSON translations for English and Hindi.
- **Client Routing**: `react-router-dom` with HTML5 history navigation.
- **Progressive Web App (PWA)**: Configured via `vite-plugin-pwa` with local web manifest and service worker. API calls and recommendation submissions are deliberately excluded from caching to prevent stale results.

### 3.2 Backend
- **Framework**: FastAPI with Uvicorn server running on `127.0.0.1:8000`.
- **Settings**: Pydantic Settings reading from `backend/.env` with safe local defaults.
- **ORM & Migrations**: SQLAlchemy 2.0 and Alembic. The database path is resolved relative to `backend/data/app.db` so shifts in working directory never disrupt SQLite connection resolution.
- **Data Normalization**: Handles canonical code lookups, whitespace/alias normalization, and deduplication.

### 3.3 Database Models
- `internships`: Stores stable ID (e.g., `INT-001`), title, synthetic organization name, description, location (state, district), work mode (`onsite`, `hybrid`, `remote`), duration, stipend, deadline, active flag, and sample flag.
- `education_categories`: Education levels (`tenth_pass`, `twelfth_pass`, `iti`, `diploma`, `bachelors`, `masters`, `any`) with English & Hindi labels.
- `sectors`: Industry sectors with English & Hindi names.
- `skills`: Skills associated with sectors with English & Hindi names.
- `internship_skills` & `internship_educations`: Many-to-many relationship tables with foreign key cascades.

---

## 4. Privacy & Data Handling Guarantee
- **No Remote Tracking**: No external analytics, tracking pixels, or third-party cookies.
- **No User Profiles in Database**: Candidate responses in the wizard are kept strictly in browser memory. The submitted profile is evaluated on-the-fly in Python memory and never saved to the SQLite database.
- **No Sensitive Identifiers**: No Aadhaar numbers, phone numbers, email addresses, caste, or religious data are collected or requested.
- **Saved Opportunities**: Only the alphanumeric IDs of bookmarked internships are stored locally in the user's browser `localStorage`.

---

## 5. Future PostgreSQL Migration Path

While SQLite is optimal for local evaluation, zero setup, and portability, migrating to production-grade PostgreSQL is straightforward:

1. **Driver**: Install `psycopg[binary]>=3.1.0`.
2. **Configuration**: Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/internship_saathi"
   ```
3. **Database Session**: In `app/database.py`, the SQLite pragma handler is already conditionally applied only when `"sqlite"` is in `settings.DATABASE_URL`.
4. **Migrations**: Run `alembic upgrade head` against PostgreSQL. The schema uses standard ANSI SQL types (VARCHAR, INTEGER, BOOLEAN, DATE, TEXT) supported identically by PostgreSQL.
5. **Text Search**: The TF-IDF cosine similarity component can optionally be complemented by PostgreSQL's native `tsvector` and `pg_trgm` extensions for database-level full-text indexing.
