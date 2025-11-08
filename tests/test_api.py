from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants lists so tests can mutate safely and then restore
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    # restore
    for k, v in original.items():
        activities[k]["participants"] = v


def test_get_activities():
    client = TestClient(app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity_name = "Chess Club"
    test_email = "tester@example.com"

    # Ensure not already present
    r = client.get("/activities")
    assert test_email not in r.json()[activity_name]["participants"]

    # Sign up
    r = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert r.status_code == 200
    assert f"Signed up {test_email}" in r.json().get("message", "")

    # Confirm present
    r = client.get("/activities")
    assert test_email in r.json()[activity_name]["participants"]

    # Unregister
    r = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert r.status_code == 200
    assert f"Unregistered {test_email}" in r.json().get("message", "")

    # Confirm removed
    r = client.get("/activities")
    assert test_email not in r.json()[activity_name]["participants"]
