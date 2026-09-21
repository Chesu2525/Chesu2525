def test_create_and_filter_incident(client):
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Flooded clinic",
            "description": "Water has entered the ground floor.",
            "category": "flood",
            "severity": "high",
            "latitude": 40.7128,
            "longitude": -74.006,
            "people_affected": 18,
        },
    )
    assert response.status_code == 201
    incident = response.json["data"]
    assert incident["status"] == "reported"
    assert incident["location"]["latitude"] == 40.7128

    response = client.get("/api/v1/incidents?severity=high")
    assert response.status_code == 200
    assert len(response.json["data"]) == 1


def test_rejects_invalid_incident(client):
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Invalid",
            "description": "Bad coordinates",
            "category": "flood",
            "severity": "critical",
            "latitude": 200,
            "longitude": 0,
        },
    )
    assert response.status_code == 400
