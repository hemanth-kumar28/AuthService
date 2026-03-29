"""Tests for notes CRUD endpoints."""


class TestCreateNote:
    """POST /notes"""

    def test_create_note(self, client, auth_headers):
        resp = client.post("/notes", json={
            "title": "My First Note",
            "content": "Hello world!",
        }, headers=auth_headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["title"] == "My First Note"

    def test_create_note_title_required(self, client, auth_headers):
        resp = client.post("/notes", json={
            "content": "No title",
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_create_note_unauthenticated(self, client):
        resp = client.post("/notes", json={"title": "Test"})
        assert resp.status_code == 422  # missing auth header

    def test_create_note_with_tags(self, client, auth_headers):
        # Create a tag first
        tag_resp = client.post("/tags", json={"name": "important"}, headers=auth_headers)
        tag_id = tag_resp.json()["data"]["id"]

        resp = client.post("/notes", json={
            "title": "Tagged Note",
            "content": "Has tags",
            "tag_ids": [tag_id],
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert len(resp.json()["data"]["tags"]) == 1
        assert resp.json()["data"]["tags"][0]["name"] == "important"


class TestListNotes:
    """GET /notes"""

    def test_list_empty(self, client, auth_headers):
        resp = client.get("/notes", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["notes"] == []
        assert body["data"]["total"] == 0

    def test_list_with_notes(self, client, auth_headers):
        for i in range(3):
            client.post("/notes", json={"title": f"Note {i}"}, headers=auth_headers)

        resp = client.get("/notes", headers=auth_headers)
        assert resp.json()["data"]["total"] == 3

    def test_pagination(self, client, auth_headers):
        for i in range(5):
            client.post("/notes", json={"title": f"Note {i}"}, headers=auth_headers)

        resp = client.get("/notes?limit=2&offset=0", headers=auth_headers)
        body = resp.json()["data"]
        assert len(body["notes"]) == 2
        assert body["total"] == 5

    def test_search(self, client, auth_headers):
        client.post("/notes", json={"title": "Python Tutorial"}, headers=auth_headers)
        client.post("/notes", json={"title": "Java Guide"}, headers=auth_headers)

        resp = client.get("/notes?search=python", headers=auth_headers)
        assert resp.json()["data"]["total"] == 1
        assert "Python" in resp.json()["data"]["notes"][0]["title"]

    def test_sort_asc(self, client, auth_headers):
        client.post("/notes", json={"title": "BBB"}, headers=auth_headers)
        client.post("/notes", json={"title": "AAA"}, headers=auth_headers)

        resp = client.get("/notes?sort=title&order=asc", headers=auth_headers)
        titles = [n["title"] for n in resp.json()["data"]["notes"]]
        assert titles == ["AAA", "BBB"]

    def test_no_cross_user_notes(self, client, auth_headers, second_user):
        # Create note as first user
        client.post("/notes", json={"title": "Private"}, headers=auth_headers)

        # Second user should see nothing
        resp = client.get("/notes", headers=second_user["_headers"])
        assert resp.json()["data"]["total"] == 0


class TestGetNote:
    """GET /notes/{id}"""

    def test_get_note(self, client, auth_headers):
        create_resp = client.post("/notes", json={"title": "Detail"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Detail"

    def test_get_nonexistent(self, client, auth_headers):
        resp = client.get("/notes/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_other_user_note(self, client, auth_headers, second_user):
        create_resp = client.post("/notes", json={"title": "Mine"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.get(f"/notes/{note_id}", headers=second_user["_headers"])
        assert resp.status_code == 403


class TestUpdateNote:
    """PUT /notes/{id}"""

    def test_update_note(self, client, auth_headers):
        create_resp = client.post("/notes", json={"title": "Old"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/notes/{note_id}", json={"title": "New"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "New"

    def test_update_other_user_note(self, client, auth_headers, second_user):
        create_resp = client.post("/notes", json={"title": "Mine"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/notes/{note_id}", json={"title": "Hacked"}, headers=second_user["_headers"])
        assert resp.status_code == 403


class TestDeleteNote:
    """DELETE /notes/{id}"""

    def test_delete_note(self, client, auth_headers):
        create_resp = client.post("/notes", json={"title": "ToDelete"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
        assert resp.status_code == 200

        # Verify deleted
        resp = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_other_user_note(self, client, auth_headers, second_user):
        create_resp = client.post("/notes", json={"title": "Mine"}, headers=auth_headers)
        note_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/notes/{note_id}", headers=second_user["_headers"])
        assert resp.status_code == 403
