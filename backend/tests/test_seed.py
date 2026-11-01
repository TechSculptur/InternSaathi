import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Internship
from app.models import EducationCategory
from app.models import Sector
from app.models import Skill
from seed import seed_taxonomy, seed_internships

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from seed import seed_taxonomy, seed_internships

@pytest.fixture
def clean_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_seed_idempotency(clean_db: Session):
    # Run seed_taxonomy and seed_internships first time
    seed_taxonomy(clean_db)
    seed_internships(clean_db)

    count_internships_1 = clean_db.query(Internship).count()
    count_sectors_1 = clean_db.query(Sector).count()
    count_skills_1 = clean_db.query(Skill).count()

    assert count_internships_1 == 150
    assert count_sectors_1 >= 10
    assert count_skills_1 >= 40

    # Run seed second time
    seed_taxonomy(clean_db)
    seed_internships(clean_db)

    count_internships_2 = clean_db.query(Internship).count()
    count_sectors_2 = clean_db.query(Sector).count()
    count_skills_2 = clean_db.query(Skill).count()

    # Must be exactly identical, no duplicate rows created
    assert count_internships_1 == count_internships_2
    assert count_sectors_1 == count_sectors_2
    assert count_skills_1 == count_skills_2
