"""API tests for PromptLab

These tests verify the API endpoints work correctly.
Students should expand these tests significantly in Week 3.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient


class TestHealth:
    """Tests for health endpoint."""
    
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPrompts:
    """Tests for prompt endpoints."""
    
    def test_create_prompt(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert "id" in data
        assert "created_at" in data
    
    def test_list_prompts_empty(self, client: TestClient):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0
    
    def test_list_prompts_with_data(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        client.post("/prompts", json=sample_prompt_data)
        
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["prompts"]) == 1
        assert data["total"] == 1
    
    def test_get_prompt_success(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        response = client.get(f"/prompts/{prompt_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
    
    def test_get_prompt_not_found(self, client: TestClient):
        """Test that getting a non-existent prompt returns 404.
        
        NOTE: This test currently FAILS due to Bug #1!
        The API returns 500 instead of 404.
        """
        response = client.get("/prompts/nonexistent-id")
        # This should be 404, but there's a bug...
        assert response.status_code == 404  # Will fail until bug is fixed
    
    def test_delete_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/prompts/{prompt_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/prompts/{prompt_id}")
        # Note: This might fail due to Bug #1
        assert get_response.status_code in [404, 500]  # 404 after fix
    
    def test_update_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]
        
        # Update it
        updated_data = {
            "title": "Updated Title",
            "content": "Updated content for the prompt",
            "description": "Updated description"
        }
        
        import time
        time.sleep(0.1)  # Small delay to ensure timestamp would change
        
        response = client.put(f"/prompts/{prompt_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        
        # NOTE: This assertion will fail due to Bug #2!
        # The updated_at should be different from original
        # assert data["updated_at"] != original_updated_at  # Uncomment after fix
    
    def test_update_prompt_refreshes_updated_at(self, client: TestClient, sample_prompt_data):
        """Verify that PUT /prompts/{id} refreshes updated_at and preserves created_at.

        Covers Bug #2. The comparison is deliberately made between updated_at
        *before* the PUT and updated_at *after* it: created_at and updated_at
        already differ at creation time, because models.Prompt fills them with
        two separate default_factory calls, so asserting updated_at > created_at
        would pass even with the bug present. No sleep is needed -- utcnow() was
        measured to resolve to a few microseconds on this platform.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()
        original_created_at = datetime.fromisoformat(created["created_at"])
        original_updated_at = datetime.fromisoformat(created["updated_at"])

        response = client.put(
            f"/prompts/{created['id']}",
            json={
                "title": "Updated Title",
                "content": "Updated content for the prompt",
                "description": "Updated description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content for the prompt"

        assert datetime.fromisoformat(data["updated_at"]) > original_updated_at
        assert datetime.fromisoformat(data["created_at"]) == original_created_at

    def test_sorting_order(self, client: TestClient):
        """Test that prompts are sorted newest first.
        
        NOTE: This test might fail due to Bug #3!
        """
        import time
        
        # Create prompts with delay
        prompt1 = {"title": "First", "content": "First prompt content"}
        prompt2 = {"title": "Second", "content": "Second prompt content"}
        
        client.post("/prompts", json=prompt1)
        time.sleep(0.1)
        client.post("/prompts", json=prompt2)
        
        response = client.get("/prompts")
        prompts = response.json()["prompts"]
        
        # Newest (Second) should be first
        assert prompts[0]["title"] == "Second"  # Will fail until Bug #3 fixed


class TestCollections:
    """Tests for collection endpoints."""
    
    def test_create_collection(self, client: TestClient, sample_collection_data):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert "id" in data
    
    def test_list_collections(self, client: TestClient, sample_collection_data):
        client.post("/collections", json=sample_collection_data)
        
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert len(data["collections"]) == 1
    
    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404
    
    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data, sample_prompt_data):
        """Test deleting a collection that has prompts.

        Updated after fixing Bug #4, as this test's original docstring
        instructed. The chosen strategy is to null the prompt's collection_id
        (see the delete_collection docstring in app/api.py), so the prompt must
        survive the deletion with collection_id set to None.
        """
        # Create collection
        col_response = client.post("/collections", json=sample_collection_data)
        collection_id = col_response.json()["id"]
        
        # Create prompt in collection
        prompt_data = {**sample_prompt_data, "collection_id": collection_id}
        prompt_response = client.post("/prompts", json=prompt_data)
        prompt_id = prompt_response.json()["id"]
        
        # Delete collection
        client.delete(f"/collections/{collection_id}")
        
        # The prompt survives the deletion, unfiled rather than orphaned.
        prompts = client.get("/prompts").json()["prompts"]
        assert len(prompts) == 1
        assert prompts[0]["id"] == prompt_id
        assert prompts[0]["collection_id"] is None

    def test_delete_collection_leaves_no_dangling_reference(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        """Verify that unfiling leaves no way to reach the deleted collection.

        The test owed by the brief for Bug #4. It covers what
        test_delete_collection_with_prompts does not: that the unfiled prompt is
        still individually retrievable, that filtering by the dead collection id
        now matches nothing, and that the collection itself is gone.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        collection_id = client.post(
            "/collections", json=sample_collection_data
        ).json()["id"]
        prompt_id = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()["id"]

        assert (
            len(client.get(f"/prompts?collection_id={collection_id}").json()["prompts"])
            == 1
        )

        assert client.delete(f"/collections/{collection_id}").status_code == 204

        # The prompt is intact, with its required fields untouched.
        prompt = client.get(f"/prompts/{prompt_id}")
        assert prompt.status_code == 200
        assert prompt.json()["title"] == sample_prompt_data["title"]
        assert prompt.json()["content"] == sample_prompt_data["content"]
        assert prompt.json()["collection_id"] is None

        # The dead id no longer matches anything, and the collection is gone.
        filtered = client.get(f"/prompts?collection_id={collection_id}").json()
        assert filtered["prompts"] == []
        assert filtered["total"] == 0
        assert client.get(f"/collections/{collection_id}").status_code == 404
