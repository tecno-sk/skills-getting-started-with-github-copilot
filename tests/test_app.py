"""
Tests for the FastAPI High School Management System API.
"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that the root endpoint redirects to the static index page."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Redirect status code
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the get activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are returned
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that activities have the correct data structure."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test the activity signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client, reset_activities, test_email):
        """Test successful signup for an existing activity."""
        activity_name = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_participants = len(response.json()[activity_name]["participants"])
        
        # Sign up for the activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
        
        # Verify the participant was added
        response = client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_participants + 1
        assert test_email in updated_participants
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities, test_email):
        """Test signup for a non-existent activity returns 404."""
        response = client.post(
            f"/activities/NonExistentActivity/signup?email={test_email}"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup for the same email returns 400."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_different_activities(self, client, reset_activities, test_email):
        """Test that a user can sign up for multiple different activities."""
        activities_to_signup = ["Chess Club", "Programming Class"]
        
        for activity_name in activities_to_signup:
            response = client.post(
                f"/activities/{activity_name}/signup?email={test_email}"
            )
            assert response.status_code == 200
        
        # Verify the user is in both activities
        response = client.get("/activities")
        data = response.json()
        
        for activity_name in activities_to_signup:
            assert test_email in data[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test the activity unregistration endpoint."""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successful unregistration of an existing participant."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club
        
        # Get initial participant count
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Unregister from the activity
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the participant was removed
        response = client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email not in updated_participants
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities, test_email):
        """Test unregistration from a non-existent activity returns 404."""
        response = client.delete(
            f"/activities/NonExistentActivity/unregister?email={test_email}"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_non_participant(self, client, reset_activities, test_email):
        """Test unregistration of a non-participant returns 400."""
        activity_name = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a user can unregister and then signup again."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club
        
        # First, unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # Then, sign up again
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify addition
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]


class TestEndToEndWorkflows:
    """Test complete workflows and edge cases."""
    
    def test_complete_signup_unregister_workflow(self, client, reset_activities, test_email):
        """Test a complete workflow of signup and unregistration."""
        activity_name = "Programming Class"
        
        # Initial state - user not registered
        response = client.get("/activities")
        assert test_email not in response.json()[activity_name]["participants"]
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert test_email in response.json()[activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        assert response.status_code == 200
        
        # Verify unregistration
        response = client.get("/activities")
        assert test_email not in response.json()[activity_name]["participants"]
    
    def test_activity_names_with_spaces(self, client, reset_activities, test_email):
        """Test that activity names with spaces work correctly in URLs."""
        activity_name = "Programming Class"  # Contains space
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        assert response.status_code == 200
    
    def test_email_validation_in_endpoints(self, client, reset_activities):
        """Test behavior with different email formats."""
        activity_name = "Chess Club"
        
        # Test with valid email
        valid_email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup?email={valid_email}"
        )
        assert response.status_code == 200
        
        # The API doesn't validate email format, so any string should work
        # This tests the current behavior
        weird_email = "not-an-email"
        response = client.post(
            f"/activities/{activity_name}/signup?email={weird_email}"
        )
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency and state management."""
    
    def test_activities_data_persistence_during_session(self, client, reset_activities, test_email):
        """Test that activity data changes persist during the session."""
        activity_name = "Science Club"
        
        # Sign up user
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Make multiple requests and verify data persists
        for _ in range(3):
            response = client.get("/activities")
            assert test_email in response.json()[activity_name]["participants"]
    
    def test_participant_list_order_maintained(self, client, reset_activities):
        """Test that participant order is maintained when adding/removing participants."""
        activity_name = "Art Workshop"
        test_emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        # Add test participants
        for email in test_emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify order
        response = client.get("/activities")
        current_participants = response.json()[activity_name]["participants"]
        
        # Initial participants should still be at the beginning
        for i, participant in enumerate(initial_participants):
            assert current_participants[i] == participant
        
        # Test participants should be at the end in order
        for i, email in enumerate(test_emails):
            assert current_participants[len(initial_participants) + i] == email