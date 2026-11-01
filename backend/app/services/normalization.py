import re
from typing import List, Optional, Tuple, Set

EDUCATION_ALIASES = {
    "any": "any",
    "all": "any",
    "open": "any",
    "10th": "tenth_pass",
    "10th pass": "tenth_pass",
    "matric": "tenth_pass",
    "matriculation": "tenth_pass",
    "tenth": "tenth_pass",
    "tenth_pass": "tenth_pass",
    "12th": "twelfth_pass",
    "12th pass": "twelfth_pass",
    "intermediate": "twelfth_pass",
    "inter": "twelfth_pass",
    "hsc": "twelfth_pass",
    "twelfth": "twelfth_pass",
    "twelfth_pass": "twelfth_pass",
    "iti": "iti",
    "industrial training": "iti",
    "diploma": "diploma",
    "polytechnic": "diploma",
    "bachelor": "bachelors",
    "bachelors": "bachelors",
    "graduate": "bachelors",
    "graduation": "bachelors",
    "ba": "bachelors",
    "b.a": "bachelors",
    "bcom": "bachelors",
    "b.com": "bachelors",
    "bsc": "bachelors",
    "b.sc": "bachelors",
    "btech": "bachelors",
    "b.tech": "bachelors",
    "be": "bachelors",
    "b.e": "bachelors",
    "master": "masters",
    "masters": "masters",
    "post graduate": "masters",
    "post graduation": "masters",
    "pg": "masters",
    "ma": "masters",
    "mcom": "masters",
    "msc": "masters",
    "mtech": "masters",
}

SKILL_ALIASES = {
    "py": "python",
    "python3": "python",
    "python programming": "python",
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "react native": "react",
    "excel": "ms_excel",
    "ms excel": "ms_excel",
    "microsoft excel": "ms_excel",
    "word": "ms_word",
    "ms word": "ms_word",
    "office": "ms_office",
    "communication": "communication_skills",
    "spoken english": "communication_skills",
    "data entry": "data_entry",
    "typing": "data_entry",
    "accounting": "tally_accounting",
    "tally": "tally_accounting",
    "gst": "gst_filing",
    "customer service": "customer_support",
    "customer care": "customer_support",
    "bpo": "customer_support",
    "electrician": "electrical_wiring",
    "wiring": "electrical_wiring",
    "solar": "solar_panel_installation",
    "solar installation": "solar_panel_installation",
    "welding": "arc_welding",
    "plumbing": "basic_plumbing",
    "driving": "commercial_driving",
    "inventory": "inventory_management",
    "stock": "inventory_management",
    "nursing": "basic_nursing_care",
    "patient care": "patient_assistance",
    "pharmacy": "pharmacy_assistance",
    "agriculture": "organic_farming",
    "farming": "crop_monitoring",
    "tailoring": "garment_tailoring",
    "sewing": "garment_tailoring",
    "hospitality": "front_desk_reception",
    "front desk": "front_desk_reception",
    "reception": "front_desk_reception",
    # Technical skill aliases for resume parsing
    "ml": "machine_learning",
    "machine learning": "machine_learning",
    "deep learning": "machine_learning",
    "dl": "machine_learning",
    "ai": "machine_learning",
    "artificial intelligence": "machine_learning",
    "nlp": "machine_learning",
    "natural language processing": "machine_learning",
    "computer vision": "machine_learning",
    "cv": "machine_learning",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "keras": "tensorflow",
    "sklearn": "scikit_learn",
    "scikit": "scikit_learn",
    "scikit-learn": "scikit_learn",
    "pandas": "pandas",
    "numpy": "numpy",
    "np": "numpy",
    "sql": "sql",
    "mysql": "sql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "nosql": "mongodb",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redis": "redis",
    "git": "git",
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",
    "docker": "docker",
    "container": "docker",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "kube": "kubernetes",
    "ci/cd": "ci_cd",
    "ci cd": "ci_cd",
    "cicd": "ci_cd",
    "jenkins": "ci_cd",
    "github actions": "ci_cd",
    "gitlab ci": "ci_cd",
    "linux": "linux",
    "ubuntu": "linux",
    "unix": "linux",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "aws",
    "google cloud": "aws",
    "azure": "aws",
    "fastapi": "fastapi",
    "django": "fastapi",
    "flask": "fastapi",
    "rest": "rest_apis",
    "rest api": "rest_apis",
    "restful": "rest_apis",
    "api": "rest_apis",
    "graphql": "graphql",
    "html": "html_css",
    "css": "html_css",
    "html5": "html_css",
    "css3": "html_css",
    "typescript": "typescript",
    "ts": "typescript",
    "vue": "vue",
    "vue.js": "vue",
    "vuejs": "vue",
    "nextjs": "nextjs",
    "next.js": "nextjs",
    "next": "nextjs",
    "tailwind": "tailwind",
    "tailwindcss": "tailwind",
    "terraform": "terraform",
    "ansible": "ansible",
    "prometheus": "prometheus",
    "grafana": "grafana",
    "selenium": "selenium",
    "playwright": "playwright",
    "cypress": "cypress",
    "test automation": "test_automation",
    "automation testing": "test_automation",
    "qa": "test_automation",
    "quality assurance": "test_automation",
    "junit": "junit",
    "pytest": "pytest",
    "kafka": "kafka",
    "spark": "spark",
    "airflow": "airflow",
    "etl": "sql",
    "data pipeline": "sql",
    "data engineering": "sql",
    "powerbi": "power_bi",
    "power bi": "power_bi",
    "tableau": "tableau",
    "looker": "looker",
    "visualization": "data_visualization",
    "dashboard": "data_visualization",
    "bi": "power_bi",
    "business intelligence": "power_bi",
    "statistics": "statistics",
    "stats": "statistics",
    "probability": "statistics",
    "data analysis": "data_visualization",
    "data analytics": "data_visualization",
    "frontend": "react",
    "backend": "python",
    "fullstack": "python",
    "full stack": "python",
    "devops": "docker",
    "sre": "linux",
    "site reliability": "linux",
    "mlops": "machine_learning",
    "nlp engineer": "machine_learning",
    "cv engineer": "machine_learning",
    "android": "java",
    "ios": "javascript",
    "mobile": "react",
    "spring": "java",
    "spring boot": "java",
    "hibernate": "java",
    "jpa": "java",
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase, trim, replace multiple spaces
    text = text.strip().lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_education(education_input: str) -> Optional[str]:
    cleaned = clean_text(education_input)
    if not cleaned:
        return None
    # Direct code match or alias match
    return EDUCATION_ALIASES.get(cleaned, EDUCATION_ALIASES.get(education_input.strip().lower()))

def normalize_skill(skill_input: str) -> str:
    cleaned = clean_text(skill_input)
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    # Replace spaces with underscore for canonical code matching
    slug = re.sub(r"[^\w\s]", "", cleaned).replace(" ", "_")
    return slug

def normalize_skills(skills: List[str]) -> List[str]:
    seen: Set[str] = set()
    normalized: List[str] = []
    for s in skills:
        code = normalize_skill(s)
        if code and code not in seen:
            seen.add(code)
            normalized.append(code)
    return normalized

def normalize_sectors(sectors: List[str]) -> List[str]:
    seen: Set[str] = set()
    normalized: List[str] = []
    for s in sectors:
        clean = clean_text(s).replace(" ", "_")
        if clean and clean not in seen:
            seen.add(clean)
            normalized.append(clean)
    return normalized

def normalize_location_string(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    cleaned = val.strip()
    return cleaned if cleaned else None
