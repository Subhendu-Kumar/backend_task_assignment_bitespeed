# Bitespeed Identity Service

A FastAPI backend service that implements contact identity reconciliation. Given an email and/or phone number, the `/identify` endpoint links contacts and returns a consolidated view with primary and secondary relationships.

## Tech Stack

- **FastAPI** – web framework
- **Prisma Client Python** – ORM (PostgreSQL)
- **Pydantic** – request/response validation
- **python-jose** – JWT authentication
- **bcrypt** – password hashing

## Prerequisites

- Python 3.10+
- PostgreSQL running locally (or a remote connection string)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Subhendu-Kumar/backend_tesk_assignment_bitespeed.git
cd backend_tesk_assignment_bitespeed
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

At minimum, set `DATABASE_URL` to point to your PostgreSQL instance:

```
DATABASE_URL=postgresql://user:password@localhost:5432/bitespeed
```

### 5. Set up the database

Generate the Prisma client and run migrations:

```bash
prisma generate
prisma migrate deploy
```

### 6. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/` | Welcome / entry point | No |
| `GET` | `/health` | Health check | No |
| `POST` | `/identify` | Identity reconciliation | No |
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/login` | Login & get JWT token | No |
| `GET` | `/auth/me` | Get current user info | Yes |

## Testing the `/identify` Endpoint

```bash
curl -X POST http://127.0.0.1:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "phoneNumber": "1234567890"}'
```

**Sample response:**

```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["test@example.com"],
    "phoneNumbers": ["1234567890"],
    "secondaryContactIds": []
  }
}
```

## Testing Auth Endpoints

**Register:**

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'
```

**Login:**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

## Interactive Docs

Once the server is running, visit:

- **Swagger UI** – http://127.0.0.1:8000/docs
- **ReDoc** – http://127.0.0.1:8000/redoc
