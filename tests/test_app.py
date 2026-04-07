import pytest
from fastapi.testclient import TestClient
import src.app as app_module

# Create a TestClient instance
client = TestClient(app_module.app)

@pytest.fixture
def reset_activities():
    """Fixture to reset the in-memory activities data before each test."""
    original = app_module.activities.copy()
    yield
    app_module.activities.clear()
    app_module.activities.update(original)

def test_get_activities(reset_activities):
    """Test GET /activities retrieves all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert data == app_module.activities

def test_signup_valid(reset_activities):
    """Test POST /activities/{activity_name}/signup with valid data."""
    activity = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in app_module.activities[activity]["participants"]

def test_signup_activity_not_found(reset_activities):
    """Test POST /activities/{activity_name}/signup for non-existent activity."""
    response = client.post("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_already_signed_up(reset_activities):
    """Test POST /activities/{activity_name}/signup when already signed up."""
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}

def test_signup_activity_full(reset_activities):
    """Test POST /activities/{activity_name}/signup when activity is full."""
    activity = "Chess Club"
    max_participants = app_module.activities[activity]["max_participants"]
    current_participants = len(app_module.activities[activity]["participants"])
    
    # Fill the activity to max capacity
    for i in range(max_participants - current_participants):
        email = f"fill{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Attempt to sign up one more (should fail)
    response = client.post(f"/activities/{activity}/signup", params={"email": "extra@mergington.edu"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}

def test_unregister_valid(reset_activities):
    """Test DELETE /activities/{activity_name}/signup with valid data."""
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in app_module.activities[activity]["participants"]

def test_unregister_activity_not_found(reset_activities):
    """Test DELETE /activities/{activity_name}/signup for non-existent activity."""
    response = client.delete("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_signed_up(reset_activities):
    """Test DELETE /activities/{activity_name}/signup when not signed up."""
    activity = "Chess Club"
    email = "notsigned@mergington.edu"
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in activity"}