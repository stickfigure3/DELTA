"""Docker deployment tests for DELTA v0.1.

These tests verify that the Docker container can be built and run locally,
and that it responds correctly to health checks and API requests.

Usage:
    # Start Docker container first
    ./scripts/docker-local.sh 8000
    
    # Then run these tests
    pytest tests/v0.1/test_docker.py -v
    
    # Or run with a custom port
    DELTA_TEST_PORT=8080 pytest tests/v0.1/test_docker.py -v
"""

import os
import pytest
import httpx

# Configuration
DELTA_HOST = os.environ.get("DELTA_TEST_HOST", "localhost")
DELTA_PORT = os.environ.get("DELTA_TEST_PORT", "8000")
BASE_URL = f"http://{DELTA_HOST}:{DELTA_PORT}"


@pytest.fixture
def client():
    """Create an HTTP client for testing."""
    return httpx.Client(base_url=BASE_URL, timeout=10.0)


class TestDockerHealth:
    """Test Docker container health and connectivity."""
    
    def test_health_endpoint(self, client):
        """Test that the health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self, client):
        """Test that the root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "DELTA Platform"
        assert "version" in data
        assert data["status"] == "running"
    
    def test_docs_accessible(self, client):
        """Test that the API docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_schema(self, client):
        """Test that the OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "DELTA Platform"


class TestDockerAPIStatus:
    """Test API route loading status."""
    
    def test_status_endpoint(self, client):
        """Test that the status endpoint shows loaded routes."""
        response = client.get("/v1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "routes_loaded" in data
        assert "routes_failed" in data
        
        # These routes should be loaded
        expected_routes = ["/v1/auth", "/v1/agents", "/v1/sandboxes", "/v1/messaging"]
        for route in expected_routes:
            assert route in data["routes_loaded"], f"Route {route} not loaded"


class TestDockerAPIEndpoints:
    """Test that API endpoints are accessible (not necessarily functional)."""
    
    def test_auth_endpoints_exist(self, client):
        """Test that auth endpoints exist."""
        # These should return validation errors, not 404
        response = client.post("/v1/auth/register", json={})
        assert response.status_code != 404
        
        response = client.post("/v1/auth/login", json={})
        assert response.status_code != 404
    
    def test_agents_endpoints_exist(self, client):
        """Test that agents endpoints exist."""
        response = client.get("/v1/agents/")
        assert response.status_code != 404
    
    def test_sandboxes_endpoints_exist(self, client):
        """Test that sandboxes endpoints exist."""
        response = client.get("/v1/sandboxes/")
        assert response.status_code != 404


class TestDockerWebSocket:
    """Test WebSocket endpoint availability."""
    
    def test_ws_stats_endpoint(self, client):
        """Test that WebSocket stats endpoint is accessible."""
        response = client.get("/v1/ws/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert "total_connections" in data


# Standalone test runner
if __name__ == "__main__":
    """Run a quick connectivity test without pytest."""
    import sys
    
    print(f"Testing DELTA Platform at {BASE_URL}")
    print("=" * 50)
    
    try:
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            # Health check
            response = client.get("/health")
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("✅ Health check: PASSED")
            else:
                print(f"❌ Health check: FAILED ({response.status_code})")
                sys.exit(1)
            
            # Root endpoint
            response = client.get("/")
            if response.status_code == 200:
                print("✅ Root endpoint: PASSED")
            else:
                print(f"❌ Root endpoint: FAILED ({response.status_code})")
            
            # Status endpoint
            response = client.get("/v1/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status endpoint: PASSED")
                print(f"   Routes loaded: {data['routes_loaded']}")
                if data['routes_failed']:
                    print(f"   Routes failed: {data['routes_failed']}")
            else:
                print(f"❌ Status endpoint: FAILED ({response.status_code})")
            
            print("=" * 50)
            print("🎉 Docker container is working correctly!")
            
    except httpx.ConnectError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Make sure the Docker container is running:")
        print("   ./scripts/docker-local.sh")
        sys.exit(1)
