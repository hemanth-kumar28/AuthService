"""Tests for authentication endpoints."""


class TestRegister:
    """POST /auth/register"""

    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "Str0ng@Pass",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert "user" in body["data"]
        assert "tokens" in body["data"]
        assert body["data"]["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client, registered_user):
        resp = client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "different",
            "password": "Str0ng@Pass",
        })
        assert resp.status_code == 409
        assert resp.json()["success"] is False

    def test_register_duplicate_username(self, client, registered_user):
        resp = client.post("/auth/register", json={
            "email": "different@example.com",
            "username": "testuser",
            "password": "Str0ng@Pass",
        })
        assert resp.status_code == 409

    def test_register_weak_password(self, client):
        resp = client.post("/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_register_password_no_special_char(self, client):
        resp = client.post("/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "NoSpecial1",
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/auth/register", json={
            "email": "not-an-email",
            "username": "validuser",
            "password": "Str0ng@Pass",
        })
        assert resp.status_code == 422

    def test_register_username_too_short(self, client):
        resp = client.post("/auth/register", json={
            "email": "ok@example.com",
            "username": "ab",
            "password": "Str0ng@Pass",
        })
        assert resp.status_code == 422


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "Test@1234",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "access_token" in body["data"]["tokens"]
        assert "refresh_token" in body["data"]["tokens"]

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "Wrong@1234",
        })
        assert resp.status_code == 401
        assert resp.json()["success"] is False

    def test_login_nonexistent_user(self, client):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "Some@1234",
        })
        assert resp.status_code == 401


class TestRefresh:
    """POST /auth/refresh"""

    def test_refresh_success(self, client, registered_user):
        refresh_token = registered_user["tokens"]["refresh_token"]
        resp = client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "access_token" in body["data"]

    def test_refresh_invalid_token(self, client):
        resp = client.post("/auth/refresh", json={
            "refresh_token": "invalid-token-string",
        })
        assert resp.status_code == 401


class TestMe:
    """GET /auth/me"""

    def test_me_success(self, client, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "test@example.com"

    def test_me_no_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 422  # missing required header

    def test_me_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401


class TestUpdateProfile:
    """PUT /auth/update-profile"""

    def test_update_username(self, client, auth_headers):
        resp = client.put("/auth/update-profile", json={
            "username": "updated_user",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == "updated_user"

    def test_update_duplicate_email(self, client, auth_headers, second_user):
        resp = client.put("/auth/update-profile", json={
            "email": "other@example.com",
        }, headers=auth_headers)
        assert resp.status_code == 409


class TestDeleteAccount:
    """DELETE /auth/delete-account"""

    def test_delete_account(self, client, auth_headers):
        resp = client.delete("/auth/delete-account", headers=auth_headers)
        assert resp.status_code == 200

        # Verify user no longer exists
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 401
