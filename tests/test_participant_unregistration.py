from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_activities_response_disables_caching():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_unregister_participant():
    activity_name = "Chess Club"
    email = f"{uuid4()}@mergington.edu"
    participants = activities[activity_name]["participants"]
    participants.append(email)

    try:
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in participants
    finally:
        if email in participants:
            participants.remove(email)


def test_unregister_unknown_activity_returns_not_found():
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonparticipant_returns_not_found():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": f"{uuid4()}@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
