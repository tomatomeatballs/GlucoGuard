# Project Log

## 28 June 2026
Fully integrated the core predictive pipeline and database logging into the interactive Streamlit application (app.py).
Completed:
- Connected user inputs with standard line charts for multi-source historical and predicted trend visualization.
- Implemented a complete real-time Blood Glucose Prediction form interface.
- Integrated asynchronous multi-source trend charting to overlay real-time historical trends alongside future AI prediction windows.

## 27 June 2026
Aligned the algorithmic backend with the Streamlit interactive UI (app.py).
Completed:
- Upgraded the Blood Glucose Prediction console to pipe user entries directly into local SQLite storage using db.py.

Completed:
- Re-engineered the Model Training panel to read real-time slider and selectbox parameters.
- Implemented a complete real-time Blood Glucose Prediction form interface.


## 25 June 2026
Integrated the core algorithmic prediction pipeline into the main application backend (main.py).

Completed:
- Added vmdpy for signal decomposition into 5 IMF components.
- Integrated Nutcracker Optimization Algorithm (NOA) for hyperparameter tuning.
- Implemented component-wise BiLSTM prediction modeling.
- Automated input sequence length (Look-back) deduction from data columns.
- Added VMD signal decomposition plot generation and saving.
- Connected performance evaluation using MAE, RMSE, and Clarke error grids.


## 18 June 2026

Integrated the SQLite database MVP into the main Streamlit application.

Completed:
- Connected the existing login system with the database dashboard.
- Added glucose record input after login.
- Stored glucose records in SQLite through `db.py`.
- Displayed glucose history table from the database.
- Added glucose trend visualization.
- Added a simple latest glucose risk level indicator.


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

## 5 June 2026
Upgraded the login card design with clear font configurations and personalized system titles.

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