import sys
import os
from pathlib import Path

# Add backend directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

def run_smoke_test():
    print("=== Running End-to-End Integration Smoke Test ===")
    client = TestClient(app)

    # 1. Health check
    print("[1/4] Checking GET /api/v1/health...")
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    health_data = res_health.json()
    assert health_data["status"] == "healthy"
    print(f"      OK! Health status: {health_data['status']}, Sample count: {health_data['sample_data_count']}")

    # 2. Options check
    print("[2/4] Checking GET /api/v1/options...")
    res_options = client.get("/api/v1/options")
    assert res_options.status_code == 200, f"Options check failed: {res_options.text}"
    options_data = res_options.json()
    assert len(options_data["education_categories"]) > 0
    assert len(options_data["sectors"]) > 0
    print(f"      OK! Found {len(options_data['education_categories'])} education categories and {len(options_data['sectors'])} sectors.")

    # 3. Recommendations check
    print("[3/4] Checking POST /api/v1/recommendations...")
    profile_payload = {
        "profile": {
            "education": "twelfth_pass",
            "skills": ["python", "ms_excel"],
            "sectors": ["it_software"],
            "state": "Maharashtra",
            "district": "Pune",
            "preferred_work_mode": "any",
            "is_work_mode_mandatory": False,
            "is_location_mandatory": False,
            "willing_to_relocate": True
        },
        "limit": 5
    }
    res_rec = client.post("/api/v1/recommendations", json=profile_payload)
    assert res_rec.status_code == 200, f"Recommendation request failed: {res_rec.text}"
    rec_data = res_rec.json()
    results = rec_data.get("results", [])
    assert len(results) > 0, "No recommendations returned for valid profile!"
    assert len(results) <= 5, f"Expected <= 5 recommendations, got {len(results)}"
    first_item = results[0]
    first_id = first_item["internship"]["id"]
    print(f"      OK! Received {len(results)} recommendations. Top match: {first_id} ('{first_item['internship']['title']}', Score: {first_item['relative_score']})")

    # 4. Internship Detail check
    print(f"[4/4] Checking GET /api/v1/internships/{first_id}...")
    res_detail = client.get(f"/api/v1/internships/{first_id}")
    assert res_detail.status_code == 200, f"Detail check failed: {res_detail.text}"
    detail_data = res_detail.json()
    assert detail_data["id"] == first_id
    assert "description" in detail_data
    print(f"      OK! Loaded details for '{detail_data['title']}' ({detail_data['organization_name']}).")

    print("\nALL SMOKE & INTEGRATION CHECKS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    try:
        run_smoke_test()
    except Exception as e:
        print(f"\nERROR: Smoke test failed: {e}", file=sys.stderr)
        sys.exit(1)
