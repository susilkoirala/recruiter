# TechKraft Recruiter Dashboard

A full-stack internal recruiter dashboard for managing candidates, reviewer scores, role-based access, and AI-assisted candidate summaries. The app uses FastAPI, React/Vite, SQLite, Docker Compose, and nginx serving the built frontend.

## Run Locally

Add the local domain to your hosts file:

```bash
sudo sh -c 'echo "127.0.0.1 recruiter.local" >> /etc/hosts'
```

Create environment files from the example and fill in local values:

```bash
cp .env.example backend/.env
cp .env.example frontend/.env
```

For the frontend file, keep:

```env
VITE_API_BASE_URL=/api/v1
```

For AI summaries, create a Groq API key from the Groq console and place it in `backend/.env`:

```env
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

Keep real API keys out of git; commit only placeholder values in `.env.example`.

Build and start the app:

```bash
docker compose up -d --build
```

The `--build` flag tells Docker Compose to rebuild the backend and frontend images before starting containers. The frontend Dockerfile installs dependencies and runs the React build, producing the `frontend/dist` files that nginx serves.

Seed the database before using the dashboard:

```bash
docker compose exec backend python seed_dummy_data.py
```

This step is required for the default admin account and demo candidates. The seeded admin login is:

```text
email: root@example.com
password: apple@pie
```

Open:

```text
http://recruiter.local:8000
```

The FastAPI API is served behind nginx at:

```text
http://recruiter.local:8000/api/v1
```

## Useful Commands

Run backend tests:

```bash
cd backend
python -m pytest tests -q
```

Seed demo data again if needed:

```bash
docker compose exec backend python seed_dummy_data.py
```

Stop containers:

```bash
docker compose down
```

## Example API Calls

Register a reviewer:

```bash
curl -X POST http://recruiter.local:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"reviewer@example.com","password":"password123"}'
```

Login with the seeded admin account:

```bash
curl -X POST http://recruiter.local:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"root@example.com","password":"apple@pie"}'
```

List candidates with a token:

```bash
curl http://recruiter.local:8000/api/v1/candidates \
  -H "Authorization: Bearer <access_token>"
```

## Architecture Decision Record

### 1. FastAPI For The Backend

**Context:** The assignment needed a working API quickly with authentication, filtering, validation, and a small test surface.

**Decision:** I used FastAPI because it is easy to get a project running quickly, provides request validation through Pydantic, and needs fewer extra package dependencies for a clean API compared with heavier alternatives.

**Trade-off:** FastAPI keeps the backend lightweight, but more production concerns like migrations, background workers, and observability still need explicit setup.

### 2. SQLite With Relational Candidate And Score Tables

**Context:** Candidates and reviewer scores have clear relationships, and reviewers must only see their own scores while admins see all scores.

**Decision:** I modeled candidates and scores as separate relational tables with indexes on common query fields like candidate status, role, candidate ID, and reviewer ID.

**Trade-off:** SQLite is simple for local/demo use, but a hosted production version should move to PostgreSQL for stronger concurrency and operational reliability.

### 3. Manual JWT Authentication

**Context:** The project needed email/password auth, reviewer/admin roles, refresh tokens, and a rule that registration never accepts role from the client.

**Decision:** I implemented JWT handling manually with signed access/refresh tokens and hardcoded new registrations to the reviewer role.

**Trade-off:** This avoids hiding the auth flow behind a large dependency, but a production app would likely use a mature auth library/provider to reduce security maintenance risk.

## Debugging Signal

The bug in the sample query is that it loads every candidate first:

```python
all_candidates = db.execute("SELECT * FROM candidates").fetchall()
```

Then filtering and pagination happen in Python. This matters at scale because the database must send the full table to the application, memory usage grows with total candidate count, and each page gets slower as the table grows.

The correct approach is to push filtering, search, ordering, limit, and offset into the database query:

```sql
SELECT *
FROM candidates
WHERE status = :status
  AND (name LIKE :keyword OR email LIKE :keyword)
ORDER BY created_at DESC
LIMIT :page_size OFFSET :offset;
```

That lets the database use indexes and return only the requested page.

## Learning Reflection

One thing I tried more deliberately here was implementing JWT authentication manually instead of relying on a full auth package. Given more time, I would explore rotating refresh tokens more deeply, adding migration tooling, and replacing SQLite with PostgreSQL for a deployment-ready setup.

## Notes

- Registration always creates reviewer accounts; the client cannot choose an admin role.
- Real credentials should stay out of git. Use `.env.example` for placeholder values only.
- Candidate deletion is handled as a soft archive rather than a hard delete.
