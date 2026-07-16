"""
Test suite for Effective Dollop API
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data
        assert "version" in data


class TestAnalyzeEndpoint:
    """Tests for sentiment analysis endpoint."""
    
    def test_analyze_positive_text(self):
        """Test analysis of positive text."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "I love this amazing product!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["emotion"] == "happy"
        assert data["data"]["confidence"] > 0.5
    
    def test_analyze_negative_text(self):
        """Test analysis of negative text."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "This is terrible and awful!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["emotion"] == "angry"
    
    def test_analyze_neutral_text(self):
        """Test analysis of neutral text."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "The meeting is at 3 PM."}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["emotion"] == "neutral"
    
    def test_analyze_empty_text(self):
        """Test analysis with empty text."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_long_text(self):
        """Test analysis with long text."""
        long_text = "I love this! " * 100
        response = client.post(
            "/api/v1/analyze",
            json={"text": long_text}
        )
        assert response.status_code == 200
    
    def test_response_structure(self):
        """Test response has correct structure."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "Test text"}
        )
        data = response.json()
        
        assert "status" in data
        assert "data" in data
        assert "id" in data["data"]
        assert "text" in data["data"]
        assert "emotion" in data["data"]
        assert "confidence" in data["data"]
        assert "scores" in data["data"]
        assert "timestamp" in data["data"]


class TestBatchEndpoint:
    """Tests for batch analysis endpoint."""
    
    def test_batch_analysis(self):
        """Test batch analysis of multiple texts."""
        response = client.post(
            "/api/v1/analyze/batch",
            json={
                "texts": [
                    "I love this!",
                    "This is terrible!",
                    "It's okay."
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["results"]) == 3
        assert "summary" in data
    
    def test_batch_summary(self):
        """Test batch summary statistics."""
        response = client.post(
            "/api/v1/analyze/batch",
            json={
                "texts": [
                    "Happy text!",
                    "Another happy text!",
                    "Sad text."
                ]
            }
        )
        data = response.json()
        assert "total_analyzed" in data["summary"]
        assert "emotion_distribution" in data["summary"]
        assert "avg_confidence" in data["summary"]


class TestHistoryEndpoint:
    """Tests for history endpoint."""
    
    def test_get_history(self):
        """Test getting analysis history."""
        # First, add some data
        client.post("/api/v1/analyze", json={"text": "Test 1"})
        client.post("/api/v1/analyze", json={"text": "Test 2"})
        
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
    
    def test_clear_history(self):
        """Test clearing history."""
        response = client.delete("/api/v1/history")
        assert response.status_code == 200
        
        # Verify history is empty
        response = client.get("/api/v1/history")
        data = response.json()
        assert len(data["data"]) == 0


class TestStatsEndpoint:
    """Tests for statistics endpoint."""
    
    def test_get_stats(self):
        """Test getting statistics."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data["data"]
        assert "emotion_counts" in data["data"]
        assert "avg_confidence" in data["data"]
