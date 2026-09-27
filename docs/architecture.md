# System Architecture & Cloud Computing Concepts

## Simple Explanation
A user creates an account, tells the app a bit about themselves (age,
height, weight, diet preference, goal), and the app generates a meal plan
for the day. The plan and any uploaded files are saved online, so the user
can log in from any device and see the same data.

## Technical Explanation
The frontend (React) never talks to a database directly. It calls a REST
API (Flask). The API authenticates the request (JWT), talks to a **cloud
database service** for structured data (users, plans) and a **cloud object
storage service** for files/exports, and optionally calls an **AI engine**
(external API with a local rule-based fallback) to generate the plan.

```
User
 ↓
Web Application (React)
 ↓
Authentication (JWT)
 ↓
User Profile Input
 ↓
Cloud Backend/API (Flask REST)
 ↓
AI Diet Planner (rule-based + optional external AI, with fallback)
 ↓
Personalized Plan
 ↓
Cloud Database (structured: users, plans, file metadata)
 ↓
Cloud Storage (unstructured: uploaded files, plan exports)
 ↓
User Dashboard
```

### Layered view

```
CLIENT LAYER        Web Browser → React Frontend
APPLICATION LAYER    REST API → Flask Backend
AI LAYER             Diet Recommendation Engine (ai_engine/)
DATA LAYER           Cloud Database (cloud/database_service.py)
STORAGE LAYER        Cloud Object Storage (cloud/storage_service.py)
AUTH LAYER           JWT-based Authentication Service
```

### Text architecture diagram

```
                        User
                         ↓
                      Frontend
                         ↓
                  Authentication (JWT)
                         ↓
                      REST API
                         ↓
                Backend Application (Flask)
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   AI Engine         Cloud DB       Cloud Storage
        └────────────────┼────────────────┘
                         ↓
                     Diet Plan
                         ↓
                    User Dashboard
```

## Cloud Database vs Cloud Object Storage
| | Cloud Database | Cloud Object Storage |
|---|---|---|
| Stores | Structured rows/documents (users, plans, file *metadata*) | Raw files (images, exports, PDFs) |
| In this project | `cloud/database_service.py` (SQLite locally → Firestore/Cloud SQL in production) | `cloud/storage_service.py` (local disk locally → Firebase Storage/S3 in production) |
| Query style | Filter/search by fields | Fetch/write by path/key |

## Where each Cloud Computing concept appears in this project

| Concept | Where it appears |
|---|---|
| Cloud Computing | Entire app is designed to run on remote, on-demand infrastructure (Firebase/AWS/GCP) rather than one fixed local machine |
| SaaS | The deployed diet planner itself, delivered to end users over the browser |
| PaaS | Deploying the Flask backend to a managed platform (Cloud Run / Render / Railway) — you don't manage the OS |
| IaaS (concept) | Explained in `docs/deployment.md` Option B (EC2/VM-based deployment) as the lower-level alternative |
| Cloud Storage | `cloud/storage_service.py` — file uploads and plan exports |
| Cloud Database | `cloud/database_service.py` — users, plans, file metadata |
| Object Storage | Same as Cloud Storage row above — unstructured file storage |
| Authentication | `backend/routes/auth_routes.py` + Flask-JWT-Extended |
| REST API | All endpoints in `backend/routes/*.py` |
| Client-Server Architecture | React frontend (client) ↔ Flask backend (server) over HTTP |
| Serverless Computing | Deployment guide shows deploying the Flask app as Cloud Functions/Cloud Run — scale-to-zero, pay-per-use |
| Scalability | `docs/scalability.md` |
| Availability | Stateless JWT auth + managed DB/storage means any backend instance can serve any request → no single point of failure once deployed behind a load balancer |
| Elasticity | Cloud Run/serverless auto-adds instances under load and removes them when idle |
| Load Balancing | Covered in `docs/scalability.md` — multiple backend instances behind a load balancer |
| API Gateway | Covered in `docs/scalability.md` and `docs/deployment.md` (Option B) |
| Environment Variables | `.env.example`, `backend/config.py` — no secrets hardcoded |
| Secrets Management | Same as above; production guidance uses cloud secret managers |
| Cloud Security | `docs/security.md` |
| Logging | `ai_engine/diet_engine.py` logs AI fallback events; Flask error handlers in `backend/app.py` |
| Monitoring | Covered in `docs/deployment.md` (cloud provider dashboards/logs) |
| Deployment | `docs/deployment.md` |
| CI/CD | Suggested GitHub Actions workflow in `docs/deployment.md` |

## Database Design

**USERS**: user_id (PK), name, email (unique), password_hash, age, height_cm,
weight_kg, activity_level, dietary_preference, goal, allergies (JSON list),
created_at.

**DIET_PLANS**: plan_id (PK), user_id (FK → users), breakfast, lunch, snack,
dinner (each JSON), nutrition_summary (JSON), source (`ai_api` |
`rule_based_fallback`), created_at.

**USER_FILES**: file_id (PK), user_id (FK → users), filename, storage_path,
content_type, size_bytes, uploaded_at.

**Relationships**: one user → many plans, one user → many files (1:N via
`user_id` foreign key). **User isolation** is enforced at the query level —
every read/update/delete filters by the `user_id` extracted from the
caller's own JWT, so User A can never fetch User B's rows even by guessing
an id (`GET /plans/{id}` returns 404, not 403, for another user's plan, to
avoid leaking which ids exist).
