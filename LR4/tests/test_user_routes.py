from uuid import UUID


def test_get_users_empty(test_client):
    response = test_client.get("/users")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 0
    assert payload["users"] == []


def test_create_and_retrieve_user(test_client):
    create_response = test_client.post(
        "/users",
        json={"username": "api_user", "email": "api_user@example.com"},
    )
    assert create_response.status_code in (200, 201)
    created_user = create_response.json()
    user_id = UUID(created_user["id"])
    assert created_user["username"] == "api_user"

    get_response = test_client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["email"] == "api_user@example.com"


def test_update_and_delete_user(test_client):
    create_response = test_client.post(
        "/users",
        json={"username": "to_update", "email": "update_me@example.com"},
    )
    user_id = create_response.json()["id"]

    update_response = test_client.put(
        f"/users/{user_id}",
        json={"description": "updated via api"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "updated via api"

    delete_response = test_client.delete(f"/users/{user_id}")
    assert delete_response.status_code in (200, 204)

    not_found_response = test_client.get(f"/users/{user_id}")
    assert not_found_response.status_code == 404

