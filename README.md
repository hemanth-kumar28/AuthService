# 🔐 AuthService — Production-Grade CRUD & Auth API

A secure, production-ready backend API built with **FastAPI** and **PostgreSQL** featuring JWT-based authentication, full CRUD operations on user-owned resources, and clean modular architecture.

---

## ✨ Features

- **JWT Authentication** — Access + refresh token rotation
- **Full CRUD** — Notes with tag support (many-to-many)
- **Ownership Enforcement** — Users can only access their own data
- **Strong Validation** — Password strength, email format, input sanitization
- **Structured Errors** — Consistent JSON error responses with status codes
- **Advanced Queries** — Pagination, ILIKE search, multi-field sorting
- **Database Migrations** — Alembic version-controlled schema management
- **Clean Architecture** — Service layer, dependency injection, separation of concerns

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Language | Python 3.12 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |
| Containerization | Docker Compose |

---

## 📁 Project Structure

```
app/
├── main.py                  # FastAPI app factory, CORS, routers
├── core/
│   ├── config.py            # Settings from .env (pydantic-settings)
│   └── security.py          # JWT encode/decode + bcrypt hashing
├── db/
│   ├── session.py           # SQLAlchemy engine + session factory
│   └── base.py              # DeclarativeBase + model registry
├── models/
│   ├── user.py              # User model (UUID, unique email/username)
│   ├── note.py              # Note model (FK → users)
│   ├── tag.py               # Tag + NoteTag association table (M2M)
│   └── refresh_token.py     # Refresh token storage
├── schemas/
│   ├── common.py            # SuccessResponse / ErrorResponse wrappers
│   ├── user.py              # Registration, login, profile schemas
│   ├── note.py              # Note CRUD + paginated list schemas
│   └── tag.py               # Tag create/response schemas
├── routes/
│   ├── auth.py              # /auth/* endpoints
│   ├── notes.py             # /notes/* endpoints
│   └── tags.py              # /tags/* endpoints
├── services/
│   ├── auth_service.py      # Auth business logic
│   ├── note_service.py      # Notes CRUD + search + ownership
│   └── tag_service.py       # Per-user tag management
└── utils/
    ├── errors.py            # Custom exceptions + global handlers
    └── dependencies.py      # JWT auth dependency
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Conda (optional, for environment management)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/auth-service.git
cd auth-service
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your own values:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5431/auth_service_db
JWT_SECRET_KEY=<generate-a-strong-random-key>
```



**Generate a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

This starts PostgreSQL 16 on port `5431` and creates both `auth_service_db` and `auth_service_test_db`.

### 4. Create Python Environment

```bash
# Using conda
conda create -n authservice python=3.12 -y
conda activate authservice

# Or using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 8. Open API Docs

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoints

### Auth (`/auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | ❌ | Register a new user |
| `POST` | `/auth/login` | ❌ | Login and receive tokens |
| `POST` | `/auth/refresh` | ❌ | Refresh token rotation |
| `GET` | `/auth/me` | ✅ | Get current user profile |
| `PUT` | `/auth/update-profile` | ✅ | Update email or username |
| `DELETE` | `/auth/delete-account` | ✅ | Delete account (cascades) |

### Notes (`/notes`)

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/notes` | ✅ | Create a note |
| `GET` | `/notes` | ✅ | List notes (paginate/search/sort) |
| `GET` | `/notes/{id}` | ✅ | Get a specific note |
| `PUT` | `/notes/{id}` | ✅ | Update a note |
| `DELETE` | `/notes/{id}` | ✅ | Delete a note |

**Query Parameters for `GET /notes`:**

```
?limit=20&offset=0&search=keyword&sort=created_at&order=desc&tag_id=<uuid>
```

### Tags (`/tags`)

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/tags` | ✅ | Create a tag |
| `GET` | `/tags` | ✅ | List your tags |
| `DELETE` | `/tags/{id}` | ✅ | Delete a tag |

---

## 📦 Request / Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": 404,
    "message": "Note not found",
    "details": null
  }
}
```

---

## 🔒 Validation Rules

### Password
- Minimum 8 characters, maximum 128
- At least one **uppercase** letter
- At least one **lowercase** letter
- At least one **digit**
- At least one **special character** (`!@#$%^&*` etc.)

### Username
- 3–30 characters
- Alphanumeric + underscores only

### Notes
- Title: required, 1–200 characters
- Content: optional, max 50,000 characters

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests run against a separate PostgreSQL database (`auth_service_test_db`) with table truncation between tests for full isolation.

```
42 passed ✅
```

---

## 🗄️ Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    users     │     │    notes     │     │    tags      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id (PK)      │◄────│ owner_id(FK) │     │ id (PK)      │
│ email (UQ)   │     │ id (PK)      │     │ name         │
│ username(UQ) │     │ title        │     │ user_id (FK) │
│ hashed_pass  │     │ content      │     └──────┬───────┘
│ created_at   │     │ created_at   │            │
│ updated_at   │     │ updated_at   │     ┌──────┴───────┐
└──────┬───────┘     └──────┬───────┘     │  note_tags   │
       │                    │             ├──────────────┤
       │             ┌──────┴─────────────│ note_id (FK) │
       │             │                    │ tag_id  (FK) │
┌──────┴───────┐     │                    └──────────────┘
│refresh_tokens│     │
├──────────────┤     │
│ id (PK)      │     │
│ user_id (FK) │     │
│ token (UQ)   │
│ expires_at   │
│ revoked      │
└──────────────┘
```

---

## 🔐 Security Considerations

- Passwords are hashed with **bcrypt** — never stored in plaintext
- JWT tokens include expiry and type claims
- Refresh tokens are stored in DB and revoked on rotation
- All routes enforce **ownership checks** — no horizontal privilege escalation
- Input validated via **Pydantic** — prevents injection
- Database queries use **SQLAlchemy ORM** — no raw SQL injection risk
- `.env` is **gitignored** — secrets never committed
- Internal errors are **never exposed** to clients

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
