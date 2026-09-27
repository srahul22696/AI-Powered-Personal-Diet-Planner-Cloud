# Interview Preparation

## 10 Predicted Questions & Answers

**1. Explain your project.**
I built a cloud-based AI-powered personal diet planner. Users register and
log in with JWT-based authentication, fill in a demo profile (age, height,
weight, activity level, dietary preference, goal), and generate a
personalized meal plan. The recommendation engine is rule-based by default
and can call an external AI API if one is configured, with automatic
fallback if that API is unavailable. Plans and file uploads are stored
through cloud-database and cloud-storage abstraction layers, so each user
only ever sees their own data, and the same service interfaces can be
pointed at real managed services (Firestore, Firebase Storage) without
changing the rest of the app.

**2. Why did you use cloud computing for this project?**
Cloud infrastructure lets the same app be reached from any device, scales
the backend and storage independently of any one machine, and separates
concerns (compute, structured data, files) into services that can each be
managed, secured, and scaled on their own terms.

**3. What is the difference between cloud database and cloud storage in your project?**
The cloud database (`cloud/database_service.py`) stores structured records
— users, diet plans, file metadata. Cloud object storage
(`cloud/storage_service.py`) stores the raw file bytes — uploaded images
and exported plan text files. Metadata that needs to be searched/filtered
belongs in the database; large or binary content belongs in object
storage.

**4. How does the AI recommendation engine work?**
The backend builds a structured request (diet preference, goal, allergies,
target calories) and, if an AI API key/URL is configured, sends it there
first. If that call fails, times out, or returns an unexpected shape, the
code catches the exception and falls back to a local rule-based engine
that selects meals from a small food dataset filtered by diet preference
and allergy keywords — so the app always returns a usable plan.

**5. How did you secure user data?**
Passwords are hashed (never stored in plain text). Every protected route
requires a valid JWT, and every database query is filtered by the user id
extracted from that token, so one user can never read or modify another
user's data — I have an automated test specifically for this. Secrets
(JWT key, AI API key) are read from environment variables, never
hardcoded, and `.env` is excluded from Git.

**6. What is the role of REST APIs in this project?**
They're the contract between frontend and backend — endpoints like
`/register`, `/generate-plan`, `/plans`, and `/upload` let the React app
and the Flask server evolve independently, as long as the API shape stays
stable.

**7. What happens if the AI API fails?**
The failure is caught in `diet_engine.generate_plan()`, logged, and the
function transparently returns a rule-based plan instead — the API
response looks the same to the frontend either way, just with
`source: "rule_based_fallback"` instead of `"ai_api"`.

**8. How would you scale this application if the number of users increased significantly?**
I'd swap SQLite for a managed database and local disk for real object
storage (both already isolated behind service interfaces), run multiple
stateless backend instances behind a load balancer, add autoscaling, put a
CDN in front of the frontend, and add caching for the static food catalog.
This is documented in detail in `docs/scalability.md`.

**9. How did you test this project?**
I wrote 18 automated pytest tests covering registration, login,
authorization failures, profile validation, plan generation across all
diet preferences and goals, the AI-fallback path, plan and file
CRUD operations, and — critically — a dedicated cross-user isolation test
that confirms User B cannot fetch User A's plan by id.

**10. How can this project be improved further?**
Add real push notifications, a proper CI/CD pipeline, rate limiting on
auth endpoints, infrastructure-as-code for the cloud resources, and
richer analytics on intake history. Any medical/nutrition claims would
need professional and regulatory review before this could be anything
beyond an educational demo.

---

## Resume Bullet Points
- Built a full-stack, cloud-architected diet-planning app (React + Flask)
  with JWT authentication, a rule-based AI recommendation engine with
  automatic fallback, and swappable cloud database/storage service layers.
- Implemented strict per-user data isolation and validated it with an
  automated pytest suite (18 tests, including a dedicated cross-user
  access test).
- Designed the backend around service abstractions so the local
  SQLite/disk-based demo can be swapped for Firestore/Firebase Storage or
  AWS RDS/S3 without changing any route logic.

## 2-line resume description
Cloud-architected AI-powered diet planner (React/Flask) with JWT auth,
rule-based + AI-fallback recommendations, and isolated per-user cloud
database/storage layers; 18 automated tests covering security and
functionality.

## LinkedIn project description
"I built an AI-Powered Personal Diet Planner as a cloud-computing project:
a React frontend, a Flask REST API, JWT-based authentication, and a
recommendation engine that calls an AI API when available and
transparently falls back to a rule-based engine otherwise. The database
and file-storage layers are built as swappable service abstractions
(currently SQLite + local disk for free local development, designed to
point at Firestore/Firebase Storage in production), with strict per-user
data isolation verified by an automated test suite. This is an
educational project using synthetic data — generated plans are general
wellness examples, not medical advice."

## Technical skills demonstrated
React, Flask, REST API design, JWT authentication, password hashing,
SQL/SQLite, service-layer architecture, cloud storage abstraction,
rule-based recommendation systems, fallback/error-handling design, pytest,
Git/GitHub workflow, cloud deployment concepts (Firebase/GCP/AWS).

## Suggested GitHub repository description
"Cloud-based AI-powered personal diet planning application with
authentication, personalized recommendation generation, cloud database
integration, object storage, and scalable deployment architecture."
