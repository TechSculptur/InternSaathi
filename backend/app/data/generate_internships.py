import json
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Deterministic seed reference date: 2026-09-01
REF_DATE = date(2026, 9, 1)

SECTORS = [
    "it_software", "agriculture", "healthcare", "banking_finance",
    "retail_logistics", "manufacturing_automotive", "renewable_energy",
    "tourism_hospitality", "handicrafts_textiles", "education_skilling"
]

SECTOR_TITLES = {
    "it_software": [
        ("Junior Web Development Intern", "Frontend Support & Web Page Assistant", ["javascript", "communication_skills"], ["diploma", "bachelors"], 6, 8500),
        ("Data Entry & Digitization Trainee", "Digital Records & Clerical Assistant", ["data_entry", "ms_excel"], ["tenth_pass", "twelfth_pass", "diploma", "bachelors"], 3, 6000),
        ("Python Scripting & Automation Intern", "Automation & Basic Data Operations Assistant", ["python", "ms_excel"], ["diploma", "bachelors"], 6, 9000),
        ("Customer Support & Helpdesk Trainee", "Helpdesk Support & Candidate Assistance", ["customer_support", "communication_skills"], ["twelfth_pass", "diploma", "bachelors"], 4, 7000),
        ("Social Media & Community Intern", "Community Outreaches & Graphic Content Help", ["social_media_marketing", "communication_skills"], ["twelfth_pass", "bachelors"], 3, 6500),
        ("IT Hardware & Lab Support Assistant", "Computer Lab Maintenance & Networking Support", ["communication_skills"], ["iti", "diploma"], 6, 7500),
    ],
    "agriculture": [
        ("Organic Farming Field Assistant", "Assisting demonstration plots and compost management", ["organic_farming"], ["tenth_pass", "twelfth_pass", "iti"], 4, 6000),
        ("Agritech Crop Monitoring Trainee", "Soil testing and smartphone-based crop health monitoring", ["crop_monitoring", "data_entry"], ["twelfth_pass", "diploma", "bachelors"], 6, 7500),
        ("Dairy Farm Operations Trainee", "Livestock record keeping and milk testing support", ["dairy_management"], ["tenth_pass", "twelfth_pass", "iti"], 5, 6500),
        ("Horticulture & Nursery Assistant", "Plant propagation, sapling tagging and nursery maintenance", ["organic_farming"], ["tenth_pass", "twelfth_pass"], 4, 5500),
    ],
    "healthcare": [
        ("Patient Care & Desk Assistant", "Patient queue coordination and clinic reception", ["basic_nursing_care", "communication_skills"], ["twelfth_pass", "diploma"], 6, 7500),
        ("Pharmacy Dispensing Assistant", "Stock organizing and billing counter support", ["pharmacy_assistance", "data_entry"], ["twelfth_pass", "diploma"], 6, 8000),
        ("Rural Health Camp Coordinator", "Community survey and camp logistical support", ["communication_skills"], ["tenth_pass", "twelfth_pass", "bachelors"], 3, 6000),
        ("Diagnostic Lab Sample Helper", "Sample receiving and digital report printing", ["lab_testing_assistance", "ms_excel"], ["diploma", "bachelors"], 6, 8500),
    ],
    "banking_finance": [
        ("Accounting & Bookkeeping Trainee", "Voucher entry and daily ledger maintenance", ["tally_accounting", "ms_excel"], ["twelfth_pass", "bachelors"], 6, 8500),
        ("GST & Invoicing Assistant", "Tax invoice verification and compliance documentation", ["gst_filing", "tally_accounting"], ["bachelors", "masters"], 6, 9000),
        ("Microfinance Field Coordinator", "SHG meeting records and collection log support", ["communication_skills", "ms_excel"], ["twelfth_pass", "diploma", "bachelors"], 6, 7500),
        ("Branch Banking Support Assistant", "Form filling assistance and customer queue guidance", ["communication_skills", "banking_operations"], ["twelfth_pass", "bachelors"], 4, 7000),
    ],
    "retail_logistics": [
        ("Warehouse Inventory Trainee", "Barcode scanning and dispatch parcel verification", ["inventory_management", "data_entry"], ["tenth_pass", "twelfth_pass", "iti"], 6, 7000),
        ("Dispatch & Logistics Assistant", "Delivery route planning and vehicle dispatch logs", ["delivery_coordination", "ms_excel"], ["twelfth_pass", "diploma"], 4, 7500),
        ("Retail Store Display & Sales Intern", "Merchandise arrangement and billing assistance", ["retail_sales", "communication_skills"], ["tenth_pass", "twelfth_pass"], 3, 6500),
        ("E-Commerce Fulfillment Helper", "Order packaging and stock replenishing assistant", ["inventory_management"], ["tenth_pass", "twelfth_pass"], 6, 7000),
    ],
    "manufacturing_automotive": [
        ("Electrical Maintenance Apprentice", "Panel wiring and workshop equipment checks", ["electrical_wiring"], ["iti", "diploma"], 6, 8500),
        ("Welding & Fabrication Trainee", "Structural fabrication and workshop safety practices", ["arc_welding"], ["iti"], 6, 8000),
        ("CNC Machine Helper", "Raw material loading and basic dimension measurement", ["cnc_machine_operation"], ["iti", "diploma"], 6, 9000),
        ("Quality Control Junior Inspector", "Component checking and log sheet maintenance", ["ms_excel"], ["diploma", "bachelors"], 6, 8500),
    ],
    "renewable_energy": [
        ("Solar Rooftop Installation Trainee", "Panel mounting and inverter cable laying support", ["solar_panel_installation", "electrical_wiring"], ["iti", "diploma"], 6, 9000),
        ("Solar Site Survey Assistant", "Measuring rooftop dimensions and shading report logs", ["solar_panel_installation", "ms_excel"], ["diploma", "bachelors"], 4, 8500),
        ("Inverter Maintenance Assistant", "Routine battery checkup and solar inverter cleaning", ["inverter_maintenance", "electrical_wiring"], ["iti"], 6, 8000),
    ],
    "tourism_hospitality": [
        ("Front Office & Guest Desk Intern", "Guest welcoming, check-in registration and inquiries", ["front_desk_reception", "communication_skills"], ["twelfth_pass", "diploma", "bachelors"], 4, 7000),
        ("Food & Beverage Service Trainee", "Dining room preparation and banquet service help", ["food_and_beverage"], ["tenth_pass", "twelfth_pass"], 6, 6500),
        ("Heritage Tourism & Guide Intern", "Tourist information desk and heritage walk assistance", ["tour_guiding", "communication_skills"], ["twelfth_pass", "bachelors"], 3, 6000),
    ],
    "handicrafts_textiles": [
        ("Garment Tailoring & Stitching Trainee", "Fabric cutting and industrial sewing machine operations", ["garment_tailoring"], ["tenth_pass", "twelfth_pass", "iti"], 6, 6500),
        ("Handloom Weaving Support Assistant", "Yarn preparation, loom setting and quality inspection", ["handloom_weaving"], ["tenth_pass", "twelfth_pass"], 6, 6000),
        ("Textile Quality & Packaging Assistant", "Fabric defect tagging and export carton packaging", ["inventory_management"], ["tenth_pass", "twelfth_pass"], 4, 6000),
    ],
    "education_skilling": [
        ("Community Digital Literacy Trainer", "Teaching basic smartphone and computer skills to seniors", ["digital_literacy_trainer", "communication_skills"], ["twelfth_pass", "diploma", "bachelors"], 6, 7500),
        ("Primary Learning Center Assistant", "Remedial reading and activity class coordination", ["teaching_assistance", "communication_skills"], ["twelfth_pass", "bachelors"], 6, 7000),
        ("Vocational Workshop Mobilizer", "Community awareness meetings and batch enrollment logs", ["communication_skills", "ms_excel"], ["twelfth_pass", "diploma", "bachelors"], 4, 6500),
    ]
}

ORG_PREFIXES = [
    "Pragati", "Gramin", "Kisan", "Udaan", "Jan Seva", "Bharat", "Navodaya",
    "Sahayog", "Vikas", "Sankalp", "Samriddhi", "Atmanirbhar", "Shramik", "Panchayat"
]
ORG_TYPES = [
    "Digital Labs", "Agri Services", "Solar Energy Trust", "Rural Health Care",
    "Supply Chain Network", "Textile Guild", "Skills Foundation", "Hospitality Group",
    "Tech Innovations", "Automotive Solutions", "Handloom Co-op", "Finance Bureau"
]

LOCATIONS = [
    ("Maharashtra", "Mumbai"), ("Maharashtra", "Pune"), ("Maharashtra", "Nagpur"), ("Maharashtra", "Nashik"),
    ("Uttar Pradesh", "Lucknow"), ("Uttar Pradesh", "Varanasi"), ("Uttar Pradesh", "Kanpur"), ("Uttar Pradesh", "Noida"),
    ("Karnataka", "Bengaluru"), ("Karnataka", "Mysuru"), ("Karnataka", "Hubballi"), ("Karnataka", "Mangaluru"),
    ("Odisha", "Bhubaneswar"), ("Odisha", "Cuttack"), ("Odisha", "Rourkela"), ("Odisha", "Puri"),
    ("Delhi", "New Delhi"), ("Delhi", "North Delhi"), ("Delhi", "South Delhi"),
    ("Tamil Nadu", "Chennai"), ("Tamil Nadu", "Coimbatore"), ("Tamil Nadu", "Madurai"),
    ("Gujarat", "Ahmedabad"), ("Gujarat", "Surat"), ("Gujarat", "Vadodara"),
    ("Bihar", "Patna"), ("Bihar", "Gaya"), ("Bihar", "Muzaffarpur"),
    ("Madhya Pradesh", "Bhopal"), ("Madhya Pradesh", "Indore"), ("Madhya Pradesh", "Jabalpur"),
    ("West Bengal", "Kolkata"), ("West Bengal", "Howrah"), ("West Bengal", "Siliguri")
]

WORK_MODES = ["onsite", "onsite", "hybrid", "remote"]

def generate():
    items = []
    int_id = 1

    # Loop through combinations to build 120 diverse records
    for i in range(120):
        code_id = f"INT-{int_id:03d}"
        sector = SECTORS[i % len(SECTORS)]
        title_options = SECTOR_TITLES[sector]
        title_info = title_options[(i // len(SECTORS)) % len(title_options)]
        title, desc_summary, skills, educations, duration, stipend = title_info

        state, district = LOCATIONS[i % len(LOCATIONS)]
        
        # Determine work mode
        if i % 7 == 0:
            mode = "remote"
        elif i % 5 == 0:
            mode = "hybrid"
        else:
            mode = "onsite"

        # Synthetic organization name
        org_p = ORG_PREFIXES[(i + 3) % len(ORG_PREFIXES)]
        org_t = ORG_TYPES[(i + 5) % len(ORG_TYPES)]
        org_name = f"{org_p} {org_t}"

        # Some listings have no listed skills required
        allows_no_skills = (i % 6 == 0)
        req_skills = [] if allows_no_skills else list(skills)

        # Some accept any education
        if i % 8 == 0:
            req_educations = ["any"]
        else:
            req_educations = list(educations)

        # Test cases for expired and inactive items (stable)
        # INT-115 to INT-118 are expired (past deadline)
        # INT-119 and INT-120 are inactive (is_active=False)
        if int_id in [115, 116, 117, 118]:
            deadline = REF_DATE - timedelta(days=15 + (int_id - 115) * 5)
            is_active = True
        elif int_id in [119, 120]:
            deadline = REF_DATE + timedelta(days=30)
            is_active = False
        else:
            # Active items: deadlines between 30 and 120 days in future
            deadline = REF_DATE + timedelta(days=30 + (i % 90))
            is_active = True

        description = (
            f"{desc_summary}. This 100% synthetic demonstration internship is organized by {org_name} "
            f"located at {district}, {state}. Interns will gain practical on-the-ground experience, "
            f"mentorship from industry supervisors, and a monthly stipend of INR {stipend:,}. "
            f"Demonstration prototype. Sample internships only. Not an official government portal."
        )

        item = {
            "id": code_id,
            "title": title,
            "organization_name": org_name,
            "description": description,
            "sector_code": sector,
            "state": state,
            "district": district,
            "work_mode": mode,
            "duration_months": duration,
            "stipend_inr": stipend,
            "deadline": deadline.isoformat(),
            "is_active": is_active,
            "allows_no_skills": allows_no_skills,
            "is_sample": True,
            "required_skills": req_skills,
            "accepted_educations": req_educations
        }
        items.append(item)
        int_id += 1

    # Additional synthetic technical roles (IDs continue from INT-121; original 120 IDs stay stable)
    tech_templates = [
        (
            "Data Scientist Intern",
            "Build exploratory analyses, feature pipelines, and baseline models using Python.",
            ["python", "statistics", "pandas", "machine_learning", "sql"],
            ["bachelors", "masters"],
            6,
            12000,
        ),
        (
            "Data Analyst Intern",
            "Clean datasets, write SQL queries, and produce dashboards for programme monitoring.",
            ["python", "sql", "pandas", "data_visualization", "ms_excel", "statistics"],
            ["twelfth_pass", "diploma", "bachelors"],
            6,
            10000,
        ),
        (
            "Software Development Engineer (SDE) Intern",
            "Implement product features, write unit tests, and participate in code reviews.",
            ["python", "java", "git", "rest_apis", "sql"],
            ["diploma", "bachelors"],
            6,
            12500,
        ),
        (
            "Machine Learning Intern",
            "Train and evaluate classical ML models and document experiment results.",
            ["python", "machine_learning", "numpy", "pandas", "statistics"],
            ["bachelors", "masters"],
            6,
            12000,
        ),
        (
            "Backend Developer (Python/FastAPI) Intern",
            "Design REST endpoints with FastAPI, persist data with SQL, and write API tests.",
            ["python", "fastapi", "rest_apis", "sql", "git", "docker"],
            ["diploma", "bachelors"],
            6,
            11500,
        ),
        (
            "Frontend Developer (React) Intern",
            "Build accessible React interfaces with TypeScript, HTML, and CSS.",
            ["react", "typescript", "javascript", "html_css", "git"],
            ["diploma", "bachelors"],
            6,
            11000,
        ),
        (
            "DevOps Intern",
            "Containerize services, maintain CI/CD pipelines, and assist with Linux operations.",
            ["docker", "git", "linux", "ci_cd", "kubernetes"],
            ["diploma", "bachelors"],
            6,
            11500,
        ),
        (
            "QA/Test Automation Intern",
            "Author automated UI and API tests using Python, Selenium, and CI pipelines.",
            ["test_automation", "python", "selenium", "git", "ci_cd"],
            ["twelfth_pass", "diploma", "bachelors"],
            4,
            9000,
        ),
        (
            "Business Intelligence Intern",
            "Model reporting datasets and publish Power BI / visualization dashboards.",
            ["sql", "data_visualization", "power_bi", "ms_excel", "statistics"],
            ["bachelors", "masters"],
            6,
            10500,
        ),
        (
            "Cloud Engineering Intern",
            "Help provision AWS environments, Docker images, and basic Linux networking.",
            ["aws", "linux", "docker", "git", "ci_cd"],
            ["diploma", "bachelors"],
            6,
            11500,
        ),
        # Additional 15 internships to reach 25+ total technical roles
        (
            "Data Engineer Intern",
            "Build and maintain data pipelines, ETL processes, and data quality checks.",
            ["python", "sql", "pandas", "rest_apis", "docker"],
            ["bachelors", "masters"],
            6,
            11000,
        ),
        (
            "MLOps Intern",
            "Automate ML model deployment, monitoring, and retraining pipelines.",
            ["python", "machine_learning", "docker", "ci_cd", "kubernetes", "git"],
            ["bachelors", "masters"],
            6,
            12000,
        ),
        (
            "Full Stack Developer Intern",
            "Develop end-to-end features across frontend (React) and backend (FastAPI).",
            ["react", "typescript", "python", "fastapi", "rest_apis", "sql", "git"],
            ["diploma", "bachelors"],
            6,
            12000,
        ),
        (
            "Data Visualization Intern",
            "Create interactive dashboards and visual analytics for business insights.",
            ["data_visualization", "power_bi", "sql", "python", "statistics"],
            ["twelfth_pass", "diploma", "bachelors"],
            4,
            9500,
        ),
        (
            "Site Reliability Engineering (SRE) Intern",
            "Monitor system health, automate incident response, and improve reliability.",
            ["linux", "docker", "kubernetes", "ci_cd", "python", "aws"],
            ["diploma", "bachelors"],
            6,
            11500,
        ),
        (
            "AI Research Intern",
            "Assist with literature review, experiment design, and model prototyping.",
            ["python", "machine_learning", "pandas", "numpy", "statistics", "git"],
            ["bachelors", "masters"],
            6,
            12500,
        ),
        (
            "Mobile App Developer (React Native) Intern",
            "Build cross-platform mobile applications with React Native and TypeScript.",
            ["react", "typescript", "javascript", "git", "rest_apis"],
            ["diploma", "bachelors"],
            6,
            11000,
        ),
        (
            "Security Engineering Intern",
            "Support vulnerability scanning, secure code review, and compliance checks.",
            ["python", "linux", "git", "ci_cd", "rest_apis"],
            ["diploma", "bachelors"],
            6,
            11000,
        ),
        (
            "Database Administration Intern",
            "Assist with query optimization, backup strategies, and schema migrations.",
            ["sql", "python", "linux", "docker"],
            ["diploma", "bachelors"],
            6,
            10000,
        ),
        (
            "API Integration Intern",
            "Design and implement third-party API integrations and webhook handlers.",
            ["rest_apis", "python", "fastapi", "git", "docker"],
            ["diploma", "bachelors"],
            4,
            10000,
        ),
        (
            "NLP Intern",
            "Process text data, build language models, and evaluate NLP pipelines.",
            ["python", "machine_learning", "pandas", "numpy", "statistics"],
            ["bachelors", "masters"],
            6,
            12000,
        ),
        (
            "Computer Vision Intern",
            "Develop image processing pipelines and train vision models.",
            ["python", "machine_learning", "numpy", "pandas", "statistics"],
            ["bachelors", "masters"],
            6,
            12000,
        ),
        (
            "Data Quality Intern",
            "Implement data validation rules, profiling, and anomaly detection.",
            ["python", "sql", "pandas", "statistics", "data_visualization"],
            ["twelfth_pass", "diploma", "bachelors"],
            4,
            9000,
        ),
        (
            "Backend Developer (Java/Spring) Intern",
            "Build RESTful services with Spring Boot, JPA, and PostgreSQL.",
            ["java", "rest_apis", "sql", "git", "docker", "ci_cd"],
            ["diploma", "bachelors"],
            6,
            11500,
        ),
        (
            "Frontend Developer (Vue.js) Intern",
            "Create reactive user interfaces with Vue 3, TypeScript, and Pinia.",
            ["javascript", "typescript", "html_css", "git", "rest_apis"],
            ["diploma", "bachelors"],
            6,
            10500,
        ),
        (
            "Platform Engineering Intern",
            "Build developer tooling, internal platforms, and self-service infrastructure.",
            ["docker", "kubernetes", "ci_cd", "python", "git", "linux"],
            ["diploma", "bachelors"],
            6,
            12000,
        ),
    ]
    tech_title_variants = [
        "{title}",
        "Junior {title}",
        "Associate {title}",
    ]
    tech_locations = [
        ("Karnataka", "Bengaluru"),
        ("Maharashtra", "Pune"),
        ("Delhi", "New Delhi"),
        ("Tamil Nadu", "Chennai"),
        ("Uttar Pradesh", "Noida"),
        ("Gujarat", "Ahmedabad"),
        ("West Bengal", "Kolkata"),
        ("Odisha", "Bhubaneswar"),
        ("Madhya Pradesh", "Indore"),
        ("Bihar", "Patna"),
    ]
    tech_modes = ["onsite", "hybrid", "remote"]

    for j in range(30):
        code_id = f"INT-{int_id:03d}"
        title, desc_summary, skills, educations, duration, stipend = tech_templates[j % len(tech_templates)]
        variant = tech_title_variants[(j // len(tech_templates)) % len(tech_title_variants)]
        display_title = variant.format(title=title)
        state, district = tech_locations[j % len(tech_locations)]
        mode = tech_modes[j % len(tech_modes)]
        org_p = ORG_PREFIXES[(j + 7) % len(ORG_PREFIXES)]
        org_t = ORG_TYPES[(j + 2) % len(ORG_TYPES)]
        org_name = f"{org_p} {org_t}"
        deadline = REF_DATE + timedelta(days=40 + (j % 80))
        description = (
            f"{desc_summary} This 100% synthetic demonstration internship is organized by {org_name} "
            f"located at {district}, {state}. Interns will gain practical on-the-ground experience, "
            f"mentorship from industry supervisors, and a monthly stipend of INR {stipend:,}. "
            f"Demonstration prototype. Sample internships only. Not an official government portal."
        )
        items.append({
            "id": code_id,
            "title": display_title,
            "organization_name": org_name,
            "description": description,
            "sector_code": "it_software",
            "state": state,
            "district": district,
            "work_mode": mode,
            "duration_months": duration,
            "stipend_inr": stipend,
            "deadline": deadline.isoformat(),
            "is_active": True,
            "allows_no_skills": False,
            "is_sample": True,
            "required_skills": list(skills),
            "accepted_educations": list(educations),
        })
        int_id += 1

    out_file = BASE_DIR / "internships.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(items)} synthetic internships to {out_file}")

if __name__ == "__main__":
    generate()
