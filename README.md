# EstateFlow AI

A deliberately small AI-powered real-estate sales workspace. It prioritizes inbound leads, stores the current customer profile, performs deterministic property matching, and uses Groq only for explicit AI actions.

## Architecture
- Frontend: Next.js + TypeScript + Tailwind CSS
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- AI: Groq API (server-side only)
- Deployment target: Vercel + Render + Neon/Supabase PostgreSQL

## Core rule
`leads` is the current source of truth. `interactions` is historical context. Requirement changes are proposed by AI and must be confirmed by the salesperson before the lead is updated. Property matching is deterministic and never calls Groq.

## AI cost control
No AI call happens on page load, refresh, GET endpoints, filters, or property matching. Groq is called only for Analyze Lead, contextual assistant messages, requirement-change extraction, and any explicit re-analysis. Analysis is cached in PostgreSQL.

## Local setup
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
copy .env.example .env  # Windows
# or cp .env.example .env
# configure DATABASE_URL and GROQ_API_KEY
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Database URL / psycopg v3
The user-facing `DATABASE_URL` remains the standard PostgreSQL form:
```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```
The backend normalizes a leading `postgresql://` scheme internally to `postgresql+psycopg://` before SQLAlchemy creates the engine. This keeps the `.env` format simple while explicitly selecting the installed psycopg v3 driver. Alembic uses the same normalized URL, and `seed.py` uses the same `SessionLocal`, so there is one database configuration path.

The hostname is never hardcoded; it always comes from `DATABASE_URL`. A DNS error such as `getaddrinfo failed` is therefore a separate hostname/network problem, not a driver-selection problem. The application does not fall back to SQLite or fake data.

To verify the driver locally:
```bash
python -c "import psycopg; print(psycopg.__version__)"
```

To verify migrations with the standard URL:
```powershell
$env:PYTHONPATH="."
alembic upgrade head
```

### Frontend
```bash
cd frontend
npm install
copy .env.example .env.local  # Windows
# or cp .env.example .env.local
npm run dev
```

Open http://localhost:3000.

## Deployment
1. Create PostgreSQL on Neon or Supabase and set the backend `DATABASE_URL`.
2. Deploy `backend` to Render as a Python web service with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Set `GROQ_API_KEY`, `GROQ_MODEL`, and `FRONTEND_URL` in Render.
4. Before seeding a production database, run `alembic upgrade head`; then run `python seed.py` once. The seed script does not call Groq.
5. Deploy `frontend` to Vercel and set `NEXT_PUBLIC_API_URL` to the Render `/api` URL.
6. Set `FRONTEND_URL` on Render to the exact Vercel origin.

## AI usage disclosure
AI assistance may be used during development for code generation, debugging, UI iteration, and architecture discussion. The application itself uses Groq for lead analysis, contextual assistance, requirement-change extraction, and response suggestions.

## Known limitations
- Authentication/user roles are intentionally omitted for assignment scope.
- Inventory is seeded rather than live.
- Timeline matching is intentionally simple and transparent.
- No WhatsApp, email, payments, booking, scraping, maps, RAG, vector database, background AI worker, or real-time notification system.

## Final hardening notes

- Lead and property monetary values are stored canonically as INR numeric values; the UI formats them as lakh for readability.
- Seed data is deterministic, idempotent by stable demo identifiers, and recomputes `lead_properties` without any Groq calls.
- Alembic is the production schema authority; runtime `create_all()` is not used.
- Property matching is deterministic and does not call Groq. Timeline points are awarded only when possession can be compared with the stated timeline.
- Requirement changes use a strict field whitelist and type normalization before database updates.
- The contextual assistant has a deterministic guard for obviously unrelated requests and a strict lead-context system prompt for ambiguous requests.
- AI failures return controlled errors; the application does not fabricate fallback AI answers.
- Property relationship status updates are database-only operations.
- AI calls occur only on explicit Analyze/Re-analyze, Assistant, and Requirement Change actions. Normal page loads, searches, interactions, status updates, and matching do not call Groq.

## Final acceptance behavior
- Chat responses are validated through a strict `ChatResponse` Pydantic contract; malformed assistant output is rejected rather than sent to the UI.
- AI failures use inline retry states in the lead workspace; no fake/canned AI result is substituted.
- `leads.ai_analyzed_at` records the timestamp of the latest successful explicit analysis. Apply migration `0003_ai_analyzed_at` before running the app against an existing database.
- The contextual assistant uses two-layer scope protection: a deterministic obvious-out-of-scope guard followed by a strict lead-context Groq prompt. No separate AI classifier is used.
- Property search, matching, interactions, relationship-status changes, and requirement-change application are database/deterministic operations and do not call Groq.
