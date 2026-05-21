# Effective Mobile — User Auth API

Django REST API for user registration, JWT authentication, and document access control. Built as a test task submission.

**Persisted:** users (PostgreSQL)  
**Mocked (per task spec):** documents and admin-granted permissions (in-memory)

---

## Tech stack

| Layer | Choice |
|--------|--------|
| Framework | Django 6 + Django REST Framework |
| Auth | SimpleJWT (email-based login, custom `Users` model) |
| Password hashing | bcrypt |
| Database | PostgreSQL 15 |
| Containerization | Docker Compose |
| Dependencies | [uv](https://github.com/astral-sh/uv) (`pyproject.toml` + `uv.lock`) |

---

## Project structure

```
Effective-Mobile/
├── UserAuth/                 # Django project (settings, root URLs)
├── users/                    # Main application
│   ├── models.py             # Users model (PostgreSQL)
│   ├── serializers.py        # Registration + JWT login
│   ├── authentication.py     # Custom JWT + login backend
│   ├── views.py              # API endpoints
│   ├── urls.py               # /api/* routes
│   ├── constants.py          # UserRole enum
│   ├── permissions.py        # DRF permission classes (IsAdmin)
│   ├── documents.py          # Document service + access rules
│   ├── mocks/                # In-memory documents & permissions (task spec)
│   └── services/
│       └── permission_service.py   # Admin grant/revoke logic
├── manage.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
└── pyproject.toml
```

---

## Quick start (Docker)

**Prerequisites:** Docker and Docker Compose

1. Copy `.env.example` to `.env` and adjust values if needed:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. API base URL: `http://localhost:8000`

Migrations run automatically via `entrypoint.sh` before the server starts.

---

## Local development (without Docker)

**Prerequisites:** Python 3.12+, PostgreSQL, [uv](https://github.com/astral-sh/uv)

```bash
uv sync
source .venv/bin/activate

# Set database env vars (or use a local .env)
export DB_NAME=django_db
export DB_USER=django_user
export DB_PASSWORD=django_password
export DB_HOST=localhost
export DB_PORT=5432

python manage.py migrate
python manage.py runserver
```

---

## Authentication

Login uses **email + password** (not username).

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/token/` | POST | Public |
| `/api/token/refresh/` | POST | Public |

**Obtain tokens**

```http
POST /api/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response**

```json
{
  "access": "<jwt-access>",
  "refresh": "<jwt-refresh>",
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "user"
}
```

Send the access token on protected routes:

```http
Authorization: Bearer <access>
```

---

## API endpoints

### Users

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/users/create/` | POST | Public | Register a new user |
| `/api/users/` | GET | JWT | List users (non-admins see active users only) |
| `/api/users/<id>/update/` | PATCH | JWT | Update user (self or admin) |
| `/api/users/<id>/delete/` | DELETE | JWT | Soft-delete (deactivate) user |
| `/api/users/delete/` | DELETE | JWT | Deactivate own account (no `pk`) |

**Registration body**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "role": "user"
}
```

Roles: `user` (default), `admin`.

### Documents (mocked)

Documents live in memory (`users/mocks/documents.py`). Data resets when the process restarts.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/documents/` | GET | JWT | List documents the user may view |
| `/api/documents/<doc_id>/` | GET | JWT | Get one document |
| `/api/documents/<doc_id>/update/` | PATCH | JWT | Update title/content if allowed |

**Seeded mock documents**

| ID | Title | Owner ID |
|----|-------|----------|
| 1 | Django JWT Setup | 2 |
| 2 | My Python Notes | 1 |
| 3 | Docker Commands | 1 |

**Access rules**

- Owner can view and edit their documents.
- `admin` can view all documents.
- Users may receive extra view/edit/delete grants via the admin permission API (also in-memory).

### Admin permissions (mocked)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/admin/permissions/` | GET | JWT (admin) | List all users, owned docs, and granted permissions |
| `/api/admin/permissions/grant/` | POST | JWT (admin) | Grant document permissions to a user |
| `/api/admin/permissions/revoke/` | DELETE | JWT (admin) | Revoke document permissions from a user |

**Grant body**

```json
{
  "user_id": 2,
  "document_id": 1,
  "can_view": true,
  "can_edit": false,
  "can_delete": false
}
```

**Revoke body**

```json
{
  "user_id": 2,
  "document_id": 1
}
```

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_NAME` | Yes | — | PostgreSQL database name |
| `DB_USER` | Yes | — | PostgreSQL user |
| `DB_PASSWORD` | Yes | — | PostgreSQL password |
| `DB_HOST` | No | `db` (Docker) | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `SECRET_KEY` | Yes (Docker) | dev fallback in settings | Django secret key |
| `DEBUG` | No | `1` | Set to `0` in production |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hosts |

---

## Design notes

- **Custom `Users` model** — Not Django’s built-in `User`; passwords are hashed with bcrypt in serializers.
- **JWT** — `CustomJWTAuthentication` loads the user from the `user_id` claim in the token.
- **Soft delete** — “Delete” sets `is_active=False`; inactive users cannot log in.
- **Mock layer** — Documents and permissions under `users/mocks/` are intentional for the test task; replace with ORM models for production.

---

## Running tests

```bash
uv sync
source .venv/bin/activate
python manage.py test users
```

Tests use an in-memory SQLite database (no PostgreSQL required).

---

## License

Private test task — no license specified.
