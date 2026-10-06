"""API tests for PromptLab

These tests verify the API endpoints work correctly.
Students should expand these tests significantly in Week 3.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient


# The message Pydantic gives for a tag that breaks the ``Tag`` pattern (AC-2.3).
PATTERN_MSG = "String should match pattern '^[a-z0-9]+(-[a-z0-9]+)*$'"

# The message for a ``tag`` query value that breaks the ``TagQuery`` pattern (AC-3.7).
QUERY_PATTERN_MSG = "String should match pattern '^([a-z0-9]+(-[a-z0-9]+)*)?$'"


class TestHealth:
    """Tests for health endpoint."""
    
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 201
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

    # --- create_prompt: error cases ---

    def test_create_prompt_unknown_collection(self, client: TestClient, sample_prompt_data):
        """Verify a ``collection_id`` naming no collection is a 400 and stores nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.post("/prompts", json={**sample_prompt_data, "collection_id": "nope"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Collection not found"}
        assert client.get("/prompts").json()["total"] == 0

    def test_create_prompt_with_tags(self, client: TestClient, sample_prompt_data):
        """Verify tags sent on POST are returned and stored in the order sent.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.post(
            "/prompts", json={**sample_prompt_data, "tags": ["code-review", "ai"]}
        )

        assert response.status_code == 201
        assert response.json()["tags"] == ["code-review", "ai"]
        stored = client.get(f"/prompts/{response.json()['id']}").json()
        assert stored["tags"] == ["code-review", "ai"]

    def test_create_prompt_without_tags(self, client: TestClient, sample_prompt_data):
        """Verify a POST without ``tags`` stores an empty list.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, with no tags.
        """
        response = client.post("/prompts", json=sample_prompt_data)

        assert response.status_code == 201
        assert client.get(f"/prompts/{response.json()['id']}").json()["tags"] == []

    def test_create_prompt_null_tags(self, client: TestClient, sample_prompt_data):
        """Verify ``"tags": null`` on POST is a 422 that stores nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.post("/prompts", json={**sample_prompt_data, "tags": None})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "tags"]
        assert error["msg"] == "Input should be a valid list"
        assert client.get("/prompts").json()["total"] == 0

    def test_create_prompt_unknown_collection_keeps_nothing(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify valid tags with an unknown ``collection_id`` are a 400 that stores nothing.

        Passes before tags exist too: it guards the check running before the
        prompt is stored.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.post(
            "/prompts",
            json={**sample_prompt_data, "tags": ["ai"], "collection_id": "nope"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Collection not found"}
        assert client.get("/prompts").json()["total"] == 0

    @pytest.mark.parametrize("field", ["title", "content"])
    def test_create_prompt_missing_required_field(
        self, client: TestClient, sample_prompt_data, field
    ):
        """Verify leaving out a required field is a 422 naming that field.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            field: The required field left out of the body.
        """
        body = {k: v for k, v in sample_prompt_data.items() if k != field}

        response = client.post("/prompts", json=body)

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert error["msg"] == "Field required"
        assert client.get("/prompts").json()["total"] == 0

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("title", "", "String should have at least 1 character"),
            ("title", "a" * 201, "String should have at most 200 characters"),
            ("content", "", "String should have at least 1 character"),
            ("description", "d" * 501, "String should have at most 500 characters"),
        ],
    )
    def test_create_prompt_length_rule_broken(
        self, client: TestClient, sample_prompt_data, field, value, msg
    ):
        """Verify each length constraint of ``PromptBase`` is enforced with a 422.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            field: The field given an out-of-range value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        response = client.post("/prompts", json={**sample_prompt_data, field: value})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert error["msg"] == msg
        assert client.get("/prompts").json()["total"] == 0

    @pytest.mark.parametrize(
        "tag, msg",
        [
            ("Python", PATTERN_MSG),
            ("code review", PATTERN_MSG),
            ("-ai", PATTERN_MSG),
            ("ai-", PATTERN_MSG),
            ("a--b", PATTERN_MSG),
            ("", "String should have at least 1 character"),
            ("a" * 33, "String should have at most 32 characters"),
        ],
    )
    def test_create_prompt_invalid_tag(
        self, client: TestClient, sample_prompt_data, tag, msg
    ):
        """Verify a tag breaking the ``Tag`` rules is a 422 at its index that stores nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            tag: The bad tag, sent as the only one.
            msg: The message Pydantic reports for it.
        """
        response = client.post("/prompts", json={**sample_prompt_data, "tags": [tag]})

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert len(detail) == 1
        assert detail[0]["loc"] == ["body", "tags", 0]
        assert detail[0]["msg"] == msg
        assert client.get("/prompts").json()["total"] == 0

    def test_create_prompt_repeated_tag(self, client: TestClient, sample_prompt_data):
        """Verify a tag sent twice on POST is a 422 on the list that stores nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai", "ai"]})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "tags"]
        assert error["msg"] == "Value error, tags must not repeat a tag"
        assert client.get("/prompts").json()["total"] == 0

    def test_create_prompt_too_many_tags(self, client: TestClient, sample_prompt_data):
        """Verify 11 distinct tags on POST are a 422 on the list that stores nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        tags = [f"t{i}" for i in range(11)]

        response = client.post("/prompts", json={**sample_prompt_data, "tags": tags})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "tags"]
        assert error["msg"] == (
            "Value error, a prompt can have at most 10 tags; delete a tag before including another"
        )
        assert client.get("/prompts").json()["total"] == 0

    # --- create_prompt: edge cases ---

    def test_create_prompt_length_limits_inclusive(self, client: TestClient):
        """Verify a title of exactly 200 and a description of exactly 500 are accepted.

        Args:
            client: FastAPI test client fixture.
        """
        body = {"title": "a" * 200, "content": "Text.", "description": "d" * 500}

        response = client.post("/prompts", json=body)

        assert response.status_code == 201
        assert response.json()["title"] == body["title"]
        assert response.json()["description"] == body["description"]

    @pytest.mark.parametrize("tags", [["a" * 32], [f"t{i}" for i in range(10)]])
    def test_create_prompt_tags_at_limits(
        self, client: TestClient, sample_prompt_data, tags
    ):
        """Verify tags at the ``Tag`` and list limits are accepted and stored in order.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            tags: Tags at a limit: one of exactly 32 characters, or 10 tags.
        """
        response = client.post("/prompts", json={**sample_prompt_data, "tags": tags})

        assert response.status_code == 201
        assert client.get(f"/prompts/{response.json()['id']}").json()["tags"] == tags

    def test_create_prompt_optional_fields_default_to_null(self, client: TestClient):
        """Verify an omitted ``description`` and ``collection_id`` are stored as null.

        Args:
            client: FastAPI test client fixture.
        """
        created = client.post("/prompts", json={"title": "T", "content": "Text."}).json()

        stored = client.get(f"/prompts/{created['id']}").json()
        assert stored["description"] is None
        assert stored["collection_id"] is None

    def test_create_prompt_ignores_server_fields(self, client: TestClient):
        """Verify a client cannot choose the ``id`` or ``created_at`` of a new prompt.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.post(
            "/prompts",
            json={
                "title": "T",
                "content": "Text.",
                "id": "mine",
                "created_at": "2000-01-01T00:00:00",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] != "mine"
        assert datetime.fromisoformat(data["created_at"]).year != 2000
        assert client.get("/prompts/mine").status_code == 404

    def test_create_prompt_empty_collection_id_stored_unchecked(self, client: TestClient):
        """Verify ``"collection_id": ""`` is stored as is, without a lookup.

        Pins a documented known issue (``docs/API_REFERENCE.md``, *Known
        issues*): ``create_prompt`` tests the id by truthiness, so the empty
        string skips the collection check. A fix must change this test on
        purpose.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.post(
            "/prompts", json={"title": "T", "content": "Text.", "collection_id": ""}
        )

        assert response.status_code == 201
        stored = client.get(f"/prompts/{response.json()['id']}").json()
        assert stored["collection_id"] == ""

    def test_create_prompt_whitespace_title_accepted(self, client: TestClient):
        """Verify a title made only of spaces passes ``min_length=1``.

        Values are not stripped, so three spaces count as three characters.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.post("/prompts", json={"title": "   ", "content": "Text."})

        assert response.status_code == 201
        stored = client.get(f"/prompts/{response.json()['id']}").json()
        assert stored["title"] == "   "

    def test_create_prompt_stored_equals_response(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify the 201 body is what was stored, read back with GET.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]

        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()

        assert created["collection_id"] == collection_id
        assert client.get(f"/prompts/{created['id']}").json() == created

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

    def test_list_prompts_shows_tags(self, client: TestClient, sample_prompt_data):
        """Verify each listed prompt carries its own tags.

        Prompts are matched by title, not position, so the order of the list
        does not matter.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        client.post("/prompts", json={**sample_prompt_data, "title": "A", "tags": ["ai"]})
        client.post("/prompts", json={**sample_prompt_data, "title": "B", "tags": ["python"]})

        response = client.get("/prompts")

        assert response.status_code == 200
        tags_by_title = {p["title"]: p["tags"] for p in response.json()["prompts"]}
        assert tags_by_title == {"A": ["ai"], "B": ["python"]}

    # --- list_prompts: query parameters ---

    def test_list_prompts_search_matches_title_ignoring_case(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify ``search`` matches the title whatever the case of the query.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, titled
                "Code Review Prompt".
        """
        match = client.post("/prompts", json=sample_prompt_data).json()
        client.post("/prompts", json={"title": "Summarise", "content": "Summarise the text."})

        data = client.get("/prompts?search=CODE").json()

        assert [p["id"] for p in data["prompts"]] == [match["id"]]
        assert data["total"] == 1

    def test_list_prompts_search_matches_description(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify ``search`` also matches text found only in the description.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, used as the
                prompt that must not match.
        """
        client.post("/prompts", json=sample_prompt_data)
        match = client.post(
            "/prompts",
            json={
                "title": "Summarise",
                "content": "Summarise the text.",
                "description": "Condense a meeting transcript",
            },
        ).json()

        data = client.get("/prompts?search=transcript").json()

        assert [p["id"] for p in data["prompts"]] == [match["id"]]
        assert data["total"] == 1

    def test_list_prompts_filter_by_collection(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify ``collection_id`` keeps only the prompts filed in that collection.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        filed = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()
        client.post("/prompts", json=sample_prompt_data)

        data = client.get(f"/prompts?collection_id={collection_id}").json()

        assert [p["id"] for p in data["prompts"]] == [filed["id"]]
        assert data["total"] == 1

    def test_list_prompts_filter_by_collection_and_search(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify ``collection_id`` and ``search`` combine: a prompt must pass both.

        Three prompts: two in the collection, of which only one matches the
        search, and one outside the collection that also matches it.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, titled
                "Code Review Prompt".
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        match = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()
        client.post(
            "/prompts",
            json={"title": "Summarise", "content": "Summarise.", "collection_id": collection_id},
        )
        client.post("/prompts", json=sample_prompt_data)

        data = client.get(f"/prompts?collection_id={collection_id}&search=review").json()

        assert [p["id"] for p in data["prompts"]] == [match["id"]]
        assert data["total"] == 1

    @pytest.mark.parametrize(
        "query, expected",
        [
            ("tag=ai", ["P2", "P1"]),
            ("tag=ai&tag=code-review", ["P1"]),
            ("tag=rust", []),
            ("tag=ai&tag=ai", ["P2", "P1"]),
        ],
    )
    def test_list_prompts_by_tag(self, client: TestClient, tagged_prompts, query, expected):
        """Verify ``tag`` keeps the prompts carrying every tag given, newest first.

        Args:
            client: FastAPI test client fixture.
            tagged_prompts: Fixture creating P1 to P3 with their tags.
            query: The ``tag`` values sent.
            expected: The names of the prompts listed, in order.
        """
        response = client.get(f"/prompts?{query}")

        assert response.status_code == 200
        data = response.json()
        assert [p["id"] for p in data["prompts"]] == [tagged_prompts[n] for n in expected]
        assert data["total"] == len(expected)

    def test_list_prompts_by_tag_and_collection(
        self, client: TestClient, tagged_prompts, sample_collection_data
    ):
        """Verify ``tag`` and ``collection_id`` combine: a prompt must pass both.

        Args:
            client: FastAPI test client fixture.
            tagged_prompts: Fixture creating P1 to P3 with their tags.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        client.patch(f"/prompts/{tagged_prompts['P1']}", json={"collection_id": collection_id})

        response = client.get(f"/prompts?tag=ai&collection_id={collection_id}")

        assert response.status_code == 200
        data = response.json()
        assert [p["id"] for p in data["prompts"]] == [tagged_prompts["P1"]]
        assert data["total"] == 1

    def test_list_prompts_by_tag_and_search(self, client: TestClient, tagged_prompts):
        """Verify ``tag`` and ``search`` combine: a prompt must pass both.

        Args:
            client: FastAPI test client fixture.
            tagged_prompts: Fixture creating P1 to P3 with their tags, titled
                by their names.
        """
        response = client.get("/prompts?tag=ai&search=P2")

        assert response.status_code == 200
        data = response.json()
        assert [p["id"] for p in data["prompts"]] == [tagged_prompts["P2"]]
        assert data["total"] == 1

    @pytest.mark.parametrize(
        "query, expected",
        [
            ("tag=", ["P3", "P2", "P1"]),
            ("tag=ai&tag=", ["P2", "P1"]),
        ],
    )
    def test_list_prompts_empty_tag_ignored(
        self, client: TestClient, tagged_prompts, query, expected
    ):
        """Verify an empty ``tag`` value is dropped, as if it were not sent.

        Args:
            client: FastAPI test client fixture.
            tagged_prompts: Fixture creating P1 to P3 with their tags.
            query: The ``tag`` values sent, one of them empty.
            expected: The names of the prompts listed, in order.
        """
        response = client.get(f"/prompts?{query}")

        assert response.status_code == 200
        data = response.json()
        assert [p["id"] for p in data["prompts"]] == [tagged_prompts[n] for n in expected]
        assert data["total"] == len(expected)

    def test_list_prompts_without_tag(self, client: TestClient, tagged_prompts):
        """Verify a request with no ``tag`` lists every prompt, newest first.

        Args:
            client: FastAPI test client fixture.
            tagged_prompts: Fixture creating P1 to P3 with their tags.
        """
        response = client.get("/prompts")

        assert response.status_code == 200
        data = response.json()
        assert [p["id"] for p in data["prompts"]] == [
            tagged_prompts[n] for n in ["P3", "P2", "P1"]
        ]
        assert data["total"] == 3

    @pytest.mark.parametrize(
        "query, index, msg",
        [
            ("tag=Python", 0, QUERY_PATTERN_MSG),
            ("tag=ai&tag=Python", 1, QUERY_PATTERN_MSG),
            ("tag=" + "a" * 33, 0, "String should have at most 32 characters"),
        ],
    )
    def test_list_prompts_invalid_tag(self, client: TestClient, query, index, msg):
        """Verify a ``tag`` value breaking the ``TagQuery`` rules is a 422 at its index.

        Args:
            client: FastAPI test client fixture.
            query: The ``tag`` values sent, one of them invalid.
            index: The position of the invalid value.
            msg: The message Pydantic reports for it.
        """
        response = client.get(f"/prompts?{query}")

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["query", "tag", index]
        assert error["msg"] == msg

    # --- list_prompts: error cases (a filter that matches nothing is not an error) ---

    @pytest.mark.parametrize("query", ["search=zzz", "collection_id=nope"])
    def test_list_prompts_no_match_returns_empty(
        self, client: TestClient, sample_prompt_data, query
    ):
        """Verify a filter that matches nothing gives 200 with an empty list.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            query: A search with no match, or an unknown collection id.
        """
        client.post("/prompts", json=sample_prompt_data)

        response = client.get(f"/prompts?{query}")

        assert response.status_code == 200
        assert response.json() == {"prompts": [], "total": 0}

    # --- list_prompts: edge cases ---

    def test_list_prompts_search_ignores_content(self, client: TestClient):
        """Verify ``search`` does not look in the prompt's content.

        Args:
            client: FastAPI test client fixture.
        """
        client.post("/prompts", json={"title": "Summarise", "content": "Use bullet points."})

        data = client.get("/prompts?search=bullet").json()

        assert data == {"prompts": [], "total": 0}

    @pytest.mark.parametrize("query", ["search=", "collection_id=", "search=&collection_id="])
    def test_list_prompts_empty_query_value_ignored(
        self, client: TestClient, sample_prompt_data, query
    ):
        """Verify an empty query value is treated as absent, not as a filter.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            query: One or both parameters sent with an empty value.
        """
        client.post("/prompts", json=sample_prompt_data)
        client.post("/prompts", json={"title": "Summarise", "content": "Summarise."})

        data = client.get(f"/prompts?{query}").json()

        assert data["total"] == 2
        assert len(data["prompts"]) == 2

    def test_list_prompts_newest_first(self, client: TestClient, ticking_clock):
        """Verify prompts are listed by ``created_at``, newest first, with no sleep.

        Args:
            client: FastAPI test client fixture.
            ticking_clock: Gives every timestamp a distinct value, so the
                ordering cannot be broken by a coarse platform clock.
        """
        ids = [
            client.post("/prompts", json={"title": f"P{i}", "content": "Text."}).json()["id"]
            for i in range(3)
        ]

        prompts = client.get("/prompts").json()["prompts"]

        assert [p["id"] for p in prompts] == list(reversed(ids))
        created = [datetime.fromisoformat(p["created_at"]) for p in prompts]
        assert created[0] > created[1] > created[2]

    def test_get_prompt_success(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        response = client.get(f"/prompts/{prompt_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
    
    def test_get_prompt_not_found(self, client: TestClient):
        """Test that getting a non-existent prompt returns 404."""
        response = client.get("/prompts/nonexistent-id")
        assert response.status_code == 404

    # --- get_prompt: error cases ---

    def test_get_prompt_not_found_detail(self, client: TestClient):
        """Verify the 404 for an unknown id carries the documented message.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.get("/prompts/nonexistent-id")

        assert response.status_code == 404
        assert response.json() == {"detail": "Prompt not found"}

    # --- get_prompt: edge cases ---

    def test_get_prompt_returns_the_requested_one(self, client: TestClient):
        """Verify the lookup returns the prompt with that id, not just any prompt.

        Args:
            client: FastAPI test client fixture.
        """
        created = [
            client.post("/prompts", json={"title": f"P{i}", "content": "Text."}).json()
            for i in range(3)
        ]

        response = client.get(f"/prompts/{created[1]['id']}")

        assert response.status_code == 200
        assert response.json() == created[1]

    def test_get_prompt_id_is_case_sensitive(self, client: TestClient, sample_prompt_data):
        """Verify ids match exactly: the same id in upper case names nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        prompt_id = client.post("/prompts", json=sample_prompt_data).json()["id"]

        response = client.get(f"/prompts/{prompt_id.upper()}")

        assert response.status_code == 404

    def test_delete_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/prompts/{prompt_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/prompts/{prompt_id}")
        assert get_response.status_code in [404, 500]

    # --- delete_prompt: error cases ---

    def test_delete_prompt_not_found(self, client: TestClient):
        """Verify deleting an unknown id is a 404 with the documented message.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.delete("/prompts/nonexistent-id")

        assert response.status_code == 404
        assert response.json() == {"detail": "Prompt not found"}

    def test_delete_prompt_twice(self, client: TestClient, sample_prompt_data):
        """Verify a second delete of the same prompt is a 404, not a silent 204.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        prompt_id = client.post("/prompts", json=sample_prompt_data).json()["id"]

        assert client.delete(f"/prompts/{prompt_id}").status_code == 204
        assert client.delete(f"/prompts/{prompt_id}").status_code == 404

    # --- delete_prompt: edge cases ---

    def test_delete_prompt_then_get_is_404(self, client: TestClient, sample_prompt_data):
        """Verify a deleted prompt is a 404 on GET, exactly.

        The provided ``test_delete_prompt`` accepts 404 or 500 for this check,
        so it would pass if the lookup crashed; this test does not.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        prompt_id = client.post("/prompts", json=sample_prompt_data).json()["id"]
        client.delete(f"/prompts/{prompt_id}")

        response = client.get(f"/prompts/{prompt_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Prompt not found"}

    def test_delete_prompt_empty_body(self, client: TestClient, sample_prompt_data):
        """Verify the 204 response carries no body.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        prompt_id = client.post("/prompts", json=sample_prompt_data).json()["id"]

        response = client.delete(f"/prompts/{prompt_id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_prompt_leaves_others(self, client: TestClient, sample_prompt_data):
        """Verify deleting one prompt removes only that one.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        doomed = client.post("/prompts", json=sample_prompt_data).json()["id"]
        kept = client.post("/prompts", json=sample_prompt_data).json()

        client.delete(f"/prompts/{doomed}")

        data = client.get("/prompts").json()
        assert [p["id"] for p in data["prompts"]] == [kept["id"]]
        assert data["total"] == 1
        assert client.get(f"/prompts/{kept['id']}").json() == kept

    def test_delete_prompt_keeps_its_collection(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify deleting a filed prompt does not touch the collection it was in.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection = client.post("/collections", json=sample_collection_data).json()
        prompt_id = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection["id"]}
        ).json()["id"]

        client.delete(f"/prompts/{prompt_id}")

        response = client.get(f"/collections/{collection['id']}")
        assert response.status_code == 200
        assert response.json() == collection

    def test_update_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
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
    
    def test_update_prompt_refreshes_updated_at(
        self, client: TestClient, sample_prompt_data, ticking_clock
    ):
        """Verify that PUT /prompts/{id} refreshes updated_at and preserves created_at.

        Covers Bug #2. The comparison is deliberately made between updated_at
        *before* the PUT and updated_at *after* it: created_at and updated_at
        can already differ at creation time, because models.Prompt fills them
        with two separate default_factory calls, so asserting updated_at >
        created_at could pass even with the bug present. No sleep is used: the
        ticking clock gives the PUT a later timestamp than the create.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            ticking_clock: Gives every timestamp a distinct value, so a coarse
                platform clock cannot make the two equal.
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

    # --- update_prompt: error cases ---

    def test_update_prompt_not_found(self, client: TestClient, sample_prompt_data):
        """Verify PUT on an unknown id is a 404, not a silent create.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        response = client.put("/prompts/nonexistent-id", json=sample_prompt_data)

        assert response.status_code == 404
        assert response.json() == {"detail": "Prompt not found"}
        assert client.get("/prompts").json()["total"] == 0

    def test_update_prompt_unknown_collection(self, client: TestClient, sample_prompt_data):
        """Verify a ``collection_id`` naming no collection is a 400 that changes nothing.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.put(
            f"/prompts/{created['id']}",
            json={"title": "New", "content": "New text.", "collection_id": "nope"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Collection not found"}
        assert client.get(f"/prompts/{created['id']}").json() == created

    @pytest.mark.parametrize("method", ["PUT", "PATCH"])
    def test_update_prompt_unknown_collection_keeps_tags(
        self, client: TestClient, sample_prompt_data, method
    ):
        """Verify valid tags with an unknown ``collection_id`` are a 400 that keeps the stored tags.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            method: The editing method, PUT or PATCH.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.request(
            method,
            f"/prompts/{created['id']}",
            json={
                "title": "New",
                "content": "New text.",
                "tags": ["python"],
                "collection_id": "nope",
            },
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Collection not found"}
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["ai"]

    @pytest.mark.parametrize("method", ["PUT", "PATCH"])
    def test_update_prompt_invalid_tag_keeps_tags(
        self, client: TestClient, sample_prompt_data, method
    ):
        """Verify a bad tag sent on an edit is a 422 that keeps the stored tags.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            method: The editing method, PUT or PATCH.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.request(
            method,
            f"/prompts/{created['id']}",
            json={"title": "New", "content": "New text.", "tags": ["Python"]},
        )

        assert response.status_code == 422
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["ai"]

    @pytest.mark.parametrize(
        "body, field, msg",
        [
            ({"content": "New text."}, "title", "Field required"),
            ({"title": "New"}, "content", "Field required"),
            ({"title": "", "content": "New text."}, "title",
             "String should have at least 1 character"),
        ],
    )
    def test_update_prompt_invalid_body(
        self, client: TestClient, sample_prompt_data, body, field, msg
    ):
        """Verify an incomplete or invalid replacement body is a 422 that changes nothing.

        PUT replaces the whole prompt, so a body without ``title`` or
        ``content`` is refused rather than merged.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            body: The replacement body sent.
            field: The field the error names.
            msg: The message Pydantic reports for it.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.put(f"/prompts/{created['id']}", json=body)

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert error["msg"] == msg
        assert client.get(f"/prompts/{created['id']}").json() == created

    # --- update_prompt: edge cases ---

    def test_update_prompt_validation_before_lookup(self, client: TestClient):
        """Verify the order of checks: body 422 before path 404, path 404 before body 400.

        Args:
            client: FastAPI test client fixture.
        """
        invalid_body = client.put("/prompts/nonexistent-id", json={"content": "Text."})
        assert invalid_body.status_code == 422

        unknown_both = client.put(
            "/prompts/nonexistent-id",
            json={"title": "T", "content": "Text.", "collection_id": "nope"},
        )
        assert unknown_both.status_code == 404
        assert unknown_both.json() == {"detail": "Prompt not found"}

    def test_update_prompt_omitted_fields_reset(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify optional fields left out of a PUT are reset to null, not kept.

        Leaving out ``collection_id`` therefore unfiles the prompt.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, with a description.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()

        client.put(f"/prompts/{created['id']}", json={"title": "New", "content": "New text."})

        stored = client.get(f"/prompts/{created['id']}").json()
        assert stored["description"] is None
        assert stored["collection_id"] is None

    def test_update_prompt_without_tags_clears_them(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify a PUT without ``tags`` replaces the stored tags with an empty list.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.put(
            f"/prompts/{created['id']}", json={"title": "New", "content": "New text."}
        )

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == []

    def test_update_prompt_tags_keep_order(self, client: TestClient, sample_prompt_data):
        """Verify tags sent on PUT are stored in the order sent, not sorted.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, with no tags.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.put(
            f"/prompts/{created['id']}",
            json={"title": "New", "content": "New text.", "tags": ["b-tag", "a-tag"]},
        )

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["b-tag", "a-tag"]

    def test_update_prompt_ignores_id_in_body(self, client: TestClient, sample_prompt_data):
        """Verify an ``id`` in the body cannot change the stored prompt's id.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.put(
            f"/prompts/{created['id']}",
            json={"title": "New", "content": "New text.", "id": "other"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
        assert client.get("/prompts/other").status_code == 404

    def test_update_prompt_empty_collection_id_stored_unchecked(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify ``"collection_id": ""`` is stored as is, without a lookup.

        Pins a documented known issue (``docs/API_REFERENCE.md``, *Known
        issues*): ``update_prompt`` tests the id by truthiness. A fix must
        change this test on purpose.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.put(
            f"/prompts/{created['id']}",
            json={"title": "New", "content": "New text.", "collection_id": ""},
        )

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["collection_id"] == ""

    def test_update_prompt_moves_to_collection(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify a PUT naming another existing collection refiles the prompt there.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        first = client.post("/collections", json=sample_collection_data).json()["id"]
        second = client.post("/collections", json={"name": "Writing"}).json()["id"]
        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": first}
        ).json()

        response = client.put(
            f"/prompts/{created['id']}",
            json={**sample_prompt_data, "collection_id": second},
        )

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["collection_id"] == second

    def test_sorting_order(self, client: TestClient):
        """Test that prompts are sorted newest first."""
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
        assert prompts[0]["title"] == "Second"


    def test_patch_prompt_partial_update(
        self, client: TestClient, sample_prompt_data, ticking_clock
    ):
        """Verify PATCH changes only the fields the body carries.

        Covers three of the four behaviours the brief asks of the endpoint at
        once: only the sent field is updated, the untouched fields keep their
        stored values, and updated_at is refreshed while created_at is not.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            ticking_clock: Gives every timestamp a distinct value, so a coarse
                platform clock cannot make the two equal.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()
        original_updated_at = datetime.fromisoformat(created["updated_at"])

        # A body carrying one field only - PUT would reject this as incomplete.
        response = client.patch(
            f"/prompts/{created['id']}", json={"description": "Revised description"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["description"] == "Revised description"
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert data["id"] == created["id"]
        assert data["created_at"] == created["created_at"]
        assert datetime.fromisoformat(data["updated_at"]) > original_updated_at

        # The change is stored, not merely echoed back by the handler.
        assert client.get(f"/prompts/{created['id']}").json()["description"] == (
            "Revised description"
        )

    def test_patch_prompt_not_found(self, client: TestClient):
        """Verify PATCH on an unknown id is a 404, not a 500 or a silent create.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.patch("/prompts/nonexistent-id", json={"title": "New title"})
        assert response.status_code == 404

    @pytest.mark.parametrize("field", ["title", "content"])
    def test_patch_prompt_rejects_null_required_field(
        self, client: TestClient, sample_prompt_data, field
    ):
        """Verify PATCH rejects a null title or content with 422, storing nothing.

        A prompt cannot hold a null in either field, so the body must be refused
        before the merge rather than failing inside it as a 500.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            field: The required field sent as null.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.patch(f"/prompts/{created['id']}", json={field: None})
        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert f"{field} cannot be null" in error["msg"]

        # The rejected body left the stored prompt exactly as it was.
        assert client.get(f"/prompts/{created['id']}").json() == created

    # --- patch_prompt: error cases ---

    @pytest.mark.parametrize("collection_id", ["nope", ""])
    def test_patch_prompt_unknown_collection(
        self, client: TestClient, sample_prompt_data, collection_id
    ):
        """Verify a sent ``collection_id`` naming no collection is a 400 that changes nothing.

        The empty string is looked up too, unlike in POST and PUT, because
        PATCH checks the id with ``is not None`` (the documented
        inconsistency in ``docs/API_REFERENCE.md``, *Known issues*).

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            collection_id: An unknown id, or the empty string.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.patch(
            f"/prompts/{created['id']}", json={"collection_id": collection_id}
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Collection not found"}
        assert client.get(f"/prompts/{created['id']}").json() == created

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("title", "", "String should have at least 1 character"),
            ("title", "a" * 201, "String should have at most 200 characters"),
            ("description", "d" * 501, "String should have at most 500 characters"),
        ],
    )
    def test_patch_prompt_length_rule_broken(
        self, client: TestClient, sample_prompt_data, field, value, msg
    ):
        """Verify a sent field is held to the same length rules as on create.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            field: The field given an out-of-range value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.patch(f"/prompts/{created['id']}", json={field: value})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert error["msg"] == msg
        assert client.get(f"/prompts/{created['id']}").json() == created

    def test_patch_prompt_not_found_detail(self, client: TestClient):
        """Verify the 404 for an unknown id carries the documented message.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.patch("/prompts/nonexistent-id", json={"title": "New title"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Prompt not found"}

    # --- patch_prompt: edge cases ---

    def test_patch_prompt_empty_body_changes_nothing(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify an empty body is not an edit: even ``updated_at`` stays as it was.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.patch(f"/prompts/{created['id']}", json={})

        assert response.status_code == 200
        assert response.json() == created
        assert client.get(f"/prompts/{created['id']}").json() == created

    def test_patch_prompt_null_description_clears_it(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify an explicit null description clears it, unlike a missing key.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, with a description.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        response = client.patch(f"/prompts/{created['id']}", json={"description": None})

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["description"] is None

    def test_patch_prompt_collection_id_null_vs_absent(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify a null ``collection_id`` unfiles the prompt while an absent one keeps it.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()

        client.patch(f"/prompts/{created['id']}", json={"title": "New title"})
        assert client.get(f"/prompts/{created['id']}").json()["collection_id"] == collection_id

        client.patch(f"/prompts/{created['id']}", json={"collection_id": None})
        assert client.get(f"/prompts/{created['id']}").json()["collection_id"] is None

    def test_patch_prompt_several_fields(self, client: TestClient, sample_prompt_data):
        """Verify every sent field changes and every other field is kept.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json=sample_prompt_data).json()

        client.patch(
            f"/prompts/{created['id']}", json={"title": "New title", "content": "New text."}
        )

        stored = client.get(f"/prompts/{created['id']}").json()
        assert stored["title"] == "New title"
        assert stored["content"] == "New text."
        assert stored["description"] == created["description"]
        assert stored["collection_id"] == created["collection_id"]
        assert stored["created_at"] == created["created_at"]

    def test_patch_prompt_without_tags_keeps_them(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify a PATCH that does not send ``tags`` keeps the stored tags.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.patch(f"/prompts/{created['id']}", json={"title": "New"})

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["ai"]

    def test_patch_prompt_tags_replaced(
        self, client: TestClient, sample_prompt_data, ticking_clock
    ):
        """Verify tags sent on PATCH replace the stored ones and refresh ``updated_at``.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            ticking_clock: Gives every timestamp a distinct value, so a coarse
                platform clock cannot make the two equal.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.patch(f"/prompts/{created['id']}", json={"tags": ["python"]})

        assert response.status_code == 200
        stored = client.get(f"/prompts/{created['id']}").json()
        assert stored["tags"] == ["python"]
        assert datetime.fromisoformat(stored["updated_at"]) > datetime.fromisoformat(
            created["updated_at"]
        )

    def test_patch_prompt_empty_tags_clears_them(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify ``"tags": []`` on PATCH clears the stored tags, unlike an absent key.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.patch(f"/prompts/{created['id']}", json={"tags": []})

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == []

    def test_patch_prompt_invalid_tag_not_found(self, client: TestClient):
        """Verify a bad tag on PATCH to an unknown id is a 422, not a 404.

        The body is validated before ``patch_prompt`` looks the id up.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.patch("/prompts/nope", json={"tags": ["Python"]})

        assert response.status_code == 422

    def test_patch_prompt_null_tags(self, client: TestClient, sample_prompt_data):
        """Verify ``"tags": null`` on PATCH is a 422 that keeps the stored tags.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.patch(f"/prompts/{created['id']}", json={"tags": None})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "tags"]
        assert error["msg"] == (
            "Value error, tags cannot be null; send a value or omit the field "
            "to keep the current one"
        )
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["ai"]

    @pytest.mark.parametrize(
        "tags, msg",
        [
            (
                [f"t{i}" for i in range(11)],
                "Value error, a prompt can have at most 10 tags; "
                "delete a tag before including another",
            ),
            (["ai", "ai"], "Value error, tags must not repeat a tag"),
        ],
    )
    def test_patch_prompt_tag_list_rule_broken(
        self, client: TestClient, sample_prompt_data, tags, msg
    ):
        """Verify a tag list breaking a list rule on PATCH is a 422 that keeps the stored tags.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            tags: A list of valid tags that breaks the count or the repeat rule.
            msg: The message ``check_tag_list`` gives for it.
        """
        created = client.post("/prompts", json={**sample_prompt_data, "tags": ["ai"]}).json()

        response = client.patch(f"/prompts/{created['id']}", json={"tags": tags})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "tags"]
        assert error["msg"] == msg
        assert client.get(f"/prompts/{created['id']}").json()["tags"] == ["ai"]

    def test_patch_prompt_validation_before_lookup(self, client: TestClient):
        """Verify the order of checks: body 422 before path 404, path 404 before body 400.

        Args:
            client: FastAPI test client fixture.
        """
        null_title = client.patch("/prompts/nonexistent-id", json={"title": None})
        assert null_title.status_code == 422

        unknown_both = client.patch("/prompts/nonexistent-id", json={"collection_id": "nope"})
        assert unknown_both.status_code == 404
        assert unknown_both.json() == {"detail": "Prompt not found"}

    def test_patch_prompt_moves_to_collection(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        """Verify a PATCH naming another existing collection refiles the prompt there.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        first = client.post("/collections", json=sample_collection_data).json()["id"]
        second = client.post("/collections", json={"name": "Writing"}).json()["id"]
        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": first}
        ).json()

        response = client.patch(f"/prompts/{created['id']}", json={"collection_id": second})

        assert response.status_code == 200
        assert client.get(f"/prompts/{created['id']}").json()["collection_id"] == second


class TestCollections:
    """Tests for collection endpoints."""
    
    def test_create_collection(self, client: TestClient, sample_collection_data):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert "id" in data

    # --- create_collection: error cases ---

    def test_create_collection_missing_name(self, client: TestClient):
        """Verify a body without ``name`` is a 422 naming that field.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.post("/collections", json={"description": "No name"})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", "name"]
        assert error["msg"] == "Field required"
        assert client.get("/collections").json()["total"] == 0

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("name", "", "String should have at least 1 character"),
            ("name", "n" * 101, "String should have at most 100 characters"),
            ("description", "d" * 501, "String should have at most 500 characters"),
            ("name", None, "Input should be a valid string"),
        ],
    )
    def test_create_collection_rule_broken(
        self, client: TestClient, sample_collection_data, field, value, msg
    ):
        """Verify each constraint of ``CollectionBase`` is enforced with a 422.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            field: The field given an invalid value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        response = client.post("/collections", json={**sample_collection_data, field: value})

        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert error["loc"] == ["body", field]
        assert error["msg"] == msg
        assert client.get("/collections").json()["total"] == 0

    # --- create_collection: edge cases ---

    def test_create_collection_length_limits_inclusive(self, client: TestClient):
        """Verify a name of exactly 100 and a description of exactly 500 are accepted.

        Args:
            client: FastAPI test client fixture.
        """
        body = {"name": "n" * 100, "description": "d" * 500}

        response = client.post("/collections", json=body)

        assert response.status_code == 201
        assert response.json()["name"] == body["name"]
        assert response.json()["description"] == body["description"]

    def test_create_collection_ignores_id(self, client: TestClient):
        """Verify a client cannot choose the ``id`` of a new collection.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.post("/collections", json={"name": "X", "id": "mine"})

        assert response.status_code == 201
        assert response.json()["id"] != "mine"
        assert client.get("/collections/mine").status_code == 404

    def test_create_collection_duplicate_name_allowed(self, client: TestClient):
        """Verify names need not be unique: the same name twice makes two collections.

        Args:
            client: FastAPI test client fixture.
        """
        first = client.post("/collections", json={"name": "Same"})
        second = client.post("/collections", json={"name": "Same"})

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["id"] != second.json()["id"]
        assert client.get("/collections").json()["total"] == 2

    def test_create_collection_stored_equals_response(
        self, client: TestClient, sample_collection_data
    ):
        """Verify the 201 body is what was stored, read back with GET.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        created = client.post("/collections", json=sample_collection_data).json()

        assert client.get(f"/collections/{created['id']}").json() == created

    def test_list_collections(self, client: TestClient, sample_collection_data):
        client.post("/collections", json=sample_collection_data)
        
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert len(data["collections"]) == 1

    # --- list_collections: error cases (none documented; the empty store) ---

    def test_list_collections_empty(self, client: TestClient):
        """Verify an empty store gives 200 with an empty list, not an error.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.get("/collections")

        assert response.status_code == 200
        assert response.json() == {"collections": [], "total": 0}

    # --- list_collections: edge cases ---

    def test_list_collections_creation_order(self, client: TestClient):
        """Verify collections come back in creation order, not sorted by name.

        Args:
            client: FastAPI test client fixture.
        """
        for name in ["C", "A", "B"]:
            client.post("/collections", json={"name": name})

        collections = client.get("/collections").json()["collections"]

        assert [c["name"] for c in collections] == ["C", "A", "B"]

    def test_list_collections_total_matches_count(self, client: TestClient):
        """Verify ``total`` equals the number of collections listed.

        Args:
            client: FastAPI test client fixture.
        """
        for name in ["C", "A", "B"]:
            client.post("/collections", json={"name": name})

        data = client.get("/collections").json()

        assert data["total"] == 3
        assert len(data["collections"]) == 3

    def test_list_collections_omits_deleted(self, client: TestClient):
        """Verify a deleted collection is no longer listed.

        Args:
            client: FastAPI test client fixture.
        """
        doomed = client.post("/collections", json={"name": "Old"}).json()["id"]
        kept = client.post("/collections", json={"name": "New"}).json()
        client.delete(f"/collections/{doomed}")

        data = client.get("/collections").json()

        assert data == {"collections": [kept], "total": 1}

    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404

    # --- get_collection: success ---

    def test_get_collection_success(self, client: TestClient, sample_collection_data):
        """Verify a created collection is returned as it was stored.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        created = client.post("/collections", json=sample_collection_data).json()

        response = client.get(f"/collections/{created['id']}")

        assert response.status_code == 200
        assert response.json() == created

    # --- get_collection: error cases ---

    def test_get_collection_not_found_detail(self, client: TestClient):
        """Verify the 404 for an unknown id carries the documented message.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.get("/collections/nonexistent-id")

        assert response.status_code == 404
        assert response.json() == {"detail": "Collection not found"}

    # --- get_collection: edge cases ---

    def test_get_collection_excludes_prompts(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        """Verify the body holds only the collection's own fields, never its prompts.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        client.post("/prompts", json={**sample_prompt_data, "collection_id": collection_id})

        body = client.get(f"/collections/{collection_id}").json()

        assert set(body) == {"name", "description", "id", "created_at"}

    def test_get_collection_returns_the_requested_one(self, client: TestClient):
        """Verify the lookup returns the collection with that id, not just any one.

        Args:
            client: FastAPI test client fixture.
        """
        created = [
            client.post("/collections", json={"name": name}).json() for name in ["A", "B", "C"]
        ]

        response = client.get(f"/collections/{created[1]['id']}")

        assert response.status_code == 200
        assert response.json() == created[1]

    def test_get_collection_after_delete(self, client: TestClient, sample_collection_data):
        """Verify a deleted collection is a 404.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        client.delete(f"/collections/{collection_id}")

        response = client.get(f"/collections/{collection_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Collection not found"}

    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data, sample_prompt_data):
        """Test deleting a collection that has prompts.

        Updated after fixing Bug #4, as this test's original docstring
        instructed. The chosen strategy is to unfile the prompt by clearing its
        collection_id rather than to delete it, so the prompt must survive the
        deletion of its collection with collection_id set to None.
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

    # --- delete_collection: error cases ---

    def test_delete_collection_not_found(self, client: TestClient):
        """Verify deleting an unknown id is a 404 with the documented message.

        Args:
            client: FastAPI test client fixture.
        """
        response = client.delete("/collections/nonexistent-id")

        assert response.status_code == 404
        assert response.json() == {"detail": "Collection not found"}

    def test_delete_collection_twice(self, client: TestClient, sample_collection_data):
        """Verify a second delete of the same collection is a 404.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]

        assert client.delete(f"/collections/{collection_id}").status_code == 204
        assert client.delete(f"/collections/{collection_id}").status_code == 404

    # --- delete_collection: edge cases ---

    def test_delete_collection_keeps_prompt_updated_at(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        """Verify unfiling is not an edit: the prompt's ``updated_at`` is unchanged.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        created = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
        ).json()

        client.delete(f"/collections/{collection_id}")

        stored = client.get(f"/prompts/{created['id']}").json()
        assert stored["updated_at"] == created["updated_at"]

    def test_delete_collection_unfiles_only_its_prompts(
        self, client: TestClient, sample_prompt_data
    ):
        """Verify only the deleted collection's prompts are unfiled.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        doomed = client.post("/collections", json={"name": "A"}).json()["id"]
        other = client.post("/collections", json={"name": "B"}).json()["id"]
        in_doomed = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": doomed}
        ).json()["id"]
        in_other = client.post(
            "/prompts", json={**sample_prompt_data, "collection_id": other}
        ).json()
        unfiled = client.post("/prompts", json=sample_prompt_data).json()

        client.delete(f"/collections/{doomed}")

        assert client.get(f"/prompts/{in_doomed}").json()["collection_id"] is None
        assert client.get(f"/prompts/{in_other['id']}").json() == in_other
        assert client.get(f"/prompts/{unfiled['id']}").json() == unfiled

    def test_delete_collection_empty(self, client: TestClient, sample_collection_data):
        """Verify deleting a collection with no prompts is a 204 with no body.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]

        response = client.delete(f"/collections/{collection_id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_collection_unfiles_every_prompt(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        """Verify every prompt in the collection is unfiled, not just the first.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        ids = [
            client.post(
                "/prompts", json={**sample_prompt_data, "collection_id": collection_id}
            ).json()["id"]
            for _ in range(3)
        ]

        client.delete(f"/collections/{collection_id}")

        for prompt_id in ids:
            assert client.get(f"/prompts/{prompt_id}").json()["collection_id"] is None

    def test_delete_collection_keeps_tags(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        """Verify a prompt unfiled by deleting its collection keeps its tags.

        Args:
            client: FastAPI test client fixture.
            sample_collection_data: Valid collection payload fixture.
            sample_prompt_data: Valid prompt payload fixture.
        """
        collection_id = client.post("/collections", json=sample_collection_data).json()["id"]
        prompt_id = client.post(
            "/prompts",
            json={**sample_prompt_data, "collection_id": collection_id, "tags": ["ai"]},
        ).json()["id"]

        response = client.delete(f"/collections/{collection_id}")

        assert response.status_code == 204
        stored = client.get(f"/prompts/{prompt_id}").json()
        assert stored["collection_id"] is None
        assert stored["tags"] == ["ai"]


class TestTags:
    """Tests for the tag endpoint."""

    # --- list_tags: success cases ---

    @pytest.mark.parametrize("untagged", [0, 2])
    def test_list_tags_empty(self, client: TestClient, sample_prompt_data, untagged):
        """Verify ``GET /tags`` lists nothing when no prompt carries a tag.

        Args:
            client: FastAPI test client fixture.
            sample_prompt_data: Valid prompt payload fixture, with no tags.
            untagged: How many prompts without tags to create first.
        """
        for _ in range(untagged):
            client.post("/prompts", json=sample_prompt_data)

        response = client.get("/tags")

        assert response.status_code == 200
        assert response.json() == {"tags": [], "total": 0}

    def test_list_tags_counts_and_order(self, client: TestClient):
        """Verify each tag is listed once with its prompt count, sorted by name.

        Args:
            client: FastAPI test client fixture.
        """
        client.post("/prompts", json={"title": "A", "content": "Text.", "tags": ["python", "ai"]})
        client.post(
            "/prompts", json={"title": "B", "content": "Text.", "tags": ["code-review", "ai"]}
        )

        response = client.get("/tags")

        assert response.status_code == 200
        assert response.json() == {
            "tags": [
                {"name": "ai", "prompt_count": 2},
                {"name": "code-review", "prompt_count": 1},
                {"name": "python", "prompt_count": 1},
            ],
            "total": 3,
        }

    def test_list_tags_after_delete(self, client: TestClient):
        """Verify deleting a prompt lowers its tags' counts and drops a tag no prompt carries.

        Args:
            client: FastAPI test client fixture.
        """
        first = client.post(
            "/prompts", json={"title": "A", "content": "Text.", "tags": ["python", "ai"]}
        ).json()
        client.post(
            "/prompts", json={"title": "B", "content": "Text.", "tags": ["code-review", "ai"]}
        )
        client.delete(f"/prompts/{first['id']}")

        response = client.get("/tags")

        assert response.status_code == 200
        assert response.json() == {
            "tags": [
                {"name": "ai", "prompt_count": 1},
                {"name": "code-review", "prompt_count": 1},
            ],
            "total": 2,
        }

    def test_list_tags_after_patch(self, client: TestClient):
        """Verify clearing a prompt's tags with PATCH is reflected in the counts.

        Args:
            client: FastAPI test client fixture.
        """
        client.post("/prompts", json={"title": "A", "content": "Text.", "tags": ["python", "ai"]})
        second = client.post(
            "/prompts", json={"title": "B", "content": "Text.", "tags": ["code-review", "ai"]}
        ).json()
        client.patch(f"/prompts/{second['id']}", json={"tags": []})

        response = client.get("/tags")

        assert response.status_code == 200
        assert response.json() == {
            "tags": [
                {"name": "ai", "prompt_count": 1},
                {"name": "python", "prompt_count": 1},
            ],
            "total": 2,
        }

    def test_list_tags_string_order(self, client: TestClient):
        """Verify tags sort in Python's string order: hyphen, then digits, then letters.

        Args:
            client: FastAPI test client fixture.
        """
        client.post("/prompts", json={"title": "A", "content": "Text.", "tags": ["ab", "a1", "a-b"]})

        response = client.get("/tags")

        assert response.status_code == 200
        assert [t["name"] for t in response.json()["tags"]] == ["a-b", "a1", "ab"]
