"""
Integration tests for the FastAPI High School Management System API.
"""
import pytest
from fastapi.testclient import TestClient


class TestIntegrationScenarios:
    """Integration tests for complete user scenarios."""
    
    def test_new_student_full_workflow(self, client, reset_activities):
        """Test a complete workflow for a new student joining multiple activities."""
        new_student = "newcomer@mergington.edu"
        
        # Student checks available activities
        response = client.get("/activities")
        assert response.status_code == 200
        activities_data = response.json()
        
        # Student decides to join Programming Class and Art Workshop
        target_activities = ["Programming Class", "Art Workshop"]
        
        for activity in target_activities:
            # Verify activity exists and has capacity
            assert activity in activities_data
            current_count = len(activities_data[activity]["participants"])
            max_participants = activities_data[activity]["max_participants"]
            assert current_count < max_participants, f"{activity} is at capacity"
            
            # Sign up for activity
            response = client.post(f"/activities/{activity}/signup?email={new_student}")
            assert response.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        updated_data = response.json()
        
        for activity in target_activities:
            assert new_student in updated_data[activity]["participants"]
        
        # Student later decides to leave Programming Class but stay in Art Workshop
        response = client.delete(f"/activities/Programming Class/unregister?email={new_student}")
        assert response.status_code == 200
        
        # Final verification
        response = client.get("/activities")
        final_data = response.json()
        
        assert new_student not in final_data["Programming Class"]["participants"]
        assert new_student in final_data["Art Workshop"]["participants"]
    
    def test_activity_capacity_management(self, client, reset_activities):
        """Test activity capacity management under realistic conditions."""
        activity_name = "Math Olympiad"  # Has max_participants: 10
        
        # Get current state
        response = client.get("/activities")
        initial_data = response.json()[activity_name]
        current_participants = len(initial_data["participants"])
        max_capacity = initial_data["max_participants"]
        
        # Calculate how many more students we can add
        available_spots = max_capacity - current_participants
        
        # Add students up to capacity
        new_students = [f"student{i}@mergington.edu" for i in range(available_spots)]
        
        for student in new_students:
            response = client.post(f"/activities/{activity_name}/signup?email={student}")
            assert response.status_code == 200
        
        # Verify we're at capacity
        response = client.get("/activities")
        full_data = response.json()[activity_name]
        assert len(full_data["participants"]) == max_capacity
        
        # Try to add one more student (this should work since our API doesn't enforce capacity)
        overflow_student = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_student}")
        assert response.status_code == 200  # Current implementation allows over-capacity
        
        # Verify the student was added even though over capacity
        response = client.get("/activities")
        overflow_data = response.json()[activity_name]
        assert len(overflow_data["participants"]) == max_capacity + 1
        assert overflow_student in overflow_data["participants"]
    
    def test_multiple_students_same_activity_workflow(self, client, reset_activities):
        """Test multiple students interacting with the same activity."""
        activity_name = "Drama Club"
        test_students = [
            "actor1@mergington.edu",
            "actor2@mergington.edu", 
            "actor3@mergington.edu"
        ]
        
        # All students sign up
        for student in test_students:
            response = client.post(f"/activities/{activity_name}/signup?email={student}")
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        
        for student in test_students:
            assert student in activity_data["participants"]
        
        # Middle student leaves
        leaving_student = test_students[1]
        response = client.delete(f"/activities/{activity_name}/unregister?email={leaving_student}")
        assert response.status_code == 200
        
        # Verify correct student was removed and others remain
        response = client.get("/activities")
        final_data = response.json()[activity_name]
        
        assert leaving_student not in final_data["participants"]
        assert test_students[0] in final_data["participants"]
        assert test_students[2] in final_data["participants"]
        
        # Leaving student decides to join again
        response = client.post(f"/activities/{activity_name}/signup?email={leaving_student}")
        assert response.status_code == 200
        
        # Verify they're back in
        response = client.get("/activities")
        rejoined_data = response.json()[activity_name]
        assert leaving_student in rejoined_data["participants"]


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge case scenarios."""
    
    def test_malformed_requests(self, client, reset_activities):
        """Test handling of malformed requests."""
        # Missing email parameter
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # FastAPI validation error
        
        # Empty email parameter
        response = client.post("/activities/Chess Club/signup?email=")
        assert response.status_code == 200  # Empty string is accepted by current implementation
        
        # Very long email
        long_email = "a" * 1000 + "@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={long_email}")
        assert response.status_code == 200  # Long emails are accepted
    
    def test_special_characters_in_activity_names(self, client, reset_activities):
        """Test handling of special characters in URLs."""
        # Note: Our current activities don't have special characters,
        # but this tests URL encoding behavior
        
        # Try with URL-encoded activity name
        import urllib.parse
        activity_name = "Programming Class"
        encoded_name = urllib.parse.quote(activity_name)
        
        response = client.post(f"/activities/{encoded_name}/signup?email=test@mergington.edu")
        assert response.status_code == 200
    
    def test_concurrent_operations_simulation(self, client, reset_activities):
        """Simulate concurrent operations on the same activity."""
        activity_name = "Science Club"
        students = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Simulate concurrent signups
        responses = []
        for student in students:
            response = client.post(f"/activities/{activity_name}/signup?email={student}")
            responses.append((student, response))
        
        # All should succeed
        for student, response in responses:
            assert response.status_code == 200, f"Signup failed for {student}"
        
        # Verify all students are registered
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        
        for student in students:
            assert student in activity_data["participants"]
        
        # Simulate concurrent unregistrations
        unregister_responses = []
        for student in students[:3]:  # Only unregister first 3
            response = client.delete(f"/activities/{activity_name}/unregister?email={student}")
            unregister_responses.append((student, response))
        
        # All unregistrations should succeed
        for student, response in unregister_responses:
            assert response.status_code == 200, f"Unregister failed for {student}"
        
        # Verify final state
        response = client.get("/activities")
        final_data = response.json()[activity_name]
        
        # First 3 should be gone
        for student in students[:3]:
            assert student not in final_data["participants"]
        
        # Last 2 should remain
        for student in students[3:]:
            assert student in final_data["participants"]