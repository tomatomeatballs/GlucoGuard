# GlucoGuard — CGM Glucose Monitoring & AI Prediction System

> **Original project/team name: Orbital** (GlucoGuard is the project name as of Milestone 2)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Milestone 2 Progress Summary](#2-milestone-2-progress-summary)
3. [Features Implemented](#3-features-implemented)
4. [System Architecture](#4-system-architecture)
5. [Database Design](#5-database-design)
6. [Technology Stack](#6-technology-stack)
7. [How to Run](#7-how-to-run)
8. [User Guide](#8-user-guide)
9. [Testing](#9-testing)
10. [Known Limitations & Future Work](#10-known-limitations--future-work)
11. [Team Contributions](#11-team-contributions)
12. [Appendix: Milestone 1 Summary](#12-appendix-milestone-1-summary)

---

## 1. Project Overview

**GlucoGuard** is a Continuous Glucose Monitoring (CGM) support system designed for diabetes patients and healthcare professionals. It combines real-time glucose tracking, AI-powered future glucose prediction, and an interactive data visualization dashboard — all in a browser-based interface powered by Python and Streamlit.

### Motivation

Diabetes management is a daily challenge. Patients must monitor blood glucose levels multiple times a day and make decisions about diet, exercise, and medication based on trends that are difficult to see from raw numbers alone. GlucoGuard aims to:

- Help patients **understand their glucose trends** through clear visualizations
- Provide **AI-assisted predictions** of future glucose values (15–60 minutes ahead)
- Allow healthcare professionals to **train and compare prediction models** on patient data
- Store all records **securely in a local SQLite database** for historical review

### Target Users

- Diabetes patients who use Continuous Glucose Monitors
- Healthcare professionals and researchers working with CGM data
- Data scientists interested in glucose prediction algorithms

---

## 2. Milestone 2 Progress Summary

**Target Level of Achievement: Gemini.**

GlucoGuard implements **5 features of sufficient complexity** (meeting the Gemini requirement of 3–5 features) and makes full use of a **SQLite database** (meeting the Gemini database requirement). The five features are:

1. User Authentication System
2. Model Training Console
3. Real-time Blood Glucose Prediction (with data persistence)
4. Multi-Source Data Visualization
5. VMD-NOA-BiLSTM Algorithmic Prediction Backend

Compared to Milestone 1 (which only had a login page), Milestone 2 delivers a fully working multi-page application:

| Feature | Milestone 1 | Milestone 2 |
|---|---|---|
| User Login & Authentication | ✅ Simulated | ✅ Simulated + DB-backed structure |
| Dashboard | ❌ Placeholder | ✅ Welcome page with system status |
| Model Training Console | ❌ None | ✅ Full UI with file upload + pipeline simulation |
| Real-time Glucose Prediction | ❌ None | ✅ Data entry, DB storage, AI prediction, trend chart |
| AI Consultation Hub | ❌ None | ✅ In progress (UI in place) |
| SQLite Database | ❌ None | ✅ Full schema: users, glucose_records, training_files |
| Data Visualization | ❌ None | ✅ Multi-source trend chart (historical + predicted) |
| Algorithmic Backend (main.py) | ❌ None | ✅ VMD + NOA + BiLSTM pipeline |

### Effort Since Milestone 1

After Milestone 1, the team completed the following:

- Designed and implemented a full SQLite database schema (`db.py`) with three tables
- Built the Model Training page with Excel file upload, hyperparameter configuration, and a 7-step training pipeline simulation
- Built the Blood Glucose Prediction page with real-time data entry form, SQLite write/read, AI prediction output table, and multi-source trend line chart
- Integrated the `VMD-NOA-BiLSTM` algorithmic backend (`main.py`) with VMD signal decomposition, NOA optimization, component-wise BiLSTM modeling, error evaluation (MAE, RMSE, MAPE), and Clarke Error Grid Analysis
- Added sidebar navigation with `streamlit-option-menu`
- Refactored `app.py` to route between all 4 pages cleanly

---

## 3. Features Implemented

### Feature 1: User Authentication System

Users log in with a username and password. The system checks credentials against a pre-defined user dictionary and manages login state using `st.session_state`.

- Two built-in accounts: `admin` (Administrator) and `user` (Standard User)
- Session state persists across page navigation within one run
- Logout button clears the session and returns to the login page
- The database includes a `users` table for future full registration support

**Login credentials:**

| Username | Password | Role |
|---|---|---|
| admin | 123456 | Administrator |
| user | 123456 | Standard User |

---

### Feature 2: Dashboard

After login, users land on the Dashboard page showing:

- Personalized welcome message with the user's name and role
- System status overview listing all available modules
- Quick summary of GlucoGuard capabilities

---

### Feature 3: Model Training Console

The Model Training page supports the full workflow for training a glucose prediction model:

**Step 1 — Data Input**

- Users upload one or more `.xlsx` files containing CGM glucose records
- Each uploaded file is immediately parsed with `pandas` and saved to the `training_files` table in SQLite
- Upload status is shown via `st.toast` notifications
- Supported format: Excel files with glucose values at 15/30/50-minute intervals

**Step 2 — Hyperparameter Configuration**

Users configure training parameters via interactive UI controls:

| Parameter | Widget | Default |
|---|---|---|
| Predictive Algorithm | Dropdown | VMD-NOA-BiLSTM (Optimal) |
| Training Epochs | Slider | 200 (range: 50–500) |
| Train/Test Split Ratio | Slider | 0.6 (range: 0.5–0.9) |

Available algorithm choices:
- **VMD-NOA-BiLSTM** (currently optimal — described in detail below)
- LSTM Standard Model
- SVM Regression Model

**Step 3 — Launch Training**

- A 7-step progress bar simulates the training pipeline in the UI
- Steps correspond to real operations executed by `main.py` offline:
  1. Load training data from database
  2. VMD signal decomposition (K=5 IMF components)
  3. NOA swarm optimization (target epochs as configured)
  4. Dataset splitting (as configured ratio)
  5. BiLSTM parallel training per component
  6. Clarke Error Grid Analysis and metric calculations
  7. Export results to Excel report

---

### Feature 4: Real-time Blood Glucose Prediction

This is the core clinical feature of GlucoGuard. It allows users to enter their current blood glucose reading and receive an AI-generated prediction of future values.

**Data Entry Panel (left column)**

- Timestamped entry form using `st.form`
- Users enter their current blood glucose value in mmol/L (range: 1.0–30.0)
- On submission, the value and timestamp are written to the `glucose_records` SQLite table under the logged-in user's `user_id`
- Prediction window options: Next 15 / 30 / 45 / 60 minutes
- Configurable alert thresholds for hyperglycemia (default: 10.0 mmol/L) and hypoglycemia (default: 3.9 mmol/L)

**Prediction Core Panel (right column)**

- Checks for the presence of a trained model file (`models/latest_vmd_noa_bilstm.pkl`)
- If no model file found, runs in Demo Prediction Mode
- Executes prediction and outputs:
  - A **Future Predicted Metrics Table** showing predicted glucose values at +15, +30, +45, +60 minutes
  - A **Multi-Source Trend Chart** (Streamlit line chart) overlaying three data series:
    - Historical Data — last 10 records retrieved from `glucose_records` in SQLite
    - Current Input — the just-entered reading
    - AI Prediction — the 4 future predicted values

The multi-source trend chart automatically falls back to simulated historical context if no prior records are stored.

---

### Feature 5: AI Medical Consultation Hub

The AI Consultation page is currently scaffolded (title + placeholder message). The full chat-based interface connecting to an AI language model backend is planned for Milestone 3.

---

### Feature 6: VMD-NOA-BiLSTM Algorithmic Backend (`main.py`)

The `main.py` file implements the full offline prediction pipeline that powers the model training step. This is the core research contribution of the project.

**Pipeline Overview:**

```
Raw Excel Data
    ↓
Global NOA Optimization  →  Best [HiddenUnits, Epochs, LearningRate]
    ↓
VMD Decomposition        →  K=5 Intrinsic Mode Functions (IMFs)
    ↓
Component-wise BiLSTM    →  Prediction per IMF component
    ↓
Signal Reconstruction    →  Sum predictions across all IMFs
    ↓
Error Evaluation         →  MAE, RMSE, MAPE, Clarke Error Grid
    ↓
Export Results           →  Excel report + VMD plot PNG
```

**VMD (Variational Mode Decomposition)**

VMD decomposes the non-stationary glucose time series into K=5 frequency-band components (IMFs). This reduces the complexity of the prediction problem by allowing each BiLSTM to focus on a single frequency band. Parameters: α=2000, τ=0, K=5, DC=0, init=1, tol=1e-7.

**NOA (Nutcracker Optimization Algorithm)**

NOA is a bio-inspired swarm optimization algorithm used to search for the optimal BiLSTM hyperparameters (hidden units, epochs, learning rate) on the full raw dataset before component-wise training begins. This global optimization ensures all component models share the same optimal configuration.

**BiLSTM (Bidirectional Long Short-Term Memory)**

BiLSTM processes each IMF component independently. The input to each BiLSTM is the auxiliary feature columns from the original dataset combined with the current IMF column, following the design: `X_imf = [X_original_features | IMF_i]`. The final prediction is the sum of all component predictions.

**Error Metrics**

After training, the pipeline evaluates performance using:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- MAPE (Mean Absolute Percentage Error)
- Clarke Error Grid Analysis (clinical-grade accuracy assessment)

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (User)                       │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (localhost:8501)
┌───────────────────────▼─────────────────────────────────┐
│               Streamlit App (app.py)                    │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Login   │  │  Dashboard   │  │  Model Training  │  │
│  │  Page    │  │  Page        │  │  Page            │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
│                                                         │
│  ┌──────────────────────┐  ┌────────────────────────┐  │
│  │  Glucose Prediction  │  │  AI Consultation       │  │
│  │  Page                │  │  Hub (WIP)             │  │
│  └──────────────────────┘  └────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              db.py (Database Layer)              │   │
│  │  init_db | add_glucose_record | get_glucose_     │   │
│  │  records | save_training_file_to_db              │   │
│  └──────────────────────┬───────────────────────────┘   │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              glucoguard.db (SQLite)                     │
│   users | glucose_records | training_files              │
└─────────────────────────────────────────────────────────┘

Offline Training Pipeline (main.py):
  Excel Data → NOA Optimization → VMD Decomposition → BiLSTM → Results
```

**Data Flow for Glucose Prediction:**

1. User enters glucose value in the form → Streamlit captures input
2. `add_glucose_record(user_id, timestamp, glucose_value)` → written to SQLite
3. User clicks "Execute Prediction" → demo prediction values generated
4. `get_glucose_records()` → retrieves last 10 historical records from SQLite
5. Historical + current + predicted data merged → rendered as multi-source line chart

---

## 5. Database Design

GlucoGuard uses a local **SQLite** database (`glucoguard.db`) managed through `db.py`.

### Table: `users`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment user ID |
| username | TEXT (NOT NULL) | Login username |
| role | TEXT | User role (default: 'standard') |
| created_at | TEXT | Account creation timestamp |

### Table: `glucose_records`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment record ID |
| user_id | INTEGER (NOT NULL) | Foreign key to users table |
| timestamp | TEXT (NOT NULL) | Reading timestamp (YYYY-MM-DD HH:MM:SS) |
| glucose_value | REAL (NOT NULL) | Blood glucose in mmol/L |
| source | TEXT | Data source (default: 'manual') |
| notes | TEXT | Optional user notes |
| created_at | TEXT | DB insertion timestamp |

### Table: `training_files`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment file ID |
| file_name | TEXT (NOT NULL) | Uploaded Excel filename |
| file_size | INTEGER | File size in bytes |
| upload_time | TEXT (NOT NULL) | Upload timestamp |

### Database Operations (`db.py`)

| Function | Description |
|---|---|
| `init_db()` | Creates all tables if they do not exist. Includes migration logic to handle old column name variants. |
| `add_glucose_record(*args)` | Adaptive insert — accepts (timestamp, value) or (user_id, timestamp, value). |
| `get_glucose_records()` | Returns all glucose records ordered by timestamp ASC. |
| `save_training_file_to_db(name, size, df)` | Logs uploaded file metadata into `training_files`. |

---

## 6. Technology Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Navigation | streamlit-option-menu |
| Backend Language | Python 3.8+ |
| Database | SQLite (via Python built-in `sqlite3`) |
| Data Processing | pandas, numpy |
| Excel I/O | openpyxl (via pandas) |
| Signal Processing | vmdpy (VMD decomposition) |
| Deep Learning | Custom BiLSTM (via `src/fitness.py`) |
| Optimization | Custom NOA (via `src/optimization/noa.py`) |
| Visualization | Streamlit native charts |
| Version Control | Git / GitHub |

---

## 7. How to Run

### Prerequisites

- Python 3.8 or above
- pip

### Step 1 — Install Dependencies

```bash
pip install streamlit streamlit-option-menu pandas numpy openpyxl vmdpy
```

Or using the provided requirements file (once updated):

```bash
pip install -r requirements.txt
```

### Step 2 — Run the Application

Navigate to the project folder in your terminal and run:

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

### Step 3 — Log In

Use one of the test accounts:

| Username | Password | Role |
|---|---|---|
| admin | 123456 | Administrator |
| user | 123456 | Standard User |

### Step 4 — (Optional) Run the Training Pipeline

To run the offline VMD-NOA-BiLSTM training pipeline:

```bash
python main.py
```

Make sure the required source modules (`src/`) are present and Excel data files are configured in `main.py`.

---

## 8. User Guide

### Logging In

1. Open the app at `http://localhost:8501`
2. Enter username `admin` and password `123456`
3. Click the **Login** button
4. You will be redirected to the Dashboard

### Training a Model

1. Click **Model Training** in the left sidebar
2. Under **Data Input**, upload one or more `.xlsx` Excel files with glucose data
3. Under **Hyperparameter Configuration**, choose your algorithm and adjust epochs and split ratio
4. Click **Launch VMD-NOA-BiLSTM Training Pipeline**
5. Watch the 7-step progress bar complete
6. A success message confirms training is done

### Making a Prediction

1. Click **Glucose Prediction** in the left sidebar
2. In the left panel, review the current timestamp
3. Enter your current blood glucose value (mmol/L)
4. Click **Save Current Data & Trigger Prediction** — the value is saved to the database
5. In the right panel, click **Execute Forward Intelligent Prediction**
6. A table of predicted values for the next 15/30/45/60 minutes will appear
7. Below the table, a multi-source trend chart shows historical + current + predicted glucose

### Logging Out

Click **Log Out Safely** at the bottom of the sidebar.

---

## 9. Testing

### Manual Testing Performed

**Authentication:**
- Correct credentials → login succeeds, redirects to dashboard ✅
- Wrong password → error message shown ✅
- Logout → session cleared, returns to login ✅

**Model Training Page:**
- Upload valid `.xlsx` file → file parsed, saved to DB, success toast shown ✅
- Launch training without uploading file → error message shown ✅
- Progress bar completes all 7 steps ✅

**Glucose Prediction Page:**
- Submit glucose value → record written to `glucose_records` in SQLite ✅
- Click predict without entering data first → error message shown ✅
- Prediction table shows 4 future time points ✅
- Multi-source chart renders with historical, current, and predicted series ✅
- If no historical records in DB → fallback simulated data used gracefully ✅

**Database:**
- `init_db()` creates all tables on first run ✅
- `add_glucose_record()` accepts both 2-arg and 3-arg call signatures ✅
- `get_glucose_records()` returns records ordered by timestamp ✅
- `save_training_file_to_db()` logs file metadata correctly ✅
- Column migration logic handles old `glucose` column name ✅

### Known Passing Scenarios

| Scenario | Expected Result | Status |
|---|---|---|
| Login with admin/123456 | Dashboard shown | ✅ Pass |
| Login with wrong password | Error message | ✅ Pass |
| Upload Excel file on training page | File saved to DB | ✅ Pass |
| Enter glucose value and submit | Record in DB | ✅ Pass |
| Run prediction after data entry | Table + chart shown | ✅ Pass |
| Run prediction without data entry | Error message | ✅ Pass |

---

## 10. Known Limitations & Future Work

### Current Limitations

- User credentials are hardcoded in `app.py` (not read from the `users` database table)
- Passwords are stored and compared in plaintext (no hashing)
- The model training progress bar simulates steps — it does not invoke `main.py` directly; the full training must be run separately via `python main.py`
- The AI Consultation Hub page is a placeholder — the chat interface is not yet functional
- The trained model file (`models/latest_vmd_noa_bilstm.pkl`) is not included; prediction runs in demo mode by default
- User registration is not supported in the UI (accounts must be added manually in code)

### Planned for Milestone 3

1. **Full registration system** — users can create accounts stored in the `users` table with hashed passwords
2. **Live model training integration** — connect Model Training page to `main.py` subprocess or thread so training runs in real-time inside the app
3. **AI Consultation Hub** — integrate a large language model API for diabetes Q&A
4. **User-specific glucose history** — Glucose Prediction page filters records by logged-in user's `user_id`
5. **Alert system** — push notification or visual alert when predicted glucose crosses the configured hyperglycemia/hypoglycemia thresholds
6. **Report export** — generate a downloadable PDF/Excel health report from historical + prediction data
7. **Password hashing** — implement bcrypt or SHA-256 for secure credential storage

---

## 11. Team Contributions

### Xiao Hongyu (欣儿贝贝)

- Project coordination and milestone planning
- Designed and implemented the SQLite database layer (`db.py`): schema design, `init_db`, `add_glucose_record`, `get_glucose_records`, `save_training_file_to_db`, and column migration logic
- Integrated the SQLite database with the Streamlit UI (connected `db.py` calls throughout `app.py`)
- Implemented the Blood Glucose Prediction page (data entry form, DB write, prediction output, multi-source trend chart)
- Verified database insertion and retrieval
- Set up and managed the GitHub repository (`integrate-database` branch)
- Prepared and refined Milestone 2 documentation (this README, `project_log.md`)

### Li Yingzhuo (李影卓)

- Implemented the core algorithmic backend (`main.py`): VMD decomposition, NOA optimization, BiLSTM component-wise training, error evaluation (MAE, RMSE, MAPE, Clarke Error Grid)
- Developed the sliding-window data preprocessing that converts raw glucose data into the 15/30/50-minute training datasets
- Built the Model Training page workflow (file upload, hyperparameter configuration, training pipeline)
- Tuned model hyperparameters and validated prediction accuracy against test data
- Reviewed and updated the model code before Milestone 2 submission

---

## 12. Appendix: Milestone 1 Summary

Milestone 1 was submitted on 31 May 2026. It consisted of a basic Streamlit login prototype demonstrating:

- Username and password login with two simulated accounts (admin / user)
- Session management using `st.session_state`
- Role-based welcome message after login
- Logout functionality
- No database, no prediction model, no additional pages

The Milestone 1 prototype has been superseded by the full Milestone 2 application described above. All Milestone 1 functionality is preserved and extended in the current `app.py`.

### Milestone 1 Limitations (now addressed in M2)

| M1 Limitation | M2 Resolution |
|---|---|
| No database | SQLite with 3 tables implemented in `db.py` |
| No prediction functionality | Blood Glucose Prediction page with DB + chart |
| No model training | Model Training page with file upload + pipeline |
| Single login page only | Full 4-page navigation via sidebar |
| No data visualization | Multi-source trend line chart on Prediction page |

---

*GlucoGuard — Orbital 2026 | Team: Xiao Hongyu & Li Yingzhuo*
