"""
Performance and stress tests for the FastAPI High School Management System API.
"""
import pytest
import time
from fastapi.testclient import TestClient


class TestPerformance:
    """Basic performance tests for API endpoints."""
    
    def test_get_activities_performance(self, client, reset_activities):
        """Test performance of getting activities endpoint."""
        # Warm up
        client.get("/activities")
        
        # Measure response time for multiple requests
        start_time = time.time()
        num_requests = 100
        
        for _ in range(num_requests):
            response = client.get("/activities")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_requests
        
        # Assert reasonable performance (less than 10ms per request on average)
        assert avg_time < 0.01, f"Average response time too slow: {avg_time:.4f}s"
        print(f"Average response time for /activities: {avg_time:.4f}s")
    
    def test_signup_performance_batch(self, client, reset_activities):
        """Test performance of batch signups."""
        activity_name = "Basketball Club"
        num_signups = 50
        
        # Generate unique emails
        emails = [f"perf_test_{i}@mergington.edu" for i in range(num_signups)]
        
        start_time = time.time()
        
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_signups
        
        # Assert reasonable performance
        assert avg_time < 0.01, f"Average signup time too slow: {avg_time:.4f}s"
        print(f"Average signup time: {avg_time:.4f}s")
        
        # Verify all signups were successful
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        for email in emails:
            assert email in participants
    
    def test_mixed_operations_performance(self, client, reset_activities):
        """Test performance of mixed operations (signup/unregister/get)."""
        activity_name = "Programming Class"
        num_operations = 30
        
        emails = [f"mixed_test_{i}@mergington.edu" for i in range(num_operations)]
        
        start_time = time.time()
        
        for i, email in enumerate(emails):
            # Signup
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
            
            # Get activities (every 5th operation)
            if i % 5 == 0:
                response = client.get("/activities")
                assert response.status_code == 200
            
            # Unregister every other signup
            if i % 2 == 0:
                response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
                assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete reasonably quickly
        assert total_time < 1.0, f"Mixed operations took too long: {total_time:.4f}s"
        print(f"Mixed operations completed in: {total_time:.4f}s")


class TestDataIntegrity:
    """Test data integrity under various conditions."""
    
    def test_data_consistency_after_many_operations(self, client, reset_activities):
        """Test data consistency after performing many operations."""
        activity_name = "Chess Club"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = set(response.json()[activity_name]["participants"])
        
        # Perform many signup/unregister operations
        test_emails = [f"consistency_test_{i}@mergington.edu" for i in range(20)]
        
        # Sign everyone up
        for email in test_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Unregister half of them
        for email in test_emails[:10]:
            response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
            assert response.status_code == 200
        
        # Sign up the first 5 again
        for email in test_emails[:5]:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Final verification
        response = client.get("/activities")
        final_participants = set(response.json()[activity_name]["participants"])
        
        # Should have original participants + test_emails[0:5] + test_emails[10:20]
        expected_participants = initial_participants.union(
            set(test_emails[:5])
        ).union(
            set(test_emails[10:])
        )
        
        assert final_participants == expected_participants
        
        # Verify no duplicates
        participants_list = response.json()[activity_name]["participants"]
        assert len(participants_list) == len(set(participants_list)), "Duplicate participants found"
    
    def test_participant_list_integrity(self, client, reset_activities):
        """Test that participant lists maintain integrity."""
        activities_to_test = ["Soccer Team", "Art Workshop", "Science Club"]
        
        # Add test participants to each activity
        for activity in activities_to_test:
            for i in range(5):
                email = f"integrity_{activity}_{i}@mergington.edu"
                response = client.post(f"/activities/{activity}/signup?email={email}")
                assert response.status_code == 200
        
        # Remove some participants
        for activity in activities_to_test:
            for i in range(0, 5, 2):  # Remove every other participant
                email = f"integrity_{activity}_{i}@mergington.edu"
                response = client.delete(f"/activities/{activity}/unregister?email={email}")
                assert response.status_code == 200
        
        # Verify final state
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities_to_test:
            participants = data[activity]["participants"]
            
            # Check that odd-indexed participants remain
            for i in range(1, 5, 2):
                expected_email = f"integrity_{activity}_{i}@mergington.edu"
                assert expected_email in participants
            
            # Check that even-indexed participants are gone
            for i in range(0, 5, 2):
                removed_email = f"integrity_{activity}_{i}@mergington.edu"
                assert removed_email not in participants
    
    def test_cross_activity_operations(self, client, reset_activities):
        """Test that operations on one activity don't affect others."""
        student_email = "cross_test@mergington.edu"
        activities = ["Drama Club", "Math Olympiad", "Gym Class"]
        
        # Sign up for all activities
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={student_email}")
            assert response.status_code == 200
        
        # Get snapshots of other activities before modification
        response = client.get("/activities")
        before_data = response.json()
        
        target_activity = "Drama Club"
        other_activities = ["Math Olympiad", "Gym Class"]
        
        # Unregister from target activity
        response = client.delete(f"/activities/{target_activity}/unregister?email={student_email}")
        assert response.status_code == 200
        
        # Verify target activity changed but others didn't
        response = client.get("/activities")
        after_data = response.json()
        
        # Target activity should have changed
        assert student_email not in after_data[target_activity]["participants"]
        
        # Other activities should be unchanged
        for activity in other_activities:
            assert student_email in after_data[activity]["participants"]
            
            # Verify other participants in these activities are unchanged
            before_participants = set(before_data[activity]["participants"])
            after_participants = set(after_data[activity]["participants"])
            
            # Only difference should be our test student (if they were added)
            assert before_participants.issubset(after_participants) or \
                   after_participants.issubset(before_participants)