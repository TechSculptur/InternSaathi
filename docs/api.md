# REST API Reference - Internship Saathi

The backend API is implemented with FastAPI and conforms to REST conventions with typed Pydantic models.

- **Base URL**: `http://127.0.0.1:8000`
- **Prefix**: `/api/v1`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **Alternative ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 1. Endpoints

### 1.1 `GET /api/v1/health`
Checks server health, timestamp, and loaded sample data count.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "app": "Internship Saathi",
  "version": "1.0.0",
  "timestamp": "2026-09-11T19:30:00",
  "sample_data_count": 120,
  "disclaimer": "Demonstration prototype. Sample internships only. Not an official government portal."
}
```

---

### 1.2 `GET /api/v1/options`
Retrieves taxonomy metadata for populating candidate filters and forms.

#### Response `200 OK`
```json
{
  "education_categories": [
    { "code": "tenth_pass", "label_en": "10th Pass / Secondary", "label_hi": "10वीं पास / माध्यमिक" },
    { "code": "twelfth_pass", "label_en": "12th Pass / Higher Secondary", "label_hi": "12वीं पास / उच्च माध्यमिक" }
  ],
  "sectors": [
    { "code": "it_software", "name_en": "IT & Digital Services", "name_hi": "आईटी एवं डिजिटल सेवाएं" }
  ],
  "skills": [
    { "code": "python", "name_en": "Python Programming", "name_hi": "पायथन प्रोग्रामिंग", "sector_code": "it_software" }
  ],
  "states_and_districts": [
    {
      "state_en": "Maharashtra",
      "state_hi": "महाराष्ट्र",
      "districts": [
        { "name_en": "Pune", "name_hi": "पुणे" }
      ]
    }
  ],
  "work_modes": [
    { "code": "any", "label_en": "Any Mode (Flexible)", "label_hi": "कोई भी मोड (लचीला)" },
    { "code": "onsite", "label_en": "On-site / In-person", "label_hi": "कार्यालय में (ऑन-साइट)" }
  ]
}
```

---

### 1.3 `GET /api/v1/internships`
Returns paginated list of active sample internships with optional filtering.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `page` | int | No | 1 | Page number (>= 1) |
| `page_size` | int | No | 20 | Items per page (max 50) |
| `sector` | string | No | null | Filter by sector code |
| `work_mode`| string | No | null | Filter by mode (`onsite`, `hybrid`, `remote`) |
| `state` | string | No | null | Filter by state name |

#### Response `200 OK`
```json
{
  "items": [
    {
      "id": "INT-001",
      "title": "Junior Web Development Intern",
      "organization_name": "Pragati Tech Solutions",
      "sector": { "id": 1, "code": "it_software", "name_en": "IT & Digital Services", "name_hi": "आईटी" },
      "state": "Maharashtra",
      "district": "Mumbai",
      "work_mode": "onsite",
      "duration_months": 6,
      "stipend_inr": 8500,
      "deadline": "2026-11-30",
      "is_active": true,
      "allows_no_skills": false,
      "is_sample": true
    }
  ],
  "pagination": {
    "total": 120,
    "page": 1,
    "page_size": 20,
    "total_pages": 6
  }
}
```

---

### 1.4 `GET /api/v1/internships/{id}`
Returns full description, required skills, and accepted education for a specific listing.

#### Response `200 OK`
```json
{
  "id": "INT-001",
  "title": "Junior Web Development Intern",
  "organization_name": "Pragati Tech Solutions",
  "description": "Frontend Support & Web Page Assistant...",
  "sector": { "id": 1, "code": "it_software", "name_en": "IT & Digital Services", "name_hi": "आईटी" },
  "state": "Maharashtra",
  "district": "Mumbai",
  "work_mode": "onsite",
  "duration_months": 6,
  "stipend_inr": 8500,
  "deadline": "2026-11-30",
  "is_active": true,
  "allows_no_skills": false,
  "is_sample": true,
  "required_skills": [
    { "id": 1, "code": "javascript", "name_en": "Web Basics / JavaScript", "name_hi": "वेब बेसिक्स" }
  ],
  "accepted_educations": [
    { "id": 4, "code": "diploma", "label_en": "Polytechnic / Diploma", "label_hi": "डिप्लोमा" }
  ]
}
```

#### Error `404 Not Found`
```json
{ "detail": "Internship with ID 'INT-999' not found." }
```

---

### 1.5 `POST /api/v1/recommendations`
Evaluates a candidate profile against eligible sample internships and computes ranked recommendations with component breakdown.

#### Request Body
```json
{
  "profile": {
    "education": "twelfth_pass",
    "skills": ["python", "ms_excel"],
    "sectors": ["it_software"],
    "state": "Maharashtra",
    "district": "Pune",
    "preferred_work_mode": "any",
    "is_work_mode_mandatory": false,
    "is_location_mandatory": false,
    "willing_to_relocate": true
  },
  "limit": 5
}
```

#### Response `200 OK`
```json
{
  "results": [
    {
      "internship": { "...": "..." },
      "relative_score": 0.893,
      "match_tier": "strong",
      "component_scores": {
        "skill_score": 1.0,
        "sector_score": 1.0,
        "location_score": 0.85,
        "text_score": 0.45
      },
      "effective_weights": {
        "skill_weight": 0.4,
        "sector_weight": 0.3,
        "location_weight": 0.2,
        "text_weight": 0.1
      },
      "missing_skills": [],
      "reasons": [
        {
          "code": "SKILL_MATCH",
          "params": { "matched_skills": ["Python Programming", "MS Excel"] },
          "text_en": "Matches your listed skills (Python Programming, MS Excel).",
          "text_hi": "आपके सूचीबद्ध कौशलों से मेल खाता है (Python Programming, MS Excel)।"
        }
      ],
      "is_sample": true
    }
  ],
  "total_eligible": 45,
  "has_limited_profile": false,
  "profile_summary_en": "Evaluated 45 eligible opportunities based on your education (twelfth_pass). Returned top 5 relative matches.",
  "profile_summary_hi": "...",
  "disclaimer": "Demonstration prototype. Sample internships only. Not an official government portal."
}
```

#### Error `422 Unprocessable Entity`
Returned if education qualification is missing or unrecognized.

---

### 1.6 `POST /api/v1/resume/parse`
Parses an uploaded resume (PDF or DOCX) and extracts skills for recommendation matching. **Privacy-preserving: processed in memory only, never stored.**

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**: `file` — PDF or DOCX file (max 5 MB)

#### Response `200 OK`
```json
{
  "detected_skills": ["python", "fastapi", "sql", "docker", "aws", "machine_learning", "pandas"],
  "detected_education": "bachelors",
  "resume_text": "Python developer with 2 years experience in Django and FastAPI. Skilled in SQL, PostgreSQL, Docker, and AWS. Machine learning experience with scikit-learn and pandas.",
  "privacy_note_en": "Your resume is processed in memory and never stored.",
  "privacy_note_hi": "आपका रिज्यूमे केवल मेमोरी में प्रोसेस किया जाता है और कभी स्टोर नहीं किया जाता।"
}
```

#### Error `400 Bad Request`
- Unsupported file type (only PDF and DOCX accepted)
- Could not extract text from file (e.g., scanned/image-based PDF)

#### Error `413 Payload Too Large`
- File exceeds 5 MB limit

---

### 1.7 `POST /api/v1/recommendations` (Updated)
Evaluates a candidate profile against eligible sample internships and computes ranked recommendations with component breakdown.

#### Request Body (Updated)
```json
{
  "profile": {
    "education": "twelfth_pass",
    "skills": ["python", "ms_excel"],
    "sectors": ["it_software"],
    "state": "Maharashtra",
    "district": "Pune",
    "preferred_work_mode": "any",
    "is_work_mode_mandatory": false,
    "is_location_mandatory": false,
    "willing_to_relocate": true,
    "resume_text": "Optional extracted resume text for semantic matching"
  },
  "limit": 5
}
```

#### Response `200 OK` (Updated)
```json
{
  "results": [
    {
      "internship": { "...": "..." },
      "relative_score": 0.893,
      "match_tier": "strong",
      "component_scores": {
        "skill_score": 0.85,
        "sector_score": 1.0,
        "location_score": 0.85,
        "text_score": 0.72
      },
      "effective_weights": {
        "skill_weight": 0.4,
        "sector_weight": 0.3,
        "location_weight": 0.2,
        "text_weight": 0.1
      },
      "missing_skills": [],
      "reasons": [
        {
          "code": "SKILL_MATCH_EXACT",
          "params": { "matched_skills": ["Python Programming", "MS Excel", "FastAPI"] },
          "text_en": "Matches your skills: Python Programming, MS Excel, FastAPI.",
          "text_hi": "आपके कौशलों से मेल खाता है: Python Programming, MS Excel, FastAPI।"
        }
      ],
      "is_sample": true
    }
  ],
  "total_eligible": 45,
  "has_limited_profile": false,
  "profile_summary_en": "Evaluated 45 eligible opportunities based on your education (twelfth_pass). Returned top 5 relative matches.",
  "profile_summary_hi": "...",
  "disclaimer": "Demonstration prototype. Sample internships only. Not an official government portal."
}
```

#### New Reason Codes
| Code | Description |
|------|-------------|
| `SKILL_MATCH_EXACT` | Exact skill matches with IDF weighting (lists matched skills) |
| `TECH_STACK_MATCH` | Multiple related technical skills matched |
| `NO_PRIOR_SKILLS_REQUIRED` | Listing open to beginners (fixed score 0.5/0.8) |

#### Scoring Changes
- **Skill Score**: F1-style harmonic mean with IDF weighting (replaces simple overlap ratio)
- **Zero-skill listings**: Fixed score 0.5 (candidate has skills) or 0.8 (beginner), no weight renormalization
- **Weight Renormalization**: Only when candidate omits input, never because listing lacks data
- **Semantic Similarity**: Sentence embeddings (all-MiniLM-L6-v2) with TF-IDF fallback
