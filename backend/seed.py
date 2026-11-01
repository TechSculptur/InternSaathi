import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import engine, SessionLocal
from app.database import Base
from app.models import EducationCategory
from app.models import Sector
from app.models import Skill
from app.models import Internship

APP_DIR = Path(__file__).resolve().parent / "app"
DATA_DIR = APP_DIR / "data"

def seed_taxonomy(db: Session):
    taxonomy_file = DATA_DIR / "taxonomy.json"
    with open(taxonomy_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Education categories
    # Also ensure an explicit 'any' category is supported in the database
    educations = list(data.get("education_categories", []))
    if not any(e["code"] == "any" for e in educations):
        educations.insert(0, {
            "code": "any",
            "label_en": "Any Education / Open to All",
            "label_hi": "कोई भी शिक्षा / सभी के लिए खुला"
        })

    for item in educations:
        existing = db.query(EducationCategory).filter_by(code=item["code"]).first()
        if not existing:
            cat = EducationCategory(
                code=item["code"],
                label_en=item["label_en"],
                label_hi=item["label_hi"]
            )
            db.add(cat)
        else:
            existing.label_en = item["label_en"]
            existing.label_hi = item["label_hi"]

    # 2. Sectors
    for item in data.get("sectors", []):
        existing = db.query(Sector).filter_by(code=item["code"]).first()
        if not existing:
            sec = Sector(
                code=item["code"],
                name_en=item["name_en"],
                name_hi=item["name_hi"]
            )
            db.add(sec)
        else:
            existing.name_en = item["name_en"]
            existing.name_hi = item["name_hi"]

    db.commit()

    # 3. Skills
    for item in data.get("skills", []):
        existing = db.query(Skill).filter_by(code=item["code"]).first()
        if not existing:
            sk = Skill(
                code=item["code"],
                name_en=item["name_en"],
                name_hi=item["name_hi"],
                sector_code=item.get("sector_code")
            )
            db.add(sk)
        else:
            existing.name_en = item["name_en"]
            existing.name_hi = item["name_hi"]
            existing.sector_code = item.get("sector_code")

    db.commit()
    print("Taxonomy seeded successfully.")

def seed_internships(db: Session, refresh_deadlines: bool = False):
    internships_file = DATA_DIR / "internships.json"
    if not internships_file.exists():
        print(f"File {internships_file} not found. Generating now...")
        from app.data.generate_internships import generate
        generate()

    with open(internships_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Build lookup dicts
    all_sectors = {s.code: s for s in db.query(Sector).all()}
    all_skills = {sk.code: sk for sk in db.query(Skill).all()}
    all_educations = {ed.code: ed for ed in db.query(EducationCategory).all()}

    today = date.today()

    count_created = 0
    count_updated = 0

    for item in items:
        internship_id = item["id"]
        sec = all_sectors.get(item["sector_code"])
        if not sec:
            print(f"Warning: Sector {item['sector_code']} not found for {internship_id}")
            continue

        deadline_val = datetime.fromisoformat(item["deadline"]).date()
        if refresh_deadlines:
            # If explicit refresh requested, re-anchor active listings relative to today
            if item.get("is_active", True) and int(internship_id.split("-")[1]) < 115:
                # Add 30 to 120 days from today
                idx = int(internship_id.split("-")[1])
                deadline_val = today + timedelta(days=30 + (idx % 90))

        existing = db.query(Internship).filter_by(id=internship_id).first()
        if not existing:
            inst = Internship(
                id=internship_id,
                title=item["title"],
                organization_name=item["organization_name"],
                description=item["description"],
                sector_id=sec.id,
                state=item["state"],
                district=item["district"],
                work_mode=item["work_mode"],
                duration_months=item["duration_months"],
                stipend_inr=item["stipend_inr"],
                deadline=deadline_val,
                is_active=item.get("is_active", True),
                allows_no_skills=item.get("allows_no_skills", False),
                is_sample=True,
            )
            # Associated skills
            for sk_code in item.get("required_skills", []):
                if sk_code in all_skills:
                    inst.required_skills.append(all_skills[sk_code])

            # Associated educations
            for ed_code in item.get("accepted_educations", []):
                if ed_code in all_educations:
                    inst.accepted_educations.append(all_educations[ed_code])

            db.add(inst)
            count_created += 1
        else:
            existing.title = item["title"]
            existing.organization_name = item["organization_name"]
            existing.description = item["description"]
            existing.sector_id = sec.id
            existing.state = item["state"]
            existing.district = item["district"]
            existing.work_mode = item["work_mode"]
            existing.duration_months = item["duration_months"]
            existing.stipend_inr = item["stipend_inr"]
            existing.deadline = deadline_val
            existing.is_active = item.get("is_active", True)
            existing.allows_no_skills = item.get("allows_no_skills", False)
            existing.is_sample = True

            # Sync skills
            new_skills = [all_skills[sk] for sk in item.get("required_skills", []) if sk in all_skills]
            existing.required_skills = new_skills

            # Sync educations
            new_eds = [all_educations[ed] for ed in item.get("accepted_educations", []) if ed in all_educations]
            existing.accepted_educations = new_eds

            count_updated += 1

    db.commit()
    print(f"Internships seeded: {count_created} created, {count_updated} updated (total {len(items)}).")

def main():
    refresh_deadlines = "--refresh-deadlines" in sys.argv
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_taxonomy(db)
        seed_internships(db, refresh_deadlines=refresh_deadlines)
    finally:
        db.close()

if __name__ == "__main__":
    main()
