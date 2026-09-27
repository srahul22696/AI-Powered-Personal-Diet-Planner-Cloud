# Testing Strategy

Automated tests live in `tests/test_app.py` (pytest). Run with:
```bash
pytest tests/ -v
```
All 18 automated tests pass as of the last run.

## Test Case Table

| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|
| TC01 | New user registration | Valid name/email/password | 201 + access_token | 201 + access_token | Pass |
| TC02 | Existing email registration | Duplicate email | 409 error | 409 error | Pass |
| TC03 | Valid login | Correct credentials | 200 + access_token | 200 + access_token | Pass |
| TC04 | Invalid login | Wrong password | 401 error | 401 error | Pass |
| TC05 | Unauthorized dashboard access | No token on /profile | 401 error | 401 error | Pass |
| TC06 | Profile creation | Valid profile fields | 200 + updated profile | 200 + updated profile | Pass |
| TC06b | Profile validation | age = 500 | 400 validation error | 400 validation error | Pass |
| TC07 | Diet plan generation | Any valid preference/goal | 201 + 4 meals | 201 + 4 meals | Pass |
| TC08 | Vegetarian preference | dietary_preference=vegetarian | Only veg-tagged meals | Only veg-tagged meals | Pass |
| TC08b | Vegan preference | dietary_preference=vegan | Only vegan-tagged meals | Only vegan-tagged meals | Pass |
| TC09 | Different goal | goal=weight_loss | Plan generated, adjusted calorie logic used | Plan generated | Pass |
| TC10 | AI API failure | AI_API_URL/KEY unset | Falls back automatically | source=rule_based_fallback | Pass |
| TC11 | Rule-based fallback | (same as TC10) | Valid 4-meal plan returned | Valid plan returned | Pass |
| TC12 | Save diet plan | Generate plan | Plan appears in /plans | Plan appears in /plans | Pass |
| TC13 | Retrieve plan | GET /plans/{id} | 200 + full plan | 200 + full plan | Pass |
| TC14 | Upload file | Valid .txt file | 201 + file metadata | 201 + file metadata | Pass |
| TC15 | Retrieve file | GET /files/{id}/download | 200 + file bytes | 200 + file bytes | Pass |
| TC16 | Invalid file | .exe file | 400 rejected | 400 rejected | Pass |
| TC17 | Cross-user isolation | User B requests User A's plan_id | 404 (not found, not leaked) | 404 | Pass |
| TC18 | Logout | POST /logout | 200 message | 200 message | Pass |
| TC19 | Storage failure handling | File removed from disk, then downloaded | 410 Gone | 410 Gone | Pass |

## Manual / Exploratory Checks (do these once before recording your demo video/screenshots)
- Register → complete profile → generate plan → save → log out → log back in
  → confirm the same plan is still visible (proves cloud persistence).
- Upload an image, then delete it, then confirm it disappears from the list.
- Try generating a plan with allergies set (e.g. "egg") and confirm egg-based
  meals are avoided.

## What's not covered by automated tests (documented honestly, not hidden)
- Real external AI-API integration is mocked/absent by design (no paid key
  required) — the fallback path is what's actually tested.
- Load/performance testing under concurrent users is out of scope for this
  student project; `docs/scalability.md` discusses it conceptually instead.
