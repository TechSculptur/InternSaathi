from app.schemas import CandidateProfile
from app.services.recommender import recommender

def test_expired_and_inactive_excluded(db_session):
    profile = CandidateProfile(
        education="twelfth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="any"
    )
    res = recommender.recommend(profile=profile, db=db_session)
    rec_ids = [r.internship.id for r in res.results]
    assert "TEST-004" not in rec_ids  # Expired
    assert "TEST-005" not in rec_ids  # Inactive

def test_education_eligibility_filtering(db_session):
    # Candidate with 10th pass should be eligible for TEST-002 (10th) and TEST-003 (Any)
    profile_10th = CandidateProfile(
        education="tenth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="any"
    )
    res_10th = recommender.recommend(profile=profile_10th, db=db_session)
    ids_10th = {r.internship.id for r in res_10th.results}
    assert "TEST-002" in ids_10th
    assert "TEST-003" in ids_10th
    assert "TEST-001" not in ids_10th  # Requires 12th or bachelors

    # Candidate with 12th pass
    profile_12th = CandidateProfile(
        education="twelfth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="any"
    )
    res_12th = recommender.recommend(profile=profile_12th, db=db_session)
    ids_12th = {r.internship.id for r in res_12th.results}
    assert "TEST-001" in ids_12th
    assert "TEST-003" in ids_12th
    assert "TEST-002" not in ids_12th

def test_mandatory_work_mode_constraint(db_session):
    # Mandatory remote only
    profile_remote = CandidateProfile(
        education="twelfth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="remote",
        is_work_mode_mandatory=True
    )
    res_remote = recommender.recommend(profile=profile_remote, db=db_session)
    for r in res_remote.results:
        assert r.internship.work_mode == "remote"

    # Non-mandatory preference: should still include onsite if eligible, with lower/adjusted score
    profile_pref_remote = CandidateProfile(
        education="twelfth_pass",
        skills=[],
        sectors=[],
        preferred_work_mode="remote",
        is_work_mode_mandatory=False
    )
    res_pref = recommender.recommend(profile=profile_pref_remote, db=db_session)
    modes = {r.internship.work_mode for r in res_pref.results}
    assert "remote" in modes
    assert "onsite" in modes

def test_mandatory_location_constraint(db_session):
    # Candidate in Delhi with mandatory location constraint
    profile_delhi = CandidateProfile(
        education="twelfth_pass",
        skills=[],
        sectors=[],
        state="Delhi",
        district="New Delhi",
        is_location_mandatory=True
    )
    res_delhi = recommender.recommend(profile=profile_delhi, db=db_session)
    for r in res_delhi.results:
        # Should be located in Delhi or remote
        assert r.internship.state == "Delhi" or r.internship.work_mode == "remote"
        assert r.internship.state != "Maharashtra"
