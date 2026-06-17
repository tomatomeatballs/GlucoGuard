# Project Log
## 18 June 2026

Implemented a basic SQLite database MVP for GlucoGuard.

Completed:
- Created `db.py` for database operations.
- Created a local SQLite database structure using SQLite.
- Added `users` and `glucose_records` tables.
- Implemented functions to initialize the database, insert glucose records, and read glucose records.
- Created `app_database_demo.py` to test the Streamlit-to-database workflow.
- The demo can now add glucose records, save them to SQLite, display historical records, and visualize glucose trends.
- Tested manual glucose record input through the Streamlit interface.

## 31 May 2026

### Xiao Hongyu

- Reviewed the Orbital Milestone 1 submission requirements.
- Set up and organized the clean Milestone 1 project folder.
- Tested the Streamlit login prototype locally using `localhost`.
- Verified the admin login flow and logout function.
- Prepared and refined the GitHub submission files, including `README.md`, `requirements.txt`, and `project_log.md`.
- Coordinated with teammate on the final Milestone 1 submission scope and GitHub preparation.

### Li Yingzhuo

- Prepared the initial Streamlit login module prototype.
- Implemented the basic authentication flow with username and password.
- Added simulated admin and standard user accounts.
- Added role-based welcome messages and logout functionality.
- Drafted the initial README instructions for running the demo.
- Confirmed that the Milestone 1 technical proof of concept should focus on the login-only prototype.

## Milestone 1 Current Progress

For Milestone 1, the team prepared a basic Streamlit login prototype for the CGM Glucose Monitoring System.

The prototype demonstrates:

- Username and password login
- Simulated user database
- Session management
- Role-based welcome page
- Logout function

This is a technical proof of concept only. The full glucose prediction model, database integration, dashboard, and health report generation will be developed in later milestones.

---

## Next Steps

- Upload the Milestone 1 files to GitHub.
- Submit the README URL and Project Log URL to Skylab.
- Reuse the Liftoff poster and video links for Milestone 1 submission.
- Continue integrating the prediction model and dashboard features after Milestone 1.