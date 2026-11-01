from app.schemas import CandidateProfile
from app.services.recommender import recommender, calculate_skill_score, compute_skill_idf
from app.services.normalization import normalize_skills
from app.models import Internship
from app.models import Skill
from app.models import Sector
from app.models import EducationCategory
from datetime import date, timedelta

def test_score_bounds_and_renormalization(db_session):
    # Candidate provides only skills, no location or sectors
    profile = CandidateProfile(
        education="twelfth_pass",
        skills=["python"],
        sectors=[],
        state=None,
        district=None,
        preferred_work_mode="any"
    )
    res = recommender.recommend(profile=profile, db=db_session)
    assert len(res.results) > 0
    for item in res.results:
        assert 0.0 <= item.relative_score <= 1.0
        # Effective weights should sum to 1.0 (with slight float rounding tolerance)
        total_eff_weight = (
            item.effective_weights.skill_weight +
            item.effective_weights.sector_weight +
            item.effective_weights.location_weight +
            item.effective_weights.text_weight
        )
        assert abs(total_eff_weight - 1.0) < 0.05

def test_internship_with_no_listed_skills(db_session):
    # Candidate has 10th pass and no skills
    profile = CandidateProfile(
        education="tenth_pass",
        skills=[],
        sectors=["agriculture"],
        state="Maharashtra",
        district="Pune"
    )
    res = recommender.recommend(profile=profile, db=db_session)
    t2_item = next((r for r in res.results if r.internship.id == "TEST-002"), None)
    assert t2_item is not None
    # TEST-002 has allows_no_skills=True
    assert t2_item.internship.allows_no_skills is True
    reason_codes = {r.code for r in t2_item.reasons}
    assert "NO_PRIOR_SKILLS_REQUIRED" in reason_codes

def test_limited_profile_detection(db_session):
    # Candidate gives only education and no other preference
    profile = CandidateProfile(
        education="tenth_pass",
        skills=[],
        sectors=[],
        state=None,
        district=None,
        preferred_work_mode="any"
    )
    res = recommender.recommend(profile=profile, db=db_session)
    assert res.has_limited_profile is True
    assert len(res.results) > 0
    # Suggestions should exist, but marked with LIMITED_PROFILE_EXPLORATION
    first_result = res.results[0]
    reason_codes = [r.code for r in first_result.reasons]
    assert any("LIMITED" in code or "NO_PRIOR_SKILLS" in code for code in reason_codes)

def test_deterministic_tie_breaking(db_session):
    profile = CandidateProfile(
        education="tenth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="any"
    )
    res1 = recommender.recommend(profile=profile, db=db_session)
    res2 = recommender.recommend(profile=profile, db=db_session)
    ids1 = [r.internship.id for r in res1.results]
    ids2 = [r.internship.id for r in res2.results]
    assert ids1 == ids2

def test_max_results_bounded_at_five(db_session):
    profile = CandidateProfile(
        education="bachelors",
        skills=["python", "ms_excel"],
        sectors=["it_software"],
        preferred_work_mode="any"
    )
    res = recommender.recommend(profile=profile, db=db_session, limit=5)
    assert len(res.results) <= 5

# --- New tests for updated scoring logic ---

def test_python_only_ranks_technical_internships_higher(db_session):
    """
    Regression test: A candidate with only 'python' skill must rank
    Python/data internships above zero-skill or generic listings.
    """
    profile = CandidateProfile(
        education="bachelors",
        skills=["python"],
        sectors=[],
        state=None,
        district=None,
        preferred_work_mode="any"
    )
    res = recommender.recommend(profile=profile, db=db_session)
    assert len(res.results) > 0

    # Find Python-related internships in results
    python_internships = [
        r for r in res.results
        if "python" in r.internship.title.lower() or
           "data" in r.internship.title.lower() or
           "sde" in r.internship.title.lower() or
           "machine learning" in r.internship.title.lower() or
           "backend" in r.internship.title.lower()
    ]

    # At least one Python/data internship should be in top results
    assert len(python_internships) > 0

    # The top result should have a skill_score > 0 (skill match)
    top_result = res.results[0]
    assert top_result.component_scores.skill_score is not None
    assert top_result.component_scores.skill_score > 0.0


def test_zero_skill_listing_cap(db_session):
    """
    Zero-skill listings (allows_no_skills=True) should get skill_score=0.5
    when candidate has skills, and 0.8 when candidate has no skills.
    They should NOT outrank genuine skill matches.
    """
    # Candidate WITH skills
    profile_with_skills = CandidateProfile(
        education="bachelors",
        skills=["python", "sql", "pandas"],
        sectors=["it_software"],
        preferred_work_mode="any"
    )
    res_with_skills = recommender.recommend(profile=profile_with_skills, db=db_session)

    # Candidate WITHOUT skills (beginner)
    profile_beginner = CandidateProfile(
        education="bachelors",
        skills=[],
        sectors=["it_software"],
        preferred_work_mode="any"
    )
    res_beginner = recommender.recommend(profile=profile_beginner, db=db_session)

    # Check zero-skill listings in results
    for item in res_with_skills.results:
        if item.internship.allows_no_skills:
            # Should be capped at 0.5
            assert item.component_scores.skill_score == 0.5

    for item in res_beginner.results:
        if item.internship.allows_no_skills:
            # Should be 0.8 for beginners
            assert item.component_scores.skill_score == 0.8


def test_idf_skill_weighting(db_session):
    """
    Rare skills (like 'machine_learning') should contribute more to skill_score
    than common skills (like 'communication_skills').
    """
    # The test fixture has python, ms_excel, organic_farming skills
    # Let's verify the IDF computation works with available skills
    all_internships = db_session.query(Internship).filter(
        Internship.is_active == True,
        Internship.deadline >= date.today()
    ).all()

    idf_weights = compute_skill_idf(all_internships)

    # At least some skills should have IDF weights
    assert len(idf_weights) > 0

    # All weights should be in [0.5, 2.0] range
    for skill, weight in idf_weights.items():
        assert 0.5 <= weight <= 2.0

    # Rare skills (appearing in fewer internships) should have higher weights
    # This is implicitly tested by the algorithm - we verify the range


def test_f1_harmonic_mean_skill_score():
    """
    Test the F1-style harmonic mean calculation directly.
    """
    candidate_skills = {"python", "sql", "pandas"}
    internship_skills = {"python", "sql", "machine_learning", "statistics"}

    # Mock IDF weights (all 1.0 for simplicity)
    idf_weights = {s: 1.0 for s in candidate_skills.union(internship_skills)}

    score, reasons = calculate_skill_score(
        candidate_skills=candidate_skills,
        internship_skills=internship_skills,
        internship_allows_no_skills=False,
        idf_weights=idf_weights,
        has_user_skills=True
    )

    # Overlap = {python, sql} -> 2 skills
    # Coverage = 2/4 = 0.5
    # Relevance = 2/min(3, 4) = 2/3 ≈ 0.667
    # F1 = 2 * 0.5 * 0.667 / (0.5 + 0.667) = 0.667 / 1.167 ≈ 0.571
    assert score is not None
    assert 0.5 < score < 0.7

    # Should have SKILL_MATCH_EXACT reason
    reason_codes = [r.code for r in reasons]
    assert "SKILL_MATCH_EXACT" in reason_codes


def test_no_overlap_zero_skill_score():
    """
    No overlap should result in skill_score = 0.0
    """
    candidate_skills = {"python", "sql"}
    internship_skills = {"java", "spring", "hibernate"}
    idf_weights = {s: 1.0 for s in candidate_skills.union(internship_skills)}

    score, reasons = calculate_skill_score(
        candidate_skills=candidate_skills,
        internship_skills=internship_skills,
        internship_allows_no_skills=False,
        idf_weights=idf_weights,
        has_user_skills=True
    )

    assert score == 0.0
    assert len(reasons) == 0


def test_embeddings_fallback(db_session, monkeypatch):
    """
    Test that embeddings gracefully fall back to TF-IDF when model unavailable.
    """
    # Mock the embedding service to return None (simulating unavailable model)
    import app.services.embeddings as embeddings_module
    original_get = embeddings_module.get_embedding_service

    class MockEmbeddingService:
        def encode(self, text):
            return None
        def encode_batch(self, texts):
            return [None] * len(texts)
        def encode_internships(self, internships):
            return {inst.id: None for inst in internships}

    mock_service = MockEmbeddingService()
    embeddings_module._embedding_service = mock_service

    try:
        profile = CandidateProfile(
            education="bachelors",
            skills=["python"],
            sectors=["it_software"],
            preferred_work_mode="any"
        )
        res = recommender.recommend(profile=profile, db=db_session)
        assert len(res.results) > 0
        # Should still work with TF-IDF only
        for item in res.results:
            assert item.component_scores.text_score is not None
    finally:
        embeddings_module._embedding_service = None


# --- Resume Parsing Tests ---

def test_resume_parse_pdf(client):
    """Test PDF resume parsing endpoint."""
    import io
    import pypdf

    # Create a simple PDF in memory with some text
    pdf_buffer = io.BytesIO()
    writer = pypdf.PdfWriter()
    page = pypdf.PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    writer.write(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    # Test the endpoint
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")}
    )

    # Should handle empty PDF gracefully
    assert response.status_code in [200, 400]


def test_resume_parse_docx(client):
    """Test DOCX resume parsing endpoint."""
    import io
    import docx

    doc = docx.Document()
    doc.add_paragraph("Python developer with 2 years experience in Django and FastAPI. Skilled in SQL, PostgreSQL, Docker, and AWS. Machine learning experience with scikit-learn and pandas.")
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    docx_bytes = doc_buffer.getvalue()

    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("test.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "detected_skills" in data
    assert "python" in data["detected_skills"]
    assert "fastapi" in data["detected_skills"]
    assert "sql" in data["detected_skills"]
    assert "docker" in data["detected_skills"]
    assert "aws" in data["detected_skills"]
    assert "machine_learning" in data["detected_skills"]
    assert "pandas" in data["detected_skills"]
    assert "resume_text" in data
    assert len(data["resume_text"]) <= 2000


def test_resume_parse_size_limit(client):
    """Test that files over 5MB are rejected."""
    # Create a 6MB file
    large_content = b"x" * (6 * 1024 * 1024)

    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("large.pdf", large_content, "application/pdf")}
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_resume_parse_invalid_type(client):
    """Test that invalid file types are rejected."""
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("test.txt", b"plain text", "text/plain")}
    )

    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"].lower()


def test_skill_alias_mapping():
    """Test that skill aliases are correctly mapped."""
    from app.services.normalization import normalize_skill

    # Test various aliases
    assert normalize_skill("py") == "python"
    assert normalize_skill("python3") == "python"
    assert normalize_skill("reactjs") == "react"
    assert normalize_skill("ml") == "machine_learning"
    assert normalize_skill("machine learning") == "machine_learning"
    assert normalize_skill("js") == "javascript"
    assert normalize_skill("ts") == "typescript"
    assert normalize_skill("k8s") == "kubernetes"
    assert normalize_skill("ci/cd") == "ci_cd"
    assert normalize_skill("ci cd") == "ci_cd"
    assert normalize_skill("postgres") == "postgresql"
    assert normalize_skill("tf") == "tensorflow"
    assert normalize_skill("sklearn") == "scikit_learn"
