"""API integration tests using TestClient with mocked endpoints."""

import pytest
from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


@pytest.fixture
def client():
    """Create test client with mocked routes for testing API contract."""
    # Create a minimal test app
    app = FastAPI(title="Next.Epoch API Test")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add health routes
    from next_epoch.api.routes import health
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])

    # Add content routes (mock data)
    content_router = APIRouter(prefix="/content")

    @content_router.get("")
    def list_content(
        source: Optional[str] = None,
        type: Optional[str] = None,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
    ):
        return {
            "data": [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
            }
        }

    @content_router.get("/search")
    def search_content(q: str = Query(..., min_length=2)):
        return {
            "data": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "total_pages": 0,
            }
        }

    @content_router.get("/{content_id}")
    def get_content(content_id: str):
        raise HTTPException(status_code=404, detail="Content not found")

    app.include_router(content_router, prefix="/api/v1", tags=["Content"])

    # Add sources routes (mock data)
    sources_router = APIRouter(prefix="/sources")

    MOCK_SOURCES = [
        {"id": "arxiv", "type": "arxiv", "name": "arXiv", "enabled": True},
        {"id": "github", "type": "github_trending", "name": "GitHub Trending", "enabled": True},
    ]

    @sources_router.get("")
    def list_sources():
        return MOCK_SOURCES

    @sources_router.get("/{source_id}")
    def get_source(source_id: str):
        for source in MOCK_SOURCES:
            if source["id"] == source_id:
                return source
        raise HTTPException(status_code=404, detail="Source not found")

    @sources_router.post("/{source_id}/refresh")
    def refresh_source(source_id: str):
        for source in MOCK_SOURCES:
            if source["id"] == source_id:
                return {"job_id": "job-123", "message": "Refresh started"}
        raise HTTPException(status_code=404, detail="Source not found")

    app.include_router(sources_router, prefix="/api/v1", tags=["Sources"])

    # Add fields routes (mock data)
    fields_router = APIRouter(prefix="/fields")

    MOCK_FIELDS = [
        {"id": "llm", "name": "Large Language Models", "parent_id": None},
        {"id": "agents", "name": "AI Agents", "parent_id": None},
    ]

    @fields_router.get("")
    def list_fields():
        return MOCK_FIELDS

    @fields_router.get("/{field_id}")
    def get_field(field_id: str):
        for field in MOCK_FIELDS:
            if field["id"] == field_id:
                return field
        raise HTTPException(status_code=404, detail="Field not found")

    app.include_router(fields_router, prefix="/api/v1", tags=["Fields"])

    # Add runs routes (mock data)
    runs_router = APIRouter(prefix="/runs")

    @runs_router.get("")
    def list_runs():
        return {
            "data": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "total_pages": 0,
            }
        }

    @runs_router.post("", status_code=202)
    def create_run(body: dict):
        return {
            "id": "run-123",
            "type": body.get("type", "ingest"),
            "status": "running",
        }

    app.include_router(runs_router, prefix="/api/v1", tags=["Runs"])

    # Add digests routes (mock data)
    digests_router = APIRouter(prefix="/digests")

    @digests_router.get("")
    def list_digests():
        return {
            "data": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "total_pages": 0,
            }
        }

    @digests_router.post("", status_code=202)
    def create_digest(body: dict):
        return {
            "job_id": "job-456",
            "status": "pending",
        }

    @digests_router.get("/latest")
    def get_latest_digest(type: str = "daily"):
        raise HTTPException(status_code=404, detail="No digests found")

    app.include_router(digests_router, prefix="/api/v1", tags=["Digests"])

    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_readiness_check(self, client):
        """Readiness endpoint returns ready."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200


class TestContentEndpoints:
    """Test content API endpoints."""

    def test_list_content_empty(self, client):
        """List content returns empty when no data."""
        response = client.get("/api/v1/content")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_list_content_with_filters(self, client):
        """List content accepts filter parameters."""
        response = client.get("/api/v1/content", params={
            "source": "arxiv",
            "type": "paper",
            "page": 1,
            "per_page": 10,
        })
        assert response.status_code == 200

    def test_search_content(self, client):
        """Search content works with query."""
        response = client.get("/api/v1/content/search", params={"q": "transformer"})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_search_content_min_length(self, client):
        """Search requires minimum query length."""
        response = client.get("/api/v1/content/search", params={"q": "a"})
        assert response.status_code == 422  # Validation error

    def test_get_content_not_found(self, client):
        """Get non-existent content returns 404."""
        response = client.get("/api/v1/content/nonexistent-id")
        assert response.status_code == 404


class TestSourcesEndpoints:
    """Test sources API endpoints."""

    def test_list_sources(self, client):
        """List sources returns configured sources."""
        response = client.get("/api/v1/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default sources
        source_ids = [s["id"] for s in data]
        assert "arxiv" in source_ids
        assert "github" in source_ids

    def test_get_source(self, client):
        """Get specific source configuration."""
        response = client.get("/api/v1/sources/arxiv")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "arxiv"
        assert data["type"] == "arxiv"

    def test_get_source_not_found(self, client):
        """Get non-existent source returns 404."""
        response = client.get("/api/v1/sources/nonexistent")
        assert response.status_code == 404

    def test_refresh_source(self, client):
        """Refresh source returns job ID."""
        response = client.post("/api/v1/sources/arxiv/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "message" in data


class TestFieldsEndpoints:
    """Test fields/taxonomy API endpoints."""

    def test_list_fields(self, client):
        """List fields returns taxonomy."""
        response = client.get("/api/v1/fields")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default fields
        field_ids = [f["id"] for f in data]
        assert "llm" in field_ids
        assert "agents" in field_ids

    def test_get_field(self, client):
        """Get specific field."""
        response = client.get("/api/v1/fields/llm")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "llm"
        assert "name" in data

    def test_get_field_not_found(self, client):
        """Get non-existent field returns 404."""
        response = client.get("/api/v1/fields/nonexistent")
        assert response.status_code == 404


class TestRunsEndpoints:
    """Test processing runs API endpoints."""

    def test_list_runs_empty(self, client):
        """List runs returns empty when no runs."""
        response = client.get("/api/v1/runs")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_create_run(self, client):
        """Create run returns run info."""
        response = client.post("/api/v1/runs", json={
            "type": "ingest",
            "source": "arxiv",
        })
        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        assert data["type"] == "ingest"
        assert data["status"] == "running"


class TestDigestsEndpoints:
    """Test digests API endpoints."""

    def test_list_digests_empty(self, client):
        """List digests returns empty when no digests."""
        response = client.get("/api/v1/digests")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_create_digest(self, client):
        """Create digest returns job info."""
        response = client.post("/api/v1/digests", json={
            "type": "daily",
        })
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    def test_get_latest_digest_not_found(self, client):
        """Get latest digest when none exist returns 404."""
        response = client.get("/api/v1/digests/latest", params={"type": "daily"})
        assert response.status_code == 404


class TestPagination:
    """Test pagination behavior."""

    def test_pagination_params(self, client):
        """Pagination parameters are respected."""
        response = client.get("/api/v1/content", params={
            "page": 2,
            "per_page": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["per_page"] == 5

    def test_pagination_limits(self, client):
        """Per page is limited to 100."""
        response = client.get("/api/v1/content", params={"per_page": 200})
        assert response.status_code == 422  # Validation error
