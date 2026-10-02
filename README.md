# EstateFlow AI

> **AI-powered real-estate sales workspace for salespeople**

EstateFlow AI helps real-estate salespeople manage inbound leads, understand customer requirements, prioritize leads dynamically, track interactions, detect requirement changes, match customers with properties, and get contextual AI assistance during the sales process.

## Live Demo

**Frontend:** https://estateflow-ai-frontend.onrender.com/

---

# 1. Problem

Real-estate salespeople can receive a large number of leads every day. The challenge is quickly understanding which leads need attention, what each customer wants, which properties match, whether requirements changed, and what the salesperson should do next.

EstateFlow AI treats a lead as an **evolving sales profile** rather than static information.

---

# 2. Solution

EstateFlow AI combines:

- Lead management
- Dynamic lead prioritization
- AI-powered lead analysis
- Contextual lead-specific AI assistant
- Customer interaction tracking
- Requirement change detection
- Human-confirmed requirement updates
- Deterministic property matching
- Property recommendation and journey tracking

Main product loop:

```text
Customer Conversation
        ↓
Interaction
        ↓
Priority Update
        ↓
Requirement Evolution
        ↓
Property Rematching
        ↓
AI Analysis / Assistance
        ↓
Salesperson Action
        ↓
Customer Conversation
        ↓
       ...
```

---

# 3. Main Features

## Lead Management

Salespeople can create and manage multiple leads containing:

- Name
- Location
- Property requirement
- BHK
- Budget
- Buying timeline
- Parking requirement
- Customer message
- Lead score
- Lead priority

Priority is represented as:

```text
HOT / WARM / COLD
```

Priority can change as new customer interactions are recorded.

## Dynamic Lead Prioritization

Base scoring uses:

- Buying intent
- Timeline
- Budget availability
- Requirement clarity
- Engagement

Interaction signals dynamically adjust the score:

| Signal | Effect |
|---|---:|
| Ready to buy | +15 |
| Ready to purchase | +15 |
| Wants site visit | +15 |
| Shortlisted | +15 |
| Interested/details | +5 |
| Still comparing | -10 |
| Needs more time | -10 |
| Better deal found | -20 |
| Doesn't want to buy | COLD |
| Not interested | COLD |
| Already purchased elsewhere | COLD |

```text
Lead Profile → Base Score → Customer Interaction
→ Dynamic Adjustment → Final Score → HOT/WARM/COLD
```

---

# 4. AI Lead Analysis

The salesperson explicitly chooses **Analyze Lead** or **Re-analyze**.

AI generates:

- Lead summary
- Customer intent
- Key requirements
- Objections/concerns
- Recommended next action
- Suggested customer response

```text
Lead
 ↓
Analyze
 ↓
FastAPI
 ↓
AI Service
 ↓
Groq API
 ↓
Structured JSON
 ↓
Pydantic Validation
 ↓
Database
 ↓
Lead Detail
```

Re-analysis uses the current lead profile, latest interaction history, and current property matches. Previous AI analysis is not used as the source for new analysis.

---

# 5. Contextual AI Assistant

The assistant is specific to the selected lead rather than a general chatbot.

It can answer using:

- Customer requirements
- Customer intent
- Objections
- Interaction history
- Matched properties
- Recommended sales action

```text
Selected Lead
     ↓
Lead Context
     ↓
Salesperson Question
     ↓
Groq
     ↓
Contextual Answer
```

Example:

> "What does the customer want?"

The answer comes from that lead's data.

---

# 6. AI Scope Control

The assistant is restricted to the sales context.

Examples of out-of-scope requests include:

- Programming questions
- Weather
- General politics
- Recipes
- General mathematics
- Stock prices
- General-purpose questions

This prevents the feature from becoming an unrelated general-purpose chatbot.

---

# 7. Requirement Change Detection

Customer requirements can change during conversations.

Example:

```text
Initial:
3 BHK
Budget: ₹90 lakh

Later:
2, 3 or 4 BHK
Budget: ₹90 lakh
Parking mandatory
```

The salesperson can save the interaction and explicitly request **Extract Requirement Changes**.

```text
Customer Interaction
        ↓
Interaction Saved
        ↓
Extract Requirement Changes
        ↓
Groq
        ↓
Proposed Changes
```

Possible fields:

- BHK
- Budget
- Location
- Timeline
- Parking required

---

# 8. Human Confirmation Before Requirement Updates

AI does **not** directly overwrite the lead profile.

```text
Interaction
    ↓
AI extracts proposed changes
    ↓
Salesperson reviews
    ↓
Confirm / Apply
    ↓
Backend validates
    ↓
Lead profile updated
    ↓
Priority recalculated
    ↓
Property matching recalculated
```

This keeps the salesperson in control of important customer information.

---

# 9. Evolving Lead Profile — Main Differentiator

The current lead profile is the **current source of truth**.

Current state:

```text
LEADS
```

Historical information:

```text
INTERACTIONS
```

Evolution:

```text
Initial Requirement
       ↓
Customer Interaction
       ↓
Requirement Change
       ↓
Salesperson Confirmation
       ↓
Updated Lead Profile
       ↓
New Property Matches
```

This means the system adapts as the salesperson learns more about the customer.

---

# 10. Deterministic Property Matching

Property matching deliberately **does not use Groq**.

It uses structured requirements and property data:

- Budget
- BHK
- Location
- Parking
- Timeline

Current scoring:

```text
Budget       → 30
BHK          → 25
Location     → 20
Parking      → 15
Timeline     → 10
```

Only properties meeting:

```text
match_score >= 45
```

are stored as matches.

The system also provides reasons and mismatches.

```text
Lead Requirements
       +
Property Data
       ↓
Deterministic Matching
       ↓
Match Score
       ↓
Reasons + Mismatches
```

### Why deterministic matching?

Property matching is an application/business decision, so explicit rules make it:

- Predictable
- Explainable
- Repeatable
- Easier to debug
- Independent of LLM variability

The LLM is used for language understanding, while structured application logic handles matching.

---

# 11. Lead ↔ Property Journey

A lead can have multiple properties.

Statuses:

```text
Recommended
Shortlisted
Shared
Site Visit Scheduled
Visited
Interested
Not Interested
```

```text
Lead
 ↓
Matched Properties
 ↓
Salesperson interacts with property
 ↓
Status changes
 ↓
Customer journey updated
```

---

# 12. Customer Journey

The lead detail page tracks:

- Interaction type
- Interaction note
- Customer feedback
- Requirement-change proposals
- Requirement updates
- Property journey/status

```text
Lead
 ↓
Interactions
 ↓
Customer Feedback
 ↓
Requirement Evolution
 ↓
Property Matching Changes
 ↓
Sales Progress
```

---

# 13. Property Management

The property database contains:

- Property code
- Project name
- Location
- Price
- BHK
- Parking
- Other property attributes

Salespeople can:

- View properties
- Search/filter properties
- View property information
- Match properties to leads

---

# 14. Dashboard

The dashboard provides a sales pipeline overview:

- HOT leads
- WARM leads
- COLD leads
- NEW leads
- NEEDS ATTENTION
- Lead statistics
- Lead/property information

---

# 15. AI Cost Control

AI is called only for explicit AI actions:

- Analyze Lead
- Re-analyze Lead
- Lead Assistant Chat
- Extract Requirement Changes

No automatic AI calls are required for:

- Page loading
- GET requests
- Filtering
- Property search
- Normal interaction saving
- Status changes
- Applying already-confirmed changes
- Deterministic rematching

This avoids unnecessary AI API usage.

---

# 16. Graceful AI Failure

If Groq is unavailable, non-AI functionality can still operate:

- Lead CRUD
- Property CRUD
- Interactions
- Priority calculation
- Property matching
- Status updates
- Requirement updates

AI-specific operations fail with an error rather than generating fake responses.

---

# 17. Technology Stack

## Frontend

### Next.js
Used for the web application and page structure.

### TypeScript
Used for type-safe frontend development and API/UI data handling.

### Tailwind CSS
Used for UI styling.

## Backend

### Python
Used for backend API implementation and business logic.

### FastAPI
Used to build the REST API and connect the frontend with backend services.

### SQLAlchemy
Used as the Python ORM/database layer for:

- Database models
- Queries
- Lead persistence
- Property persistence
- Interaction storage
- Lead-property relationships
- Updates

### Alembic
Used for versioned database schema migrations.

Production database schema is managed through migrations instead of runtime `create_all()`.

### PostgreSQL / Supabase
Used as the persistent relational database.

Main entities:

```text
users
leads
properties
interactions
lead_properties
```

AI data:

```text
AI analysis → lead
AI extracted changes → interaction
```

### Pydantic
Used for request/response validation and validating structured AI output.

```text
Groq
 ↓
JSON
 ↓
Pydantic Validation
 ↓
Application
```

### Groq
Used for AI features.

Model:

```text
openai/gpt-oss-20b
```

Temperature:

```text
0
```

The API key is stored as a backend environment variable and is never exposed to the frontend.

---

# 18. Backend Architecture

```text
Frontend
   ↓
FastAPI API
   ↓
Routes
   ↓
Services
   ├── Priority Service
   ├── Matching Service
   ├── AI Service
   └── Normalization
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

| Component | Purpose |
|---|---|
| FastAPI | REST API |
| Routes | API request/response handling |
| Priority Service | Lead scoring and priority |
| Matching Service | Deterministic property matching |
| AI Service | Groq integration and AI tasks |
| Normalization | Normalize/validate requirements |
| SQLAlchemy | ORM/database access |
| PostgreSQL | Persistent data |
| Alembic | Database migrations |
| Pydantic | Data validation |

---

# 19. AI Architecture

```text
FastAPI
   ↓
AI Service
   ↓
Groq API
   ↓
Structured JSON
   ↓
Pydantic Validation
   ↓
Application
```

AI responsibilities:

```text
Lead Analysis
Re-analysis
Contextual Assistant
Requirement Change Extraction
```

Deterministic responsibilities:

```text
Priority Calculation
Property Matching
Match Score
Database Updates
Status Changes
Rematching
```

This separation keeps important business logic predictable.

---

# 20. Overall System Architecture

```text
                  ┌─────────────────────────┐
                  │       Next.js            │
                  │  TypeScript + Tailwind   │
                  └────────────┬────────────┘
                               │
                            REST API
                               │
                               ▼
                  ┌─────────────────────────┐
                  │        FastAPI           │
                  │         Backend          │
                  └────────────┬────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │  Priority   │  │  Matching   │  │ AI Service  │
       │  Service    │  │  Service    │  │             │
       └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │  SQLAlchemy  │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ PostgreSQL   │
                       └──────────────┘

AI Service ────────────────► Groq API
```

---

# 21. Complete Lead Flow

```text
New Lead
   ↓
Lead Created
   ↓
Base Priority Calculated
   ↓
Property Matching
   ↓
Lead Appears on Dashboard
   ↓
Salesperson Opens Lead
   ↓
Analyze Lead [Optional]
   ↓
AI Analysis
   ↓
Salesperson Contacts Customer
   ↓
Interaction Added
   ↓
Dynamic Priority Recalculated
   ↓
Customer Requirement Changes?
   │
   ├── NO
   │    ↓
   │  Continue Sales Process
   │
   └── YES
        ↓
     Extract Changes
        ↓
     AI Proposed Changes
        ↓
     Salesperson Confirms
        ↓
     Update Lead
        ↓
     Recalculate Priority
        ↓
     Recalculate Property Matches
```

---

# 22. Deployment Architecture

```text
                     Internet
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      ┌─────────────┐       ┌─────────────┐
      │   Render    │       │   Render    │
      │  Frontend   │──────►│   Backend   │
      │   Next.js   │ REST  │   FastAPI   │
      └─────────────┘       └──────┬──────┘
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                  ┌─────────────┐     ┌─────────────┐
                  │ PostgreSQL  │     │  Groq API   │
                  │  Supabase   │     │     AI      │
                  └─────────────┘     └─────────────┘
```

Deployment:

```text
Frontend → Render
Backend  → Render
Database → PostgreSQL / Supabase
AI       → Groq
```

---

# 23. What Was Added Beyond the Basic Assignment

The project goes beyond basic lead intake + AI analysis + chatbot functionality.

## 1. Evolving Lead Profile

Customer requirements can change over time.

The current profile is updated only after salesperson confirmation, while historical interactions are retained.

## 2. Dynamic Lead Priority

Lead priority changes based on actual customer interactions instead of remaining fixed after lead creation.

## 3. Requirement Change Detection

AI can identify structured changes from an unstructured salesperson interaction.

## 4. Human-in-the-loop Confirmation

AI proposes changes, but the salesperson decides whether to apply them.

## 5. Dynamic Property Rematching

When the confirmed requirements change, property matches are recalculated.

## 6. Deterministic and Explainable Matching

Property matching uses explicit rules instead of asking an LLM to invent a match percentage.

## 7. Property Journey Tracking

A salesperson can track the relationship between a lead and a property through statuses such as Recommended, Shortlisted, Shared, Site Visit Scheduled, Visited, Interested, and Not Interested.

## 8. AI Scope Control

The contextual assistant is restricted to the selected lead's sales context rather than functioning as an unrestricted chatbot.

---

# 24. Complete Product Differentiator

Traditional lead management:

```text
Static Lead Information
        ↓
Property Recommendation
```

EstateFlow AI:

```text
Evolving Lead Profile
        +
Dynamic Priority
        +
Dynamic Property Matching
        +
Contextual AI Assistance
        ↓
Salesperson Action
```

The core idea is:

> **A real-estate lead is not static. Its priority, requirements, property matches, and recommended sales actions can change as the salesperson learns more from the customer.**

---

# 25. Local Development

## Backend

```bash
cd backend

python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```env
DATABASE_URL=postgresql://...
GROQ_API_KEY=...
```

Run migrations:

```bash
alembic upgrade head
```

Seed demo data:

```bash
python seed.py
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Configure the frontend API URL according to the project's environment configuration.

---

# 26. Known Limitations

- AI functionality depends on Groq API availability and limits.
- AI output is limited to the information available in the lead context.
- Property matching depends on the structured property attributes stored in the database.
- The project is a focused salesperson workspace, not a complete enterprise CRM, booking, payment, or documentation platform.

---

# 27. AI Usage

AI is used inside the application for:

1. Lead analysis
2. Lead re-analysis
3. Contextual lead assistant
4. Requirement-change extraction

AI coding assistance used during development should be disclosed separately according to the assignment requirements.

---

# 28. Project Summary

EstateFlow AI connects lead management, AI language understanding, deterministic business logic, and property matching into one salesperson workflow.

```text
Inbound Lead
     ↓
AI Understanding
     ↓
Dynamic Priority
     ↓
Sales Interaction
     ↓
Requirement Evolution
     ↓
Property Rematching
     ↓
Contextual AI Assistance
     ↓
Salesperson Action
     ↓
Customer Conversation
```

The system uses AI where natural-language understanding is valuable and deterministic backend logic where predictable business decisions are required.
