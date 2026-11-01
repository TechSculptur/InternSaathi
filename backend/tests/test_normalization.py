from app.services.normalization import (
    normalize_education,
    normalize_skill,
    normalize_skills,
    normalize_sectors,
    clean_text,
)

def test_normalize_education_aliases():
    assert normalize_education("10th") == "tenth_pass"
    assert normalize_education("10th pass") == "tenth_pass"
    assert normalize_education("Matriculation") == "tenth_pass"
    assert normalize_education("12th") == "twelfth_pass"
    assert normalize_education("Intermediate") == "twelfth_pass"
    assert normalize_education("B.Tech") == "bachelors"
    assert normalize_education("Bachelors") == "bachelors"
    assert normalize_education("Post Graduation") == "masters"
    assert normalize_education("unknown_degree_xyz") is None
    assert normalize_education("") is None

def test_normalize_skills_and_deduplication():
    raw_skills = ["Python", "python programming", "MS Excel", "excel", "react.js", "React"]
    normalized = normalize_skills(raw_skills)
    assert "python" in normalized
    assert "ms_excel" in normalized
    assert "react" in normalized
    # Assert deduplication
    assert len(normalized) == len(set(normalized))

def test_normalize_sectors():
    raw_sectors = ["it_software", "IT Software", "it_software"]
    normalized = normalize_sectors(raw_sectors)
    assert len(normalized) == 1
    assert normalized[0] == "it_software"

def test_clean_text():
    assert clean_text("  Hello   World_Test-123  ") == "hello world test 123"
