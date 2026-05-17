from __future__ import annotations


def test_health_endpoint(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_application_endpoint(client, sample_request) -> None:
    response = client.post(
        "/v1/applications/analyze",
        json=sample_request.model_dump(mode="json"),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"]
    assert payload["match"]["score"] >= 60
    assert "cover_letter" in payload


def test_get_application_after_analysis(client, sample_request) -> None:
    created = client.post(
        "/v1/applications/analyze",
        json=sample_request.model_dump(mode="json"),
    ).json()

    fetched = client.get(f"/v1/applications/{created['id']}")

    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_list_applications_endpoint(client, sample_request) -> None:
    client.post("/v1/applications/analyze", json=sample_request.model_dump(mode="json"))

    response = client.get("/v1/applications")

    assert response.status_code == 200
    assert len(response.json()) == 1

