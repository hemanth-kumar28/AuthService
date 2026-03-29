"""Tests for tags endpoints."""


class TestCreateTag:
    """POST /tags"""

    def test_create_tag(self, client, auth_headers):
        resp = client.post("/tags", json={"name": "work"}, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["name"] == "work"

    def test_create_duplicate_tag(self, client, auth_headers):
        client.post("/tags", json={"name": "dup"}, headers=auth_headers)
        resp = client.post("/tags", json={"name": "dup"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_same_tag_name_different_users(self, client, auth_headers, second_user):
        """Different users can have tags with the same name."""
        resp1 = client.post("/tags", json={"name": "shared"}, headers=auth_headers)
        resp2 = client.post("/tags", json={"name": "shared"}, headers=second_user["_headers"])
        assert resp1.status_code == 201
        assert resp2.status_code == 201


class TestListTags:
    """GET /tags"""

    def test_list_tags(self, client, auth_headers):
        client.post("/tags", json={"name": "a"}, headers=auth_headers)
        client.post("/tags", json={"name": "b"}, headers=auth_headers)

        resp = client.get("/tags", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 2

    def test_no_cross_user_tags(self, client, auth_headers, second_user):
        client.post("/tags", json={"name": "private"}, headers=auth_headers)

        resp = client.get("/tags", headers=second_user["_headers"])
        assert len(resp.json()["data"]) == 0


class TestDeleteTag:
    """DELETE /tags/{id}"""

    def test_delete_tag(self, client, auth_headers):
        create_resp = client.post("/tags", json={"name": "temp"}, headers=auth_headers)
        tag_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/tags/{tag_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_delete_other_user_tag(self, client, auth_headers, second_user):
        create_resp = client.post("/tags", json={"name": "mine"}, headers=auth_headers)
        tag_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/tags/{tag_id}", headers=second_user["_headers"])
        assert resp.status_code == 403
