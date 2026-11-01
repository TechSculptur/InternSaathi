from datetime import date
from typing import List, Dict, Tuple, Optional, Any, Set
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models import Internship
from app.models import EducationCategory
from app.models import Sector
from app.models import Skill
from app.schemas import (
    CandidateProfile,
    RecommendedInternship,
    ComponentScores,
    EffectiveWeights,
    ReasonCode,
    RecommendationResponse,
)
from app.schemas import InternshipDetail, SkillSummary, EducationSummary, SectorSummary
from app.services.normalization import (
    normalize_education,
    normalize_skills,
    normalize_sectors,
    normalize_location_string,
    clean_text,
)
from app.services.embeddings import get_embedding_service, EmbeddingService

# Baseline weights
BASE_WEIGHT_SKILL = 0.40
BASE_WEIGHT_SECTOR = 0.30
BASE_WEIGHT_LOCATION = 0.20
BASE_WEIGHT_TEXT = 0.10

# IDF cache for skill weighting
_idf_cache: Optional[Dict[str, float]] = None


def compute_skill_idf(internships: List[Internship]) -> Dict[str, float]:
    """
    Compute Inverse Document Frequency for each skill across all internships.
    Rare skills get higher weight.
    """
    global _idf_cache
    if _idf_cache is not None:
        return _idf_cache

    skill_doc_count: Dict[str, int] = {}
    total_docs = len(internships)

    for inst in internships:
        inst_skills = {sk.code for sk in inst.required_skills}
        for skill in inst_skills:
            skill_doc_count[skill] = skill_doc_count.get(skill, 0) + 1

    # Compute IDF: log(N / (df + 1)) + 1 to ensure positive values
    # Adding 1 to df prevents division by zero, adding 1 to result ensures minimum weight of 1
    idf = {}
    for skill, df in skill_doc_count.items():
        idf[skill] = math.log(total_docs / (df + 1)) + 1.0

    # Normalize IDF values to [0.5, 2.0] range for reasonable weighting
    if idf:
        min_idf = min(idf.values())
        max_idf = max(idf.values())
        if max_idf > min_idf:
            for skill in idf:
                # Scale to [0.5, 2.0]
                idf[skill] = 0.5 + 1.5 * (idf[skill] - min_idf) / (max_idf - min_idf)
        else:
            for skill in idf:
                idf[skill] = 1.0

    _idf_cache = idf
    return idf


def calculate_skill_score(
    candidate_skills: Set[str],
    internship_skills: Set[str],
    internship_allows_no_skills: bool,
    idf_weights: Dict[str, float],
    has_user_skills: bool,
) -> Tuple[Optional[float], List[ReasonCode]]:
    """
    Calculate skill score using F1-style harmonic mean with IDF weighting.

    Returns: (skill_score, reason_codes)
    """
    reasons: List[ReasonCode] = []

    # Zero-skill listing handling
    if len(internship_skills) == 0 or internship_allows_no_skills:
        if has_user_skills:
            # Candidate has skills but listing doesn't require any
            return 0.5, [ReasonCode(
                code="NO_PRIOR_SKILLS_REQUIRED",
                params={},
                text_en="Open to beginners: no prior specialized skills required.",
                text_hi="शुरुआती उम्मीदवारों के लिए खुला: किसी पूर्व विशिष्ट कौशल की आवश्यकता नहीं।"
            )]
        else:
            # Both candidate and listing have no skills - neutral beginner match
            return 0.8, [ReasonCode(
                code="NO_PRIOR_SKILLS_REQUIRED",
                params={},
                text_en="Open to beginners: no prior specialized skills required.",
                text_hi="शुरुआती उम्मीदवारों के लिए खुला: किसी पूर्व विशिष्ट कौशल की आवश्यकता नहीं।"
            )]

    # Candidate has no skills but listing requires them
    if not has_user_skills or len(candidate_skills) == 0:
        return None, []  # N/A - weight will be renormalized

    # Both have skills - compute F1-style harmonic mean with IDF weighting
    overlap = candidate_skills.intersection(internship_skills)

    if len(overlap) == 0:
        return 0.0, []  # No overlap

    # IDF-weighted coverage: sum of IDF for matched skills / sum of IDF for all required skills
    matched_idf_sum = sum(idf_weights.get(s, 1.0) for s in overlap)
    required_idf_sum = sum(idf_weights.get(s, 1.0) for s in internship_skills)
    candidate_idf_sum = sum(idf_weights.get(s, 1.0) for s in candidate_skills)

    coverage = matched_idf_sum / required_idf_sum if required_idf_sum > 0 else 0.0
    relevance = matched_idf_sum / min(candidate_idf_sum, required_idf_sum) if min(candidate_idf_sum, required_idf_sum) > 0 else 0.0

    # F1-style harmonic mean
    if coverage + relevance > 0:
        skill_score = 2 * coverage * relevance / (coverage + relevance)
    else:
        skill_score = 0.0

    # Clamp to [0, 1]
    skill_score = max(0.0, min(1.0, skill_score))

    # Add reason code with matched skill names
    if overlap:
        matched_names = [s.replace("_", " ").title() for s in overlap]
        reasons.append(ReasonCode(
            code="SKILL_MATCH_EXACT",
            params={"matched_skills": matched_names},
            text_en=f"Matches your skills: {', '.join(matched_names[:3])}{'...' if len(matched_names) > 3 else ''}.",
            text_hi=f"आपके कौशलों से मेल खाता है: {', '.join(matched_names[:3])}{'...' if len(matched_names) > 3 else ''}।"
        ))

    return skill_score, reasons


class RecommenderEngine:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.corpus_matrix: Optional[Any] = None
        self.internship_ids: List[str] = []
        self._cache_key: Optional[int] = None
        self._embedding_service: Optional[EmbeddingService] = None

    def _get_embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    def build_corpus(self, internships: List[Internship]):
        """Fit TF-IDF on internship corpus and cache matrix."""
        self.internship_ids = [i.id for i in internships]
        corpus_texts = []
        for i in internships:
            skill_names = " ".join([sk.code.replace("_", " ") for sk in i.required_skills])
            sec_name = i.sector.code.replace("_", " ") if i.sector else ""
            doc = f"{i.title} {sec_name} {i.description} {skill_names} {i.work_mode}"
            corpus_texts.append(clean_text(doc))

        if not corpus_texts or all(len(t.strip()) == 0 for t in corpus_texts):
            self.vectorizer = None
            self.corpus_matrix = None
            return

        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        try:
            self.corpus_matrix = self.vectorizer.fit_transform(corpus_texts)
        except ValueError:
            # Handle empty vocabulary
            self.vectorizer = None
            self.corpus_matrix = None

    def ensure_corpus_fitted(self, internships: List[Internship]):
        count = len(internships)
        if self.corpus_matrix is None or self._cache_key != count or len(self.internship_ids) != count:
            self.build_corpus(internships)
            self._cache_key = count

    def calculate_location_score(
        self,
        candidate_state: Optional[str],
        candidate_district: Optional[str],
        candidate_work_mode: str,
        willing_to_relocate: bool,
        internship: Internship
    ) -> Tuple[Optional[float], Optional[ReasonCode]]:
        """Deterministic location preference calculation bounded between 0.0 and 1.0."""
        # If candidate has no location preference and accepts any work mode, mark N/A
        if not candidate_state and not candidate_district and (not candidate_work_mode or candidate_work_mode == "any"):
            return None, None

        i_mode = internship.work_mode.lower()
        pref_mode = candidate_work_mode.lower() if candidate_work_mode else "any"

        # Remote internship scoring
        if i_mode == "remote":
            if pref_mode == "remote":
                return 1.0, ReasonCode(
                    code="REMOTE_MATCH",
                    params={},
                    text_en="Matches your preferred remote / work-from-home mode.",
                    text_hi="आपके पसंदीदा रिमोट / वर्क-फ्रॉम-होम मोड से मेल खाता है।"
                )
            elif pref_mode in ["any", "hybrid"]:
                return 0.95, ReasonCode(
                    code="REMOTE_FRIENDLY",
                    params={},
                    text_en="Remote opportunity that can be performed from anywhere.",
                    text_hi="रिमोट अवसर जिसे कहीं से भी किया जा सकता है।"
                )
            else:
                return 0.5, None

        # Onsite or Hybrid internship
        c_state = clean_text(candidate_state or "")
        c_dist = clean_text(candidate_district or "")
        i_state = clean_text(internship.state)
        i_dist = clean_text(internship.district)

        # Exact district match
        if c_state and c_dist and c_state == i_state and c_dist == i_dist:
            return 1.0, ReasonCode(
                code="SAME_DISTRICT",
                params={"district": internship.district, "state": internship.state},
                text_en=f"Located in your home district: {internship.district}.",
                text_hi=f"आपके गृह जिले में स्थित है: {internship.district}।"
            )

        # Same state match
        if c_state and c_state == i_state:
            score = 0.85 if willing_to_relocate else 0.75
            return score, ReasonCode(
                code="SAME_STATE",
                params={"state": internship.state},
                text_en=f"Located in your home state: {internship.state}.",
                text_hi=f"आपके गृह राज्य में स्थित है: {internship.state}।"
            )

        # Different state
        if willing_to_relocate:
            return 0.70, ReasonCode(
                code="RELOCATION_FRIENDLY",
                params={"state": internship.state},
                text_en=f"Opportunity in {internship.state} compatible with relocation preference.",
                text_hi=f"{internship.state} में अवसर जो स्थानांतरण (रीलोकेशन) के अनुकूल है।"
            )
        else:
            return 0.20, None

    def recommend(
        self,
        profile: CandidateProfile,
        db: Session,
        limit: int = 5,
        reference_date: Optional[date] = None,
        resume_text: Optional[str] = None
    ) -> RecommendationResponse:
        today = reference_date or date.today()

        # Step 1: Validation and Normalization
        norm_education = normalize_education(profile.education)
        if not norm_education:
            return RecommendationResponse(
                results=[],
                total_eligible=0,
                has_limited_profile=True,
                profile_summary_en="Invalid or unrecognized education qualification.",
                profile_summary_hi="अमान्य या अपरिचित शैक्षणिक योग्यता।"
            )

        norm_skills = normalize_skills(profile.skills)
        norm_sectors = normalize_sectors(profile.sectors)
        norm_state = normalize_location_string(profile.state)
        norm_district = normalize_location_string(profile.district)
        pref_work_mode = profile.preferred_work_mode.strip().lower() if profile.preferred_work_mode else "any"

        # Load all active, unexpired internships
        all_internships = (
            db.query(Internship)
            .filter(Internship.is_active == True, Internship.deadline >= today)
            .all()
        )

        # Step 2: Eligibility Filters
        eligible: List[Internship] = []
        for i in all_internships:
            # Education eligibility check
            accepted_codes = {e.code for e in i.accepted_educations}
            is_edu_eligible = ("any" in accepted_codes) or (norm_education in accepted_codes)
            if not is_edu_eligible:
                continue

            # Mandatory Work Mode constraint
            if profile.is_work_mode_mandatory and pref_work_mode != "any":
                if i.work_mode.lower() != pref_work_mode:
                    continue

            # Mandatory Location constraint
            if profile.is_location_mandatory and norm_state:
                if i.work_mode.lower() == "remote":
                    pass
                else:
                    i_state_clean = clean_text(i.state)
                    c_state_clean = clean_text(norm_state)
                    if i_state_clean != c_state_clean:
                        continue
                    if norm_district:
                        i_dist_clean = clean_text(i.district)
                        c_dist_clean = clean_text(norm_district)
                        if i_dist_clean != c_dist_clean:
                            continue

            eligible.append(i)

        if not eligible:
            return RecommendationResponse(
                results=[],
                total_eligible=0,
                has_limited_profile=False,
                profile_summary_en="No internships found matching your mandatory eligibility criteria.",
                profile_summary_hi="आपकी अनिवार्य पात्रता मानदंडों से मेल खाने वाला कोई इंटर्नशिप नहीं मिला।"
            )

        # Step 3: Prepare scoring components
        self.ensure_corpus_fitted(eligible)
        corpus_id_to_idx = {i_id: idx for idx, i_id in enumerate(self.internship_ids)}

        # Build candidate query text for TF-IDF and embeddings
        query_parts = []
        if norm_skills:
            query_parts.extend([s.replace("_", " ") for s in norm_skills])
        if norm_sectors:
            query_parts.extend([s.replace("_", " ") for s in norm_sectors])
        if resume_text:
            query_parts.append(resume_text[:500])  # Limit resume text contribution
        query_text = clean_text(" ".join(query_parts))

        query_vec = None
        if self.vectorizer and query_text:
            try:
                query_vec = self.vectorizer.transform([query_text])
            except Exception:
                query_vec = None

        # Get embedding service for semantic similarity
        embedding_service = self._get_embedding_service()
        candidate_embedding = None
        if query_text:
            candidate_embedding = embedding_service.encode(query_text)

        # Pre-compute internship embeddings
        internship_embeddings = embedding_service.encode_internships(eligible)

        # Compute IDF weights for skills
        idf_weights = compute_skill_idf(eligible)

        has_user_skills = len(norm_skills) > 0
        has_user_sectors = len(norm_sectors) > 0
        has_user_location = bool(norm_state or norm_district or (pref_work_mode != "any"))
        has_user_text = bool(query_vec is not None and query_vec.getnnz() > 0) or candidate_embedding is not None

        # Check if candidate profile is completely minimal
        is_limited_profile = not (has_user_skills or has_user_sectors or has_user_location)

        scored_items = []

        for inst in eligible:
            reasons: List[ReasonCode] = []

            # --- 1. Skill Overlap ---
            inst_skills_codes = {sk.code for sk in inst.required_skills}
            inst_skills_display = {sk.code: sk.name_en for sk in inst.required_skills}

            skill_score, skill_reasons = calculate_skill_score(
                candidate_skills=set(norm_skills),
                internship_skills=inst_skills_codes,
                internship_allows_no_skills=inst.allows_no_skills,
                idf_weights=idf_weights,
                has_user_skills=has_user_skills,
            )
            reasons.extend(skill_reasons)

            missing_skills = [
                inst_skills_display.get(code, code)
                for code in inst_skills_codes
                if code not in set(norm_skills)
            ]

            # --- 2. Sector Match ---
            sector_score: Optional[float] = None
            if has_user_sectors:
                inst_sec_code = inst.sector.code if inst.sector else ""
                if inst_sec_code in norm_sectors:
                    sector_score = 1.0
                    sec_name_en = inst.sector.name_en if inst.sector else inst_sec_code
                    sec_name_hi = inst.sector.name_hi if inst.sector else inst_sec_code
                    reasons.append(ReasonCode(
                        code="SECTOR_INTEREST",
                        params={"sector": sec_name_en},
                        text_en=f"Aligned with your sector interest in {sec_name_en}.",
                        text_hi=f"{sec_name_hi} में आपकी रुचि से मेल खाता है।"
                    ))
                else:
                    sector_score = 0.0

            # --- 3. Location Compatibility ---
            loc_score, loc_reason = self.calculate_location_score(
                candidate_state=norm_state,
                candidate_district=norm_district,
                candidate_work_mode=pref_work_mode,
                willing_to_relocate=profile.willing_to_relocate,
                internship=inst
            )
            if loc_reason:
                reasons.append(loc_reason)

            # --- 4. Text Cosine Similarity (TF-IDF + Embeddings hybrid) ---
            text_score: Optional[float] = None
            tfidf_score = None
            embedding_score = None

            # TF-IDF component
            if has_user_text and query_vec is not None and self.corpus_matrix is not None:
                c_idx = corpus_id_to_idx.get(inst.id)
                if c_idx is not None:
                    inst_vec = self.corpus_matrix[c_idx]
                    sim = cosine_similarity(query_vec, inst_vec)[0][0]
                    tfidf_score = float(max(0.0, min(1.0, sim)))

            # Embedding component (semantic similarity)
            if candidate_embedding is not None and inst.id in internship_embeddings:
                inst_emb = internship_embeddings[inst.id]
                if inst_emb is not None:
                    # Cosine similarity between normalized embeddings
                    sim = np.dot(candidate_embedding, inst_emb) / (
                        np.linalg.norm(candidate_embedding) * np.linalg.norm(inst_emb) + 1e-8
                    )
                    embedding_score = float(max(0.0, min(1.0, sim)))

            # Combine TF-IDF and embeddings (prefer embeddings when available)
            if embedding_score is not None:
                text_score = embedding_score
                if tfidf_score is not None:
                    # Blend: 70% embeddings, 30% TF-IDF for robustness
                    text_score = 0.7 * embedding_score + 0.3 * tfidf_score
            elif tfidf_score is not None:
                text_score = tfidf_score

            # --- Dynamic Weight Renormalization ---
            # Only renormalize when CANDIDATE omits an input, never because LISTING is missing data
            weights = {
                "skill": BASE_WEIGHT_SKILL if skill_score is not None else 0.0,
                "sector": BASE_WEIGHT_SECTOR if sector_score is not None else 0.0,
                "location": BASE_WEIGHT_LOCATION if loc_score is not None else 0.0,
                "text": BASE_WEIGHT_TEXT if text_score is not None else 0.0,
            }
            total_active_weight = sum(weights.values())

            if total_active_weight > 0.0:
                eff_weights = {k: v / total_active_weight for k, v in weights.items()}
                total_score = (
                    (skill_score or 0.0) * eff_weights["skill"] +
                    (sector_score or 0.0) * eff_weights["sector"] +
                    (loc_score or 0.0) * eff_weights["location"] +
                    (text_score or 0.0) * eff_weights["text"]
                )
            else:
                # Minimal fallback when zero signals are applicable
                eff_weights = {"skill": 0.0, "sector": 0.0, "location": 0.0, "text": 0.0}
                total_score = 0.0

            total_score = float(max(0.0, min(1.0, total_score)))

            # Determine match tier
            if total_score >= 0.75:
                match_tier = "strong"
            elif total_score >= 0.50:
                match_tier = "good"
            elif total_score >= 0.25:
                match_tier = "moderate"
            else:
                match_tier = "exploratory"

            if is_limited_profile and not reasons:
                reasons.append(ReasonCode(
                    code="LIMITED_PROFILE_EXPLORATION",
                    params={},
                    text_en="Eligible general opportunity suggested based on your education qualification.",
                    text_hi="आपकी शैक्षणिक योग्यता के आधार पर सुझाया गया पात्र सामान्य अवसर।"
                ))

            # Limit reasons to top 3
            reasons = reasons[:3]

            detail = InternshipDetail(
                id=inst.id,
                title=inst.title,
                organization_name=inst.organization_name,
                description=inst.description,
                sector=SectorSummary(
                    id=inst.sector.id,
                    code=inst.sector.code,
                    name_en=inst.sector.name_en,
                    name_hi=inst.sector.name_hi,
                ),
                state=inst.state,
                district=inst.district,
                work_mode=inst.work_mode,
                duration_months=inst.duration_months,
                stipend_inr=inst.stipend_inr,
                deadline=inst.deadline,
                is_active=inst.is_active,
                allows_no_skills=inst.allows_no_skills,
                is_sample=inst.is_sample,
                required_skills=[
                    SkillSummary(id=sk.id, code=sk.code, name_en=sk.name_en, name_hi=sk.name_hi)
                    for sk in inst.required_skills
                ],
                accepted_educations=[
                    EducationSummary(id=ed.id, code=ed.code, label_en=ed.label_en, label_hi=ed.label_hi)
                    for ed in inst.accepted_educations
                ]
            )

            rec_item = RecommendedInternship(
                internship=detail,
                relative_score=round(total_score, 3),
                match_tier=match_tier,
                component_scores=ComponentScores(
                    skill_score=round(skill_score, 3) if skill_score is not None else None,
                    sector_score=round(sector_score, 3) if sector_score is not None else None,
                    location_score=round(loc_score, 3) if loc_score is not None else None,
                    text_score=round(text_score, 3) if text_score is not None else None,
                ),
                effective_weights=EffectiveWeights(
                    skill_weight=round(eff_weights["skill"], 3),
                    sector_weight=round(eff_weights["sector"], 3),
                    location_weight=round(eff_weights["location"], 3),
                    text_weight=round(eff_weights["text"], 3),
                ),
                missing_skills=missing_skills,
                reasons=reasons,
                is_sample=True,
            )
            scored_items.append((total_score, inst.deadline, inst.id, rec_item))

        # Deterministic tie-breaking:
        # 1. Total score DESC (-score)
        # 2. Deadline ASC (earliest closing date first)
        # 3. ID ASC (stable sorting)
        scored_items.sort(key=lambda x: (-x[0], x[1], x[2]))

        top_results = [item[3] for item in scored_items[:limit]]

        profile_summary_en = (
            f"Evaluated {len(eligible)} eligible opportunities based on your education ({norm_education}). "
            f"Returned top {len(top_results)} relative matches."
        )
        profile_summary_hi = (
            f"आपकी शिक्षा ({norm_education}) के आधार पर {len(eligible)} पात्र अवसरों का मूल्यांकन किया गया। "
            f"शीर्ष {len(top_results)} सापेक्ष मिलान प्रस्तुत किए गए।"
        )

        return RecommendationResponse(
            results=top_results,
            total_eligible=len(eligible),
            has_limited_profile=is_limited_profile,
            profile_summary_en=profile_summary_en,
            profile_summary_hi=profile_summary_hi
        )


recommender = RecommenderEngine()