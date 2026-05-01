import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
}

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    # Arrange is handled by the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant():
    # Arrange
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"

    updated_response = client.get("/activities")
    assert new_email in updated_response.json()["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_email():
    # Arrange
    duplicate_email = "michael@mergington.edu"

    # Act
    first_response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": duplicate_email},
    )
    second_response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert first_response.status_code == 400
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"].lower()


def test_remove_participant_from_activity():
    # Arrange
    email_to_remove = "daniel@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants/daniel%40mergington.edu"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from Chess Club"

    updated_response = client.get("/activities")
    assert email_to_remove not in updated_response.json()["Chess Club"]["participants"]


def test_remove_participant_returns_404_for_missing_participant():
    # Arrange
    missing_email = "unknown@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants/unknown%40mergington.edu"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
