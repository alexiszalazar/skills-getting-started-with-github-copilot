from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_activity_keys():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success_adds_student_to_activity():
    email = "new.student@mergington.edu"
    activity_name = "Chess Club"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200
    assert signup_response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_rejects_duplicate_student():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post("/activities/Unknown Club/signup", params={"email": "x@y.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success_removes_student_from_activity():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_rejects_student_not_signed_up():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not.in.list@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity():
    response = client.delete("/activities/Unknown Club/signup", params={"email": "x@y.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
