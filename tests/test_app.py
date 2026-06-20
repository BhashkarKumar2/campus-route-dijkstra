from app import create_app


def test_route_api_returns_path_for_sample_graph():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/api/route",
        json={"source": "dtu_entrance", "target": "dtu_library", "profile": "walk"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["path_ids"][0] == "dtu_entrance"
    assert payload["path_ids"][-1] == "dtu_library"
    assert payload["total_time_min"] > 0
    assert payload["visited_order"]


def test_route_api_rejects_same_source_and_target():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/api/route",
        json={"source": "dtu_entrance", "target": "dtu_entrance"},
    )

    assert response.status_code == 400
    assert "different" in response.get_json()["error"]
