# Project Log

## Effort & Time Investment Log

Estimated time invested by each member across the project (Liftoff through mid-July 2026).
Hours are approximate estimates, as detailed time tracking was not kept from the start.
Work was split between algorithm/database (Xiao Hongyu) and frontend/model-integration
(Li Yingzhuo); meetings, peer evaluations, and self-directed learning were shared.

| S/N | Task | Date | Xiao Hongyu (hrs) | Li Yingzhuo (hrs) | Remarks |
|---|---|---|---|---|---|
| 1 | [Meeting] Liftoff project planning | 12 May 2026 | 2 | 2 | Team meeting to plan the project idea, motivation, and Liftoff deliverables. |
| 2 | Liftoff poster & pitch video | 13–15 May 2026 | 3 | 4 | Created the poster and pitch video for the Orbital Liftoff submission. |
| 3 | Self-learning: Python & Streamlit basics | 15–20 May 2026 | 5 | 7 | Watched tutorials on Python and Streamlit to build the web application. |
| 4 | Milestone 1 login prototype (Streamlit) | 20–28 May 2026 | 4 | 8 | Built the login prototype: username/password login, session state, role-based welcome, logout. |
| 5 | [Meeting] Milestone 1 scope & submission | 29 May 2026 | 1 | 1 | Meeting to confirm the Milestone 1 proof-of-concept scope and submission plan. |
| 6 | Milestone 1 README, requirements & project log | 30–31 May 2026 | 3 | 2 | Wrote the README, requirements.txt, and project log; organised the GitHub repository. |
| 7 | Milestone 1 testing & GitHub submission | 31 May 2026 | 2 | 2 | Tested the login flow locally and prepared the Milestone 1 submission. |
| 8 | Self-learning: SQLite & database design | 3–10 June 2026 | 7 | 2 | Studied SQLite, schema design, and basic CRUD operations for the database layer. |
| 9 | Login card redesign & system titles | 5 June 2026 | 1 | 3 | Redesigned the login card with clearer fonts and personalised system titles. |
| 10 | SQLite database MVP (db.py) | 18 June 2026 | 6 | 1 | Built db.py: SQLite structure, users and glucose_records tables, init/insert/read functions. |
| 11 | Integrating the database dashboard into the app | 18 June 2026 | 4 | 3 | Connected login with the database dashboard; added glucose input, history table, and trend chart. |
| 12 | Self-learning: ML & time-series (VMD/NOA/BiLSTM) | 15–24 June 2026 | 7 | 8 | Studied machine-learning fundamentals and the VMD, NOA, and BiLSTM methods behind the model. |
| 13 | VMD-NOA-BiLSTM prediction pipeline (main.py) | 25 June 2026 | 10 | 3 | Implemented VMD decomposition, NOA tuning, component-wise BiLSTM, and error metrics. |
| 14 | Aligning the algorithm backend with the UI | 27 June 2026 | 4 | 4 | Piped user entries into SQLite and read training parameters from the Streamlit UI. |
| 15 | Integrating the pipeline & trend charts (app.py) | 28 June 2026 | 3 | 8 | Integrated the prediction pipeline and multi-source trend charts into the Streamlit app. |
| 16 | [Meeting] Milestone 2 progress & deliverables | 26 June 2026 | 1.5 | 1.5 | Meeting to review Milestone 2 progress and plan the report, poster, and video. |
| 17 | Milestone 2 report/README & poster | 26–29 June 2026 | 4 | 6 | Wrote the Milestone 2 report/README and prepared the poster. |
| 18 | Milestone 2 submission | 29 June 2026 | 1 | 1 | Submitted the Milestone 2 deliverables. |
| 19 | Advisor demo & consultation | late June 2026 | 2 | 2 | Demonstrated the app to our advisor (Kwa Jian Quan) and collected feedback. |
| 20 | Peer Evaluation 1 (HealthSync) | June 2026 | 5 | 5 | Completed the Orbital peer evaluation for HealthSync. |
| 21 | Peer Evaluation 2 (Lumina) | June–July 2026 | 5 | 5 | Completed the Orbital peer evaluation for Lumina. |
| 22 | Data validation for uploaded training files | 5 July 2026 | 2 | 2 | Added validation for uploads (column count, missing values, non-numeric data). |
| 23 | Poster redesign (advisor feedback) | July 2026 | 2 | 3 | Redesigned the poster based on advisor feedback. |
| 24 | Reading & understanding the codebase | July 2026 | 7 | 5 | Read through the prediction pipeline and data flow before making changes. |
| 25 | Sliding-window data preprocessing (raw → 15/30/50min) | July 2026 | 4 | 6 | Designed and tested the conversion from raw glucose data into the three model datasets. |
| 26 | Database redesign planning (per-user file storage) | July 2026 | 4 | 2 | Planned the database redesign for per-user storage of uploaded and generated files. |
| 27 | [Meeting] Post-demo syncs & task planning | July 2026 (ongoing) | 3 | 3 | Ongoing weekly syncs to triage bugs and plan the next development steps. |
| | **Total (hours)** | | **102.5** | **99.5** | **Combined: 202 hours** |

---

## Milestone 2 Summary

For Milestone 2, GlucoGuard moved from a login-only proof of concept to a working
prototype that combines a database, an interactive web application, and a real glucose
prediction algorithm.

**Completed in Milestone 2**

- Integrated a SQLite database (`db.py`) for storing glucose records, with functions to
  initialise the database and to insert and read records.
- Built a multi-page Streamlit web application covering Login, Dashboard, Model Training,
  Glucose Prediction, and AI Consultation.
- Implemented the core VMD-NOA-BiLSTM prediction pipeline (Variational Mode Decomposition
  → Nutcracker Optimization Algorithm → Bidirectional LSTM). Run on its own, it produces
  real RMSE, MAE, and MAPE metrics and generates VMD decomposition, prediction, and
  Clarke error grid plots.
- Added glucose record input, a history table, and trend visualisation backed by the
  database.
- Added validation for uploaded training files (column count, missing values, and
  non-numeric data).

**In progress (to be completed in later milestones)**

- Full integration of the VMD-NOA-BiLSTM algorithm into the web app. The Model Training
  and Glucose Prediction pages currently demonstrate the intended workflow with
  placeholder output; wiring the real pipeline end-to-end into the browser is still in
  progress.
- Connecting uploaded raw data through sliding-window preprocessing into the algorithm,
  so that training uses each user's own uploaded data rather than fixed local files.
- Real user registration and login with password hashing and per-user data isolation
  (the current build uses demo accounts).
- Moving generated result files from local storage into the database to support
  deployment.

---

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