"""
AU4A (Ask Us 4 Anything) Backend API Tests
Tests all A/B/C/D quadrant endpoints, user progress, sponsors, and Black Box
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
BLACKBOX_KEY = os.environ.get('BLACKBOX_MASTER_KEY', 'YowyeaYu14Tdym1Sfki8HLg83HzASSwQ2Sm2ychFDru5rA3Gf41R10E-Ix2RzDID')

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def test_user_id():
    """Generate unique test user ID"""
    return f"TEST_user_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def blackbox_client():
    """Session with Black Box auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "X-BlackBox-Key": BLACKBOX_KEY
    })
    return session

# ============================================================================
# HEALTH & ROOT ENDPOINTS
# ============================================================================

class TestHealthEndpoints:
    """Test health check and root endpoints"""
    
    def test_root_endpoint(self, api_client):
        """Test API root returns correct info"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "AU4A" in data["message"]
        assert data["status"] == "operational"
        print(f"✓ Root endpoint working: {data['message']}")
    
    def test_health_check(self, api_client):
        """Test health check endpoint"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")

# ============================================================================
# A: ASK LAYER TESTS
# ============================================================================

class TestAskLayer:
    """Test A: Ask layer - request submission"""
    
    def test_create_request(self, api_client, test_user_id):
        """Test creating a new request"""
        payload = {
            "content": "TEST_I need help learning Python programming",
            "category": "knowledge",
            "submitted_by": test_user_id
        }
        response = api_client.post(f"{BASE_URL}/api/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["content"] == payload["content"]
        assert data["category"] == payload["category"]
        assert data["status"] == "pending"
        print(f"✓ Request created with ID: {data['id']}")
        return data["id"]
    
    def test_get_requests_list(self, api_client):
        """Test getting list of requests"""
        response = api_client.get(f"{BASE_URL}/api/requests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} requests")
    
    def test_get_requests_with_filter(self, api_client):
        """Test filtering requests by status"""
        response = api_client.get(f"{BASE_URL}/api/requests", params={"status": "pending"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned requests should be pending
        for req in data:
            assert req["status"] == "pending"
        print(f"✓ Filtered requests by status: {len(data)} pending")
    
    def test_get_single_request(self, api_client, test_user_id):
        """Test getting a single request by ID"""
        # First create a request
        payload = {
            "content": "TEST_Single request test",
            "category": "test",
            "submitted_by": test_user_id
        }
        create_response = api_client.post(f"{BASE_URL}/api/ask", json=payload)
        request_id = create_response.json()["id"]
        
        # Then retrieve it
        response = api_client.get(f"{BASE_URL}/api/request/{request_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == request_id
        assert data["content"] == payload["content"]
        print(f"✓ Retrieved single request: {request_id}")
    
    def test_get_nonexistent_request(self, api_client):
        """Test 404 for non-existent request"""
        response = api_client.get(f"{BASE_URL}/api/request/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ Correctly returns 404 for non-existent request")

# ============================================================================
# ETHICS ENGINE TESTS
# ============================================================================

class TestEthicsEngine:
    """Test ethics evaluation system"""
    
    def test_create_evaluation(self, api_client, test_user_id):
        """Test submitting an evaluation"""
        # First create a request to evaluate
        request_payload = {
            "content": "TEST_Request for evaluation test",
            "category": "test",
            "submitted_by": test_user_id
        }
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        # Submit evaluation
        eval_payload = {
            "request_id": request_id,
            "evaluator_id": test_user_id,
            "legality_score": 8,
            "morality_score": 9,
            "harm_score": 2,
            "cultural_impact_score": 7,
            "comments": "TEST_This is a test evaluation"
        }
        response = api_client.post(f"{BASE_URL}/api/evaluate", json=eval_payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["request_id"] == request_id
        assert data["legality_score"] == 8
        print(f"✓ Evaluation submitted for request: {request_id}")
    
    def test_get_pending_evaluations(self, api_client):
        """Test getting requests pending evaluation"""
        response = api_client.get(f"{BASE_URL}/api/evaluate/pending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} pending evaluations")
    
    def test_get_evaluations_for_request(self, api_client, test_user_id):
        """Test getting all evaluations for a request"""
        # Create request and evaluation
        request_payload = {"content": "TEST_Eval retrieval test", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        eval_payload = {
            "request_id": request_id,
            "evaluator_id": test_user_id,
            "legality_score": 7,
            "morality_score": 7,
            "harm_score": 3,
            "cultural_impact_score": 6
        }
        api_client.post(f"{BASE_URL}/api/evaluate", json=eval_payload)
        
        # Get evaluations
        response = api_client.get(f"{BASE_URL}/api/evaluate/{request_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Retrieved {len(data)} evaluations for request")

# ============================================================================
# B: CONTRIBUTE LAYER TESTS
# ============================================================================

class TestContributeLayer:
    """Test B: Contribute layer - 6 B-types"""
    
    def test_create_contribution(self, api_client, test_user_id):
        """Test creating a contribution"""
        # First create a request
        request_payload = {"content": "TEST_Need contribution", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        # Create contribution
        contrib_payload = {
            "request_id": request_id,
            "contributor_id": test_user_id,
            "contribution_type": "bestow",
            "content": "TEST_I can help with this",
            "details": "I have experience in this area"
        }
        response = api_client.post(f"{BASE_URL}/api/contribute", json=contrib_payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["request_id"] == request_id
        assert data["contribution_type"] == "bestow"
        assert data["status"] == "pending"
        print(f"✓ Contribution created: {data['id']}")
        return data["id"]
    
    def test_all_contribution_types(self, api_client, test_user_id):
        """Test all 6 B-types: Borrow, Barter, Buy, Bring, Bestow, Befriend"""
        b_types = ["borrow", "barter", "buy", "bring", "bestow", "befriend"]
        
        for b_type in b_types:
            request_payload = {"content": f"TEST_Request for {b_type}", "category": "test"}
            request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
            request_id = request_response.json()["id"]
            
            contrib_payload = {
                "request_id": request_id,
                "contributor_id": test_user_id,
                "contribution_type": b_type,
                "content": f"TEST_{b_type} contribution"
            }
            if b_type == "barter":
                contrib_payload["trade_offer"] = "My skills in exchange"
            
            response = api_client.post(f"{BASE_URL}/api/contribute", json=contrib_payload)
            assert response.status_code == 200
            assert response.json()["contribution_type"] == b_type
            print(f"✓ {b_type.capitalize()} contribution type works")
    
    def test_get_contributions_for_request(self, api_client, test_user_id):
        """Test getting contributions for a request"""
        # Create request and contribution
        request_payload = {"content": "TEST_Contrib retrieval", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        contrib_payload = {
            "request_id": request_id,
            "contributor_id": test_user_id,
            "contribution_type": "bestow",
            "content": "TEST_Contribution for retrieval test"
        }
        api_client.post(f"{BASE_URL}/api/contribute", json=contrib_payload)
        
        # Get contributions
        response = api_client.get(f"{BASE_URL}/api/contributions/{request_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Retrieved {len(data)} contributions for request")

# ============================================================================
# C: COORDINATE LAYER TESTS
# ============================================================================

class TestCoordinateLayer:
    """Test C: Coordinate layer"""
    
    def test_create_coordination(self, api_client, test_user_id):
        """Test creating a coordination task"""
        # Create request first
        request_payload = {"content": "TEST_Need coordination", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        # Create coordination
        coord_payload = {
            "request_id": request_id,
            "coordinator_id": test_user_id,
            "strategy": "TEST_Step-by-step plan to fulfill this request",
            "resources_needed": ["volunteers", "funding"],
            "collaborators": ["designer", "developer"]
        }
        response = api_client.post(f"{BASE_URL}/api/coordinate", json=coord_payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["request_id"] == request_id
        assert data["status"] == "planning"
        assert "volunteers" in data["resources_needed"]
        print(f"✓ Coordination created: {data['id']}")
        return data["id"]
    
    def test_get_coordination_tasks(self, api_client, test_user_id):
        """Test getting coordination tasks for a request"""
        # Create request and coordination
        request_payload = {"content": "TEST_Coord retrieval", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        coord_payload = {
            "request_id": request_id,
            "coordinator_id": test_user_id,
            "strategy": "TEST_Strategy for retrieval test"
        }
        api_client.post(f"{BASE_URL}/api/coordinate", json=coord_payload)
        
        # Get coordination tasks
        response = api_client.get(f"{BASE_URL}/api/coordinate/{request_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Retrieved {len(data)} coordination tasks")

# ============================================================================
# D: EXECUTE LAYER TESTS
# ============================================================================

class TestExecuteLayer:
    """Test D: Execute layer"""
    
    def test_create_execution(self, api_client, test_user_id):
        """Test logging an execution"""
        # Create request first
        request_payload = {"content": "TEST_Need execution", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        # Create execution
        exec_payload = {
            "request_id": request_id,
            "executor_id": test_user_id,
            "action_taken": "TEST_Delivered the requested item",
            "verification_proof": "https://example.com/proof.jpg"
        }
        response = api_client.post(f"{BASE_URL}/api/execute", json=exec_payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["request_id"] == request_id
        assert data["status"] == "in_progress"
        print(f"✓ Execution logged: {data['id']}")
        return data["id"]
    
    def test_get_executions(self, api_client, test_user_id):
        """Test getting executions for a request"""
        # Create request and execution
        request_payload = {"content": "TEST_Exec retrieval", "category": "test"}
        request_response = api_client.post(f"{BASE_URL}/api/ask", json=request_payload)
        request_id = request_response.json()["id"]
        
        exec_payload = {
            "request_id": request_id,
            "executor_id": test_user_id,
            "action_taken": "TEST_Action for retrieval test"
        }
        api_client.post(f"{BASE_URL}/api/execute", json=exec_payload)
        
        # Get executions
        response = api_client.get(f"{BASE_URL}/api/execute/{request_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Retrieved {len(data)} executions")

# ============================================================================
# USER PROGRESS TESTS
# ============================================================================

class TestUserProgress:
    """Test user creation and progress tracking"""
    
    def test_create_user(self, api_client, test_user_id):
        """Test creating a new user"""
        payload = {"anonymous_id": test_user_id}
        response = api_client.post(f"{BASE_URL}/api/user", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["anonymous_id"] == test_user_id
        assert data["participation_level"] == 0
        print(f"✓ User created: {data['id']}")
        return data["id"]
    
    def test_get_user_progress_by_anonymous_id(self, api_client, test_user_id):
        """Test getting user progress by anonymous_id"""
        # Create user first
        payload = {"anonymous_id": test_user_id}
        api_client.post(f"{BASE_URL}/api/user", json=payload)
        
        # Get progress using anonymous_id
        response = api_client.get(f"{BASE_URL}/api/user/{test_user_id}/progress")
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == test_user_id
        assert "participation_level" in data
        assert "total_actions" in data
        assert "unlocked_features" in data
        assert "ask" in data["unlocked_features"]  # Level 0 always has ask
        print(f"✓ User progress retrieved: Level {data['participation_level']}")
    
    def test_user_stats(self, api_client, test_user_id):
        """Test getting user statistics"""
        # Create user
        payload = {"anonymous_id": test_user_id}
        api_client.post(f"{BASE_URL}/api/user", json=payload)
        
        # Get stats
        response = api_client.get(f"{BASE_URL}/api/user/{test_user_id}/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_asks" in data
        assert "total_contributions" in data
        assert "total_evaluations" in data
        print(f"✓ User stats retrieved")

# ============================================================================
# SPONSOR TESTS
# ============================================================================

class TestSponsors:
    """Test sponsor management (non-clickable logos)"""
    
    def test_create_sponsor(self, api_client):
        """Test creating a sponsor"""
        payload = {
            "company_name": "TEST_Ethical Company",
            "website": "https://example.com",
            "logo_url": "https://example.com/logo.png",
            "contact_email": "test@example.com"
        }
        response = api_client.post(f"{BASE_URL}/api/sponsor", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["company_name"] == payload["company_name"]
        assert data["agreement_status"] == "pending"
        print(f"✓ Sponsor created: {data['id']}")
        return data["id"]
    
    def test_get_sponsors(self, api_client):
        """Test getting sponsors list"""
        response = api_client.get(f"{BASE_URL}/api/sponsors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} sponsors")
    
    def test_activate_sponsor(self, api_client):
        """Test activating a sponsor"""
        # Create sponsor first
        payload = {
            "company_name": "TEST_Activate Sponsor",
            "website": "https://example.com",
            "logo_url": "https://example.com/logo.png",
            "contact_email": "activate@example.com"
        }
        create_response = api_client.post(f"{BASE_URL}/api/sponsor", json=payload)
        sponsor_id = create_response.json()["id"]
        
        # Activate
        response = api_client.patch(f"{BASE_URL}/api/sponsor/{sponsor_id}/activate")
        assert response.status_code == 200
        print(f"✓ Sponsor activated: {sponsor_id}")

# ============================================================================
# SEARCH ENGINE TESTS
# ============================================================================

class TestSearchEngine:
    """Test hybrid AI search (no ads)"""
    
    def test_search_endpoint(self, api_client):
        """Test search endpoint returns results"""
        response = api_client.get(f"{BASE_URL}/api/search", params={"q": "python programming"})
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "results" in data
        assert "internal_count" in data
        assert "external_count" in data
        print(f"✓ Search returned {len(data['results'])} results")
    
    def test_search_requires_query(self, api_client):
        """Test search requires query parameter"""
        response = api_client.get(f"{BASE_URL}/api/search")
        assert response.status_code == 422  # Validation error
        print("✓ Search correctly requires query parameter")

# ============================================================================
# BLACK BOX TESTS (Hidden Admin)
# ============================================================================

class TestBlackBox:
    """Test Black Box hidden admin interface"""
    
    def test_blackbox_requires_auth(self, api_client):
        """Test Black Box endpoints require authentication"""
        response = api_client.get(f"{BASE_URL}/api/blackbox/dashboard")
        assert response.status_code == 401
        print("✓ Black Box correctly requires authentication")
    
    def test_blackbox_invalid_key(self, api_client):
        """Test Black Box rejects invalid key"""
        api_client.headers.update({"X-BlackBox-Key": "invalid-key-12345"})
        response = api_client.get(f"{BASE_URL}/api/blackbox/dashboard")
        assert response.status_code == 403
        print("✓ Black Box correctly rejects invalid key")
    
    def test_blackbox_dashboard_with_valid_key(self, blackbox_client):
        """Test Black Box dashboard with valid master key"""
        response = blackbox_client.get(f"{BASE_URL}/api/blackbox/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert "code_review" in data
        assert "ethics" in data
        assert "tasks" in data
        assert "platform" in data
        print(f"✓ Black Box dashboard accessible with master key")
    
    def test_blackbox_audit_logs(self, blackbox_client):
        """Test Black Box audit logs (master only)"""
        response = blackbox_client.get(f"{BASE_URL}/api/blackbox/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} audit logs")
    
    def test_blackbox_code_submissions(self, blackbox_client):
        """Test Black Box code submissions list"""
        response = blackbox_client.get(f"{BASE_URL}/api/blackbox/code-submissions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} code submissions")
    
    def test_blackbox_ethics_cases(self, blackbox_client):
        """Test Black Box ethics cases list"""
        response = blackbox_client.get(f"{BASE_URL}/api/blackbox/ethics-cases")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} ethics cases")

# ============================================================================
# CONTRIBUTION OFFERS (Ramp-up Polling)
# ============================================================================

class TestContributionOffers:
    """Test contribution offers (supply side)"""
    
    def test_create_offer(self, api_client, test_user_id):
        """Test creating a contribution offer"""
        payload = {
            "contributor_id": test_user_id,
            "offer_type": "skill",
            "description": "TEST_I can teach programming",
            "category": "education",
            "availability": "weekends",
            "tags": ["python", "teaching"]
        }
        response = api_client.post(f"{BASE_URL}/api/offer", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["offer_type"] == "skill"
        assert data["is_fulfilled"] == False
        print(f"✓ Contribution offer created: {data['id']}")
    
    def test_get_offers(self, api_client):
        """Test getting contribution offers"""
        response = api_client.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} contribution offers")

# ============================================================================
# OUTREACH CAMPAIGNS
# ============================================================================

class TestOutreach:
    """Test company outreach campaigns"""
    
    def test_create_outreach(self, api_client):
        """Test creating an outreach campaign"""
        payload = {
            "company_name": "TEST_Target Company",
            "company_email": "contact@testcompany.com",
            "company_website": "https://testcompany.com",
            "notes": "TEST_Potential partner"
        }
        response = api_client.post(f"{BASE_URL}/api/outreach", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["company_name"] == payload["company_name"]
        assert data["status"] == "pending"
        assert "email_subject" in data
        assert "email_body" in data
        print(f"✓ Outreach campaign created: {data['id']}")
    
    def test_get_outreach_campaigns(self, api_client):
        """Test getting outreach campaigns"""
        response = api_client.get(f"{BASE_URL}/api/outreach")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} outreach campaigns")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
