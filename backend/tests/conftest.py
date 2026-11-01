import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.database import get_db
from app.main import app
from app.models import EducationCategory
from app.models import Sector
from app.models import Skill
from app.models import Internship

from sqlalchemy.pool import StaticPool

# In-memory SQLite with StaticPool so all connections share the same database
TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Populate basic test taxonomy
    edu_any = EducationCategory(code="any", label_en="Any", label_hi="कोई भी")
    edu_10th = EducationCategory(code="tenth_pass", label_en="10th Pass", label_hi="10वीं पास")
    edu_12th = EducationCategory(code="twelfth_pass", label_en="12th Pass", label_hi="12वीं पास")
    edu_deg = EducationCategory(code="bachelors", label_en="Bachelors", label_hi="स्नातक")
    session.add_all([edu_any, edu_10th, edu_12th, edu_deg])

    sec_it = Sector(code="it_software", name_en="IT & Software", name_hi="आईटी")
    sec_agri = Sector(code="agriculture", name_en="Agriculture", name_hi="कृषि")
    session.add_all([sec_it, sec_agri])

    sk_py = Skill(code="python", name_en="Python", name_hi="पायथन", sector_code="it_software")
    sk_excel = Skill(code="ms_excel", name_en="MS Excel", name_hi="एक्सेल", sector_code="it_software")
    sk_farm = Skill(code="organic_farming", name_en="Farming", name_hi="खेती", sector_code="agriculture")
    session.add_all([sk_py, sk_excel, sk_farm])

    session.commit()

    # Add sample internships for testing
    ref_date = date.today()

    # 1. Active IT Internship (12th and Bachelors, requires python and excel, Mumbai)
    i1 = Internship(
        id="TEST-001",
        title="Python Data Intern",
        organization_name="Test Org Alpha",
        description="Assisting python data pipelines and reporting in Mumbai office.",
        sector_id=sec_it.id,
        state="Maharashtra",
        district="Mumbai",
        work_mode="onsite",
        duration_months=6,
        stipend_inr=8000,
        deadline=ref_date + timedelta(days=60),
        is_active=True,
        allows_no_skills=False,
        is_sample=True,
    )
    i1.accepted_educations.extend([edu_12th, edu_deg])
    i1.required_skills.extend([sk_py, sk_excel])

    # 2. Active Entry Level Agri Internship (10th pass, NO skills required, Pune)
    i2 = Internship(
        id="TEST-002",
        title="Field Farming Trainee",
        organization_name="Test Org Beta",
        description="Demonstration organic farm assistant in Pune.",
        sector_id=sec_agri.id,
        state="Maharashtra",
        district="Pune",
        work_mode="onsite",
        duration_months=4,
        stipend_inr=6000,
        deadline=ref_date + timedelta(days=45),
        is_active=True,
        allows_no_skills=True,
        is_sample=True,
    )
    i2.accepted_educations.append(edu_10th)

    # 3. Active Remote IT Internship (Any education, remote, requires excel)
    i3 = Internship(
        id="TEST-003",
        title="Remote Excel Assistant",
        organization_name="Test Org Gamma",
        description="Remote spreadsheet data entry and auditing.",
        sector_id=sec_it.id,
        state="Delhi",
        district="New Delhi",
        work_mode="remote",
        duration_months=3,
        stipend_inr=7000,
        deadline=ref_date + timedelta(days=90),
        is_active=True,
        allows_no_skills=False,
        is_sample=True,
    )
    i3.accepted_educations.append(edu_any)
    i3.required_skills.append(sk_excel)

    # 4. Expired Internship (Deadline in the past)
    i4 = Internship(
        id="TEST-004",
        title="Expired IT Trainee",
        organization_name="Test Org Delta",
        description="Expired position.",
        sector_id=sec_it.id,
        state="Maharashtra",
        district="Mumbai",
        work_mode="onsite",
        duration_months=3,
        stipend_inr=5000,
        deadline=ref_date - timedelta(days=10),
        is_active=True,
        allows_no_skills=True,
        is_sample=True,
    )
    i4.accepted_educations.append(edu_12th)

    # 5. Inactive Internship (is_active = False)
    i5 = Internship(
        id="TEST-005",
        title="Inactive Agri Trainee",
        organization_name="Test Org Epsilon",
        description="Inactive position.",
        sector_id=sec_agri.id,
        state="Maharashtra",
        district="Pune",
        work_mode="onsite",
        duration_months=3,
        stipend_inr=5000,
        deadline=ref_date + timedelta(days=30),
        is_active=False,
        allows_no_skills=True,
        is_sample=True,
    )
    i5.accepted_educations.append(edu_10th)

    session.add_all([i1, i2, i3, i4, i5])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
