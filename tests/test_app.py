"""
Tests for the Mergington High School API

Using Arrange-Act-Assert structure for each test.
"""

from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


class TestRootEndpoint:
    def test_root_redirects_to_static(self):
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        # Arrange
        reset_activities()

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data

    def test_activity_has_required_fields(self):
        # Arrange
        reset_activities()
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities_data = response.json()
        chess_club = activities_data["Chess Club"]

        # Assert
        assert expected_fields <= set(chess_club.keys())
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    def test_signup_new_student_success(self):
        # Arrange
        reset_activities()
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_fails(self):
        # Arrange
        reset_activities()
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        # Arrange
        reset_activities()
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    def test_unregister_existing_student_success(self):
        # Arrange
        reset_activities()
        activity_name = "Chess Club"
        email = "tempstudent@mergington.edu"
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        assert signup_response.status_code == 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_student_fails(self):
        # Arrange
        reset_activities()
        activity_name = "Tennis Team"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        # Arrange
        reset_activities()
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
