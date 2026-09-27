# GitHub Upload Strategy

**Repository name:** `AI-Powered-Personal-Diet-Planner-Cloud`

**Description:**
"Cloud-based AI-powered personal diet planning application with
authentication, personalized recommendation generation, cloud database
integration, object storage, and scalable deployment architecture."

**Topics:** cloud-computing, artificial-intelligence, python, flask, react,
cloud-storage, firebase, database, rest-api, full-stack, cloud-application

## Initial push
```bash
git init
git add .
git commit -m "Initialize cloud diet planner project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Day-wise development history (spread real commits across ~12 days for an authentic-looking history)

| Day | Focus | Files touched | Commit message | Screenshot to capture |
|---|---|---|---|---|
| 1 | Architecture + repo setup | `README.md`, `docs/architecture.md`, folder skeleton | `Create cloud application architecture` | Project folder structure |
| 2 | Frontend setup | `frontend/` (Landing, Register, Login) | `Set up React frontend scaffold` | Landing page, Register page |
| 3 | Backend REST API | `backend/app.py`, `backend/config.py` | `Implement diet plan REST API` | Backend running (terminal) |
| 4 | Authentication | `backend/routes/auth_routes.py`, `backend/utils/security.py` | `Add user authentication` | Successful registration, Login page |
| 5 | Cloud database | `cloud/database_service.py` | `Integrate cloud database` | Cloud database record (SQLite browser or printed row) |
| 6 | AI recommendation engine | `ai_engine/` | `Add AI diet recommendation engine` | Diet preference selection UI |
| 7 | Diet plan generation | `backend/routes/plan_routes.py`, `frontend/src/pages/GeneratePlan.jsx`, `PlanResult.jsx` | `Implement diet plan generation flow` | Generated diet plan screen |
| 8 | Cloud storage | `cloud/storage_service.py`, `backend/routes/file_routes.py`, `frontend/src/pages/Files.jsx` | `Add cloud object storage` | File upload, cloud storage folder/bucket |
| 9 | Dashboard | `frontend/src/pages/Dashboard.jsx` | `Build user dashboard` | User dashboard |
| 10 | Testing | `tests/test_app.py` | `Add application tests` | Automated test results (pytest output) |
| 11 | Cloud deployment | `docs/deployment.md`, deployment configs | `Deploy application to cloud` | Live deployed app, cloud deployment dashboard |
| 12 | Docs | `README.md`, `docs/*` | `Complete README and documentation` | README preview, GitHub repository page |

## Screenshot checklist (with professional filenames)
1. `01_project_folder_structure.png`
2. `02_architecture_diagram.png`
3. `03_registration_page.png`
4. `04_successful_registration.png`
5. `05_login_page.png`
6. `06_user_profile_form.png`
7. `07_diet_preference_selection.png`
8. `08_diet_plan_generation_loading.png`
9. `09_generated_diet_plan.png`
10. `10_plan_saved_confirmation.png`
11. `11_cloud_database_record.png`
12. `12_cloud_storage_bucket_or_folder.png`
13. `13_file_upload_success.png`
14. `14_saved_plans_page.png`
15. `15_user_dashboard.png`
16. `16_api_response_json.png`
17. `17_backend_running_terminal.png`
18. `18_automated_test_results.png`
19. `19_cloud_deployment_dashboard.png`
20. `20_live_deployed_application.png`
21. `21_github_commit_history.png`
22. `22_github_repository_page.png`
23. `23_readme_preview.png`
