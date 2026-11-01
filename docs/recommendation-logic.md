# Recommendation Engine & Scoring Logic

## 1. Design Philosophy

The recommendation engine in **Internship Saathi** is a **deterministic, content-based hybrid recommender**. It is designed with the following civic principles:

1. **Accessibility First**: Applicants with minimal schooling or zero prior experience are never penalized. Listings designed for beginners receive full score compatibility.
2. **Honesty & Explainability**: Every recommended opportunity provides 2–3 truthful, human-understandable reason codes (e.g. Same District, Sector Match, Beginner Friendly) in both English and Hindi.
3. **No Deceptive Percentages**: Scores are presented as **relative match tiers** ("Strong Match", "Good Match", "Relevant Opportunity") rather than "chances of admission" or "selection probability".
4. **No LLM Hallucinations**: Recommendations and explanations are generated deterministically using mathematical scoring formulas and structured locale dictionaries.

---

## 2. Recommendation Pipeline

```
Candidate Submission
        │
        ▼
[Step 1: Normalization & Validation]
  - Map education alias to canonical code (e.g., "12th" -> "twelfth_pass")
  - Deduplicate & clean skills and sectors
  - Resolve home state and district
  - Parse resume text (optional, in-memory only)
        │
        ▼
[Step 2: Hard Eligibility Filters]
  - Exclude inactive (is_active == False)
  - Exclude expired (deadline < today)
  - Check education category (internship accepts candidate's education or 'any')
  - Apply mandatory constraints ONLY if candidate flagged them (is_work_mode_mandatory, is_location_mandatory)
        │
        ▼
[Step 3: Component Scoring (Bounded [0.0, 1.0])]
  - Skill Overlap Score (S_skill) — F1-style harmonic mean with IDF weighting
  - Sector Interest Match (S_sector)
  - Location Compatibility (S_loc)
  - Semantic Similarity (S_text) — Sentence embeddings (primary) + TF-IDF (fallback)
        │
        ▼
[Step 4: Dynamic Weight Renormalization]
  - Non-applicable components have their base weights redistributed proportionally
  - Only renormalize when CANDIDATE omits input, never because LISTING is missing data
        │
        ▼
[Step 5: Deterministic Tie-Breaking & Top-5 Selection]
  - Sorted by: (-Total_Score, Deadline ASC, ID ASC)
  - Limit to top 5 results
```

---

## 3. Mathematical Formulation

### 3.1 Base Weights
The default baseline weights are:
- **Skill Overlap**: $W_{skill} = 0.40$
- **Sector Interest**: $W_{sector} = 0.30$
- **Location Compatibility**: $W_{loc} = 0.20$
- **Semantic Similarity**: $W_{text} = 0.10$

$$\sum W_{base} = 1.00$$

### 3.2 Component Definitions

#### A. Skill Overlap ($S_{skill}$) — F1-style Harmonic Mean with IDF Weighting

Let $C_{skills}$ be the candidate's normalized skills, and $I_{skills}$ be the internship's required skills.

**IDF Weighting**: Each skill $s$ has an Inverse Document Frequency weight $w_{IDF}(s)$ computed across all active internships:
$$w_{IDF}(s) = \log\left(\frac{N}{df(s) + 1}\right) + 1$$
Normalized to range $[0.5, 2.0]$, where $N$ = total internships, $df(s)$ = number of internships requiring skill $s$.

**Zero-skill listings** (allows_no_skills = true or empty skill list):
- If candidate has no skills: $S_{skill} = 0.8$ (perfect beginner match)
- If candidate has skills: $S_{skill} = 0.5$ (neutral — eligible but not a skill match)
- Reason code: `NO_PRIOR_SKILLS_REQUIRED`

**Candidate has no skills but listing requires them**:
- $S_{skill}$ is marked **Not Applicable (N/A)**. Its weight is redistributed via renormalization.

**Both have skills**: Compute F1-style harmonic mean with IDF weighting:
$$\text{coverage} = \frac{\sum_{s \in C \cap I} w_{IDF}(s)}{\sum_{s \in I} w_{IDF}(s)}$$
$$\text{relevance} = \frac{\sum_{s \in C \cap I} w_{IDF}(s)}{\min\left(\sum_{s \in C} w_{IDF}(s), \sum_{s \in I} w_{IDF}(s)\right)}$$
$$S_{skill} = \begin{cases} 0 & \text{if } C \cap I = \emptyset \\ \frac{2 \times \text{coverage} \times \text{relevance}}{\text{coverage} + \text{relevance}} & \text{otherwise} \end{cases}$$
Clamped to $[0.0, 1.0]$.

- Reason code: `SKILL_MATCH_EXACT` (lists matched skill names)

#### B. Sector Interest Match ($S_{sector}$)
Let $C_{sectors}$ be the set of sectors selected by the candidate:
- If $|C_{sectors}| > 0$:
  $$S_{sector} = \begin{cases} 1.0 & \text{if } I_{sector} \in C_{sectors} \\ 0.0 & \text{otherwise} \end{cases}$$
  - Reason code: `SECTOR_INTEREST` when $1.0$.
- If $|C_{sectors}| == 0$:
  - $S_{sector}$ is marked **Not Applicable (N/A)**.

#### C. Location Compatibility ($S_{loc}$)
Based on a documented deterministic preference matrix:
- **Remote Internships**:
  - Preferred mode is Remote: $S_{loc} = 1.0$ (`REMOTE_MATCH`).
  - Preferred mode is Any or Hybrid: $S_{loc} = 0.95$ (`REMOTE_FRIENDLY`).
  - Preferred mode is Onsite: $S_{loc} = 0.50$.
- **Onsite / Hybrid Internships**:
  - Same State + Same District: $S_{loc} = 1.0$ (`SAME_DISTRICT`).
  - Same State + Different District: $S_{loc} = 0.85$ (if willing to relocate) or $0.75$ (`SAME_STATE`).
  - Different State: $S_{loc} = 0.70$ (if willing to relocate, `RELOCATION_FRIENDLY`) or $0.20$.
- If no state/district was selected and mode is "any":
  - $S_{loc}$ is marked **Not Applicable (N/A)**.

#### D. Semantic Similarity ($S_{text}$)
**Primary: Sentence Embeddings (all-MiniLM-L6-v2)**
- At seed time, compute embedding for each internship from "title + organization + sector + description + skill names" and cache matrix on disk (`backend/data/embeddings.npy`).
- At request time, embed candidate's combined profile text (skills + sectors + resume_text).
- Cosine similarity between normalized embeddings.

**Fallback: TF-IDF**
- If model cannot be loaded (offline, no cache), fall back gracefully to TF-IDF pipeline.
- `TfidfVectorizer(stop_words='english', max_features=1000)` pre-fitted over active internship corpus.
- Cosine similarity between query vector and internship document vector.

**Hybrid**: When both available, blend 70% embeddings + 30% TF-IDF for robustness.
- If candidate provided neither skills nor sectors nor resume text:
  - $S_{text}$ is marked **Not Applicable (N/A)**.

---

## 4. Dynamic Weight Renormalization

When optional inputs are omitted by the **CANDIDATE** (not the listing), the engine dynamically renormalizes the remaining active components so the effective weights always sum to $1.00$:

$$\Omega_{active} = \{k \in \{\text{skill, sector, loc, text}\} \mid S_k \neq \text{N/A}\}$$

$$W_{eff, k} = \frac{W_{base, k}}{\sum_{j \in \Omega_{active}} W_{base, j}}$$

$$S_{total} = \sum_{k \in \Omega_{active}} S_k \times W_{eff, k}$$

### Example
If a candidate only provides education and sector interests (omitting skills and location):
- Active: Sector (0.30) and Text (0.10).
- Sum active = 0.40.
- $W_{eff, sector} = 0.30 / 0.40 = 0.75$
- $W_{eff, text} = 0.10 / 0.40 = 0.25$
- Effective weights sum to $1.00$.

**Key Change**: Zero-skill listings (allows_no_skills = true) do NOT cause skill weight renormalization. They receive a fixed neutral score (0.5 or 0.8) and keep the full 0.40 skill weight.

---

## 5. Match Tiers and Categorization

Total relative score is translated into clear qualitative tiers:
- **Strong Match**: $S_{total} \ge 0.75$
- **Good Match**: $0.50 \le S_{total} < 0.75$
- **Relevant Opportunity**: $0.25 \le S_{total} < 0.50$
- **General Suggestion**: $S_{total} < 0.25$

When a candidate submits only education and no other preferences, the system returns eligible starter opportunities with `has_limited_profile = True` and an explicit note:
> *"Limited profile information provided. Showing eligible starter opportunities based on your education."*

---

## 6. Reason Codes

| Code | Description | Parameters |
|------|-------------|------------|
| `SKILL_MATCH_EXACT` | Exact skill matches with IDF weighting | `matched_skills`: list of skill names |
| `TECH_STACK_MATCH` | Multiple related technical skills matched | `matched_skills`: list of skill names |
| `SECTOR_INTEREST` | Sector matches candidate interest | `sector`: sector name |
| `SAME_DISTRICT` | Same district as candidate | `district`, `state` |
| `SAME_STATE` | Same state as candidate | `state` |
| `RELOCATION_FRIENDLY` | Different state but willing to relocate | `state` |
| `REMOTE_MATCH` | Matches preferred remote mode | — |
| `REMOTE_FRIENDLY` | Remote opportunity compatible with hybrid/any | — |
| `NO_PRIOR_SKILLS_REQUIRED` | Listing open to beginners | — |
| `LIMITED_PROFILE_EXPLORATION` | Minimal profile, general suggestion | — |

---

## 7. Resume Parsing (Privacy-Preserving)

- **Endpoint**: `POST /api/v1/resume/parse`
- **Accepts**: PDF (via pypdf) or DOCX (via python-docx), max 5 MB
- **Processing**: IN MEMORY ONLY — never written to disk, database, or logs
- **Returns**: Detected skill codes, inferred education level, truncated resume text (first 2000 chars) for semantic matching
- **Skill Matching**: Case-insensitive, alias-aware (e.g., "py" → python, "reactjs" → react, "ml" → machine_learning)
- **Frontend**: Drop zone in Skills step, pre-selects detected skills as removable chips, shows bilingual privacy note