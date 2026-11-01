def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "sample_data_count" in data
    assert "disclaimer" in data

def test_options_endpoint(client):
    response = client.get("/api/v1/options")
    assert response.status_code == 200
    data = response.json()
    assert "education_categories" in data
    assert "sectors" in data
    assert "skills" in data
    assert "states_and_districts" in data
    assert "work_modes" in data
    assert len(data["education_categories"]) > 0

def test_internships_list_and_pagination(client):
    response = client.get("/api/v1/internships?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert len(data["items"]) <= 2

def test_internship_detail_and_404(client):
    # Known test ID
    response = client.get("/api/v1/internships/TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "TEST-001"
    assert data["title"] == "Python Data Intern"

    # Non-existent ID
    res_404 = client.get("/api/v1/internships/NON-EXISTENT-999")
    assert res_404.status_code == 404

def test_recommendation_api_valid(client):
    payload = {
        "profile": {
            "education": "twelfth_pass",
            "skills": ["python"],
            "sectors": ["it_software"],
            "state": "Maharashtra",
            "district": "Mumbai",
            "preferred_work_mode": "onsite",
            "is_work_mode_mandatory": False,
            "is_location_mandatory": False,
            "willing_to_relocate": True
        },
        "limit": 5
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_eligible" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["internship"]["id"] == "TEST-001"

def test_recommendation_api_invalid_education(client):
    payload = {
        "profile": {
            "education": "invalid_qualification_code_xyz",
            "skills": []
        }
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 422
