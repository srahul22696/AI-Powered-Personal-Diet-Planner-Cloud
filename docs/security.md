# Cloud Security

| Concept | Implementation in this project |
|---|---|
| Authentication | JWT issued on login/register (`flask-jwt-extended`); required on all protected routes via `@jwt_required()` |
| Authorization | Every DB query is scoped to `get_jwt_identity()` — a user can only ever act on their own rows |
| Password security | Passwords hashed with salted PBKDF2 (`werkzeug.security`) — never stored or logged in plain text |
| Authentication tokens / JWT | Stateless bearer tokens with a configurable expiry (`JWT_ACCESS_TOKEN_EXPIRES_MINUTES`) |
| Session concepts | No server-side session state is kept — this is what allows horizontal scaling |
| User isolation | Verified explicitly in `tests/test_app.py::test_user_isolation` |
| HTTPS | Not applicable locally; enforced automatically by Firebase Hosting/Cloud Run/most PaaS providers in production |
| Encryption in transit | Provided by HTTPS at the hosting layer once deployed |
| Encryption at rest | Provided by the managed cloud DB/storage provider (Firestore/S3 encrypt at rest by default) |
| Environment variables | All secrets read via `os.environ` (`backend/config.py`); `.env` is gitignored, only `.env.example` is committed |
| Secrets management | For real cloud deployment, use the platform's secret manager (GCP Secret Manager, AWS Secrets Manager) instead of plain env vars where possible |
| API-key protection | `AI_API_KEY` is never sent to the frontend and never logged |
| Database access rules | User-scoped queries (see User isolation); in a real Firestore deployment, this is reinforced with Firestore Security Rules |
| Object-storage permissions | Files are stored per-user (`users/{uid}/files/...`); in production, use private buckets + short-lived signed URLs instead of public links |
| Input validation | `backend/utils/security.py::validate_profile_fields`, allowed-file-extension check in `storage_service.py`, max file size limit |
| Rate limiting | Not implemented in this demo; recommended addition: `Flask-Limiter` on `/login` and `/register` to slow brute-force attempts |
| CORS | Restricted to `FRONTEND_ORIGIN` only (`backend/app.py`), not wide open to `*` |
| Logging | AI-engine fallback events and Flask error handlers log without ever logging secrets or passwords |
| Backups | Managed cloud databases (Firestore/RDS) provide automated backups; not applicable to the local SQLite demo |

## Common mistakes students should avoid
- Hardcoding API keys or passwords directly in source files (always use env vars).
- Committing the real `.env` file to GitHub (only commit `.env.example`).
- Returning different error messages for "user not found" vs "wrong
  password" on login (this leaks which emails are registered).
- Returning 403 instead of 404 when a user requests someone else's
  resource by id (403 confirms the id exists; 404 does not).
- Trusting client-submitted values for anything security-sensitive
  (always re-derive `user_id` from the verified JWT, never from the
  request body).
- Leaving CORS wide open (`origins: "*"`) in a production deployment.
