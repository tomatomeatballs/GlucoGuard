# GlucoGuard — CGM Glucose Monitoring & AI Prediction System

> **Team: GlucoGuard** | **Target Achievement Level: Apollo**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Milestone 3 Progress Summary](#2-milestone-3-progress-summary)
3. [MS2 → MS3: What Actually Changed](#3-ms2--ms3-what-actually-changed)
4. [Features in Milestone 3](#4-features-in-milestone-3)
5. [System Architecture](#5-system-architecture)
6. [Database Design](#6-database-design)
7. [Technology Stack](#7-technology-stack)
8. [How to Run](#8-how-to-run)
9. [New User Guide — Full Walkthrough](#9-new-user-guide--full-walkthrough)
10. [Testing](#10-testing)
11. [Known Limitations & Future Work](#11-known-limitations--future-work)
12. [Team Contributions](#12-team-contributions)
13. [Appendix: Milestone 1 & 2 Summary](#13-appendix-milestone-1--2-summary)

---

## 1. Project Overview

**GlucoGuard** is a Continuous Glucose Monitoring (CGM) support system for diabetes patients and healthcare professionals. It does three things: tracks glucose in real time, predicts where your glucose is heading using a VMD-NOA-BiLSTM deep learning model, and gives you AI-powered explanations and lifestyle advice via an LLM chat interface — all in the browser, all stored in your own isolated database space.

### The Long-Term Vision

Our ultimate goal is to pair GlucoGuard with a dedicated CGM hardware device — a **split sensor-transmitter design** worn on the body that tracks glucose levels 24 hours a day in real time, with **needle-free, pain-free application**. The sensor would continuously stream glucose readings directly into the GlucoGuard system, eliminating the need for manual data uploads or Excel exports. A patient would put on the sensor once, open the GlucoGuard app, and immediately see their live glucose trace, AI-predicted trajectory for the next hour, and LLM-generated lifestyle recommendations — all refreshed automatically every few minutes. No finger pricks, no CGM manufacturer portals, no file management. Just real-time, personalized glucose intelligence.

This hardware integration is not yet implemented — we are currently at the software prototype stage. But every architectural decision in MS3 (per-user data isolation, BLOB-based file storage, subprocess-driven training, and the Train → Predict → Consult pipeline) was made with this future in mind. When the hardware is ready, the data ingestion path is already designed to accept a continuous stream of readings and feed them through the same VMD-NOA-BiLSTM engine.

### Who This Is For

- Diabetes patients who use CGM devices and want to see where their glucose is trending
- Healthcare professionals who want to train and compare prediction models on patient data
- Anyone who wants AI-assisted explanations of their glucose data, not just numbers on a screen

---

## 2. Milestone 3 Progress Summary

Milestone 3 is the full-stack completion of GlucoGuard. Everything that was simulated, placeholder, or hardcoded in MS2 is now real, connected, and per-user.

Here's what we delivered in MS3:

| What | Status |
|---|---|
| Real user registration + PBKDF2-hashed passwords | ✅ Done |
| DB-backed authentication (no more hardcoded dict) | ✅ Done |
| Live model training — subprocess actually runs VMD-NOA-BiLSTM | ✅ Done |
| Real glucose prediction via trained .pkl models (predictor.py) | ✅ Done |
| AI LLM Consultation Hub — multi-turn chat with NVIDIA API | ✅ Done |
| Per-user data isolation — every file, every result scoped to user_id | ✅ Done |
| Role-based Management page (admin sees all, user sees own) | ✅ Done |
| Automatic sliding-window training data generation | ✅ Done |
| Integrated performance analytics (plots + RMSE/MAE/MAPE) | ✅ Done |
| End-to-end Train → Predict → Consult flow, fully wired | ✅ Done |

**In short:** MS2 was a working prototype with simulated guts. MS3 is a working application with real guts.

---

## 3. MS2 → MS3: What Actually Changed

This section is for anyone who saw MS2 and wants to know exactly what's different now. If you're new to GlucoGuard, skip ahead to the [User Guide](#9-new-user-guide--full-walkthrough).

### 3.1 Authentication: From Hardcoded Dict to Real DB with Hashed Passwords

**MS2:** Two accounts (`admin`/`user`, both password `123456`) stored in a Python dictionary inside `app.py`. Passwords in plaintext. No registration.

**MS3:**
- Passwords hashed with **PBKDF2-HMAC-SHA256** (100,000 iterations) and a unique 16-byte salt per user
- `verify_user()` checks credentials against the `users` table, not a hardcoded dict
- Full **registration UI** — anyone can create an account with username + password (+ display name)
- Input validation: minimum 6-char password, confirm-password match, duplicate username check
- Built-in demo accounts still work but now live in the database, not in code
- `db.py` gained four new functions: `register_user()`, `verify_user()`, `_hash_password()`, `_ensure_demo_user()`

### 3.2 Model Training: From Simulated Progress Bar to Real Subprocess

**MS2:** The "Launch Training" button ran a fake 7-step progress bar using `st.progress()` and `time.sleep()`. It didn't touch `VMD_NOA_BILSTM.py` at all. Training had to be done separately in the terminal.

**MS3:**
- Hitting "Start Training & Prediction" **actually launches `VMD_NOA_BILSTM.py` as a subprocess**
- Real-time terminal output streams into the Streamlit UI — you watch the actual VMD decomposition, NOA optimization, and BiLSTM training logs scroll by
- Progress bar reacts to real keywords in the output ("VMD" → 20%, "NOA" → 40%, "Epoch" → 70%, "Prediction" → 90%)
- The subprocess reads training data from the database and writes results back to the database — **no shared local files, no collision between users**
- Training takes ~10–15 minutes for all three horizons on a typical laptop (NOA optimization is the bottleneck)

### 3.3 Glucose Prediction: From Demo Mode to Real Inference

**MS2:** The prediction page checked for a model file, didn't find one, and fell back to "Demo Prediction Mode" — it generated random-ish numbers and called it a prediction.

**MS3:**
- `predictor.py` implements a full `GlucosePredictor` class that loads the three trained `.pkl` model packages
- Takes a 2-column Excel upload → converts to 11-column sliding-window format via `excel_to_11col()` → runs **real VMD decomposition + BiLSTM inference** across all three horizons
- Outputs actual predicted glucose values at +15, +30, and +50 minutes
- Trend chart uses Plotly (not the simpler Streamlit native chart from MS2) with proper hover labels, historical + prediction traces, and time-axis formatting
- Prediction results auto-sync to the LLM Consultation page via `st.session_state`

### 3.4 AI Consultation: From Placeholder to Multi-Turn LLM Chat

**MS2:** A page with a title and "coming soon" message. Nothing functional.

**MS3:**
- Full chat interface powered by **NVIDIA NIM API** (LLaMA 3.1 8B Instruct) via `src/llm_chat.py`
- **Two chat modes:**
  - `ask_llm()` — one-shot structured analysis (used for the initial glucose trajectory report)
  - `ask_llm_chat()` — multi-turn conversation with full history (follow-up questions stay contextual)
- **Lifestyle context inputs:** Insulin (injected? dosage? when?), Food (what? carbs? when?), Exercise (type? duration? intensity?), plus free-text notes
- **Safety-tuned system prompt** with hard rules: hypoglycemia threshold 3.9 mmol/L triggers immediate alert, exercise never recommended below 5.0 mmol/L, hyperglycemia management with appropriate cautions
- The LLM receives: prediction dashboard (current + 15/30/50min predicted values), historical data, trend summary, and all lifestyle inputs — then generates a structured 4-part analysis (trajectory, lifestyle impact, recommendations, risk alerts)
- Follow-up questions via `st.chat_input` — the model remembers the full conversation, so "what about exercise?" gets a contextual answer, not a full re-analysis

### 3.5 Data Isolation: From Shared Local Files to Per-User Database Storage

**MS2:** Uploaded files went to a shared `data/` folder. Results went to a shared `results/` folder. If two users trained models, they'd overwrite each other's files. Glucose records in the DB had a `user_id` column but it was mostly ignored (hardcoded to 1).

**MS3:**
- New **`user_files` table** in SQLite — stores everything as BLOBs with `user_id`, `file_type`, `file_name`, `created_at`
- File types: `raw_upload`, `15min_data`, `30min_data`, `50min_data`, `prediction_15min`, `prediction_30min`, `prediction_50min`, `metrics_15min`, `metrics_30min`, `metrics_50min`
- Every upload, every generated training file, every prediction result, every metrics CSV — all scoped to the user who created them
- `VMD_NOA_BILSTM.py` reads training data from and writes results to the database via `get_latest_user_file_content()` and `save_user_file()` — zero dependency on local disk paths
- `get_latest_user_file_content(user_id, file_type)` with `ORDER BY id DESC LIMIT 1` — always grabs the newest file for that user, no timestamp ambiguity
- The Management page shows each user only their own files; admins see everything

### 3.6 Management Page: New in MS3

**MS2:** Didn't exist.

**MS3:**
- Role-based view: **Admins** see all registered users + all uploaded/generated files across every account; **standard users** see only their own profile and files
- File list shows file type, name, and creation timestamp — you can trace exactly what each user has uploaded and generated

### 3.7 Database: Schema Evolution

**MS2 tables:** `users` (barebones), `glucose_records`, `training_files`

**MS3 additions:**
- `users` table: added `password_hash`, `salt`, `name` columns (with auto-migration for old DBs)
- New `user_files` table: `id`, `user_id` (FK), `file_type`, `file_name`, `file_content` (BLOB), `created_at`
- `db.py` grew from ~120 lines to ~280 lines — added `register_user()`, `verify_user()`, `_hash_password()`, `_ensure_demo_user()`, `save_user_file()`, `get_user_files()`, `get_all_user_files()`, `get_user_file_content()`, `get_latest_user_file_content()`

### 3.8 Prediction Engine: From Script to Importable Module

**MS2:** `VMD_NOA_BILSTM.py` was a standalone script you ran once. It used `glob` to find files, hardcoded `zim=1` for all horizons, output everything to local disk.

**MS3:**
- `VMD_NOA_BILSTM.py`  takes `--user-id` argument, reads/writes database, supports different `zim` values per horizon (3/6/10 for 15/30/50min)
- `predictor.py` is new — importable class that loads trained model packages and runs inference on-demand from the Streamlit UI
- Model packages (`.pkl` files) store: best_params, vmd_params, look_back, and all IMF model artifacts (state_dict, scalers) — everything needed for inference without retraining

### 3.9 Summary Table

| Area | Milestone 2 | Milestone 3 |
|---|---|---|
| **Login** | Hardcoded dict, plaintext passwords | DB-backed, PBKDF2-SHA256 hashed, per-user salt |
| **Registration** | None | Full UI with validation + DB insert |
| **Model Training** | Fake progress bar (time.sleep) | Real subprocess, live terminal output |
| **Prediction** | Demo mode (random-ish numbers) | Real VMD-NOA-BiLSTM inference via predictor.py |
| **AI Chat** | Placeholder page | Multi-turn LLM (LLaMA 3.1 8B), lifestyle context, safety rules |
| **Data Storage** | Shared local folders (data/, results/) | Per-user BLOBs in user_files table |
| **Management** | No such page | Role-based: admin sees all, user sees own |
| **Training Data** | Manual Excel upload only | Auto sliding-window generation (2-col → 11-col) |
| **Analytics** | None | Prediction vs. ground truth plots + RMSE/MAE/MAPE per horizon |
| **Model Load** | Not loadable from UI | GlucosePredictor class, cached via @st.cache_resource |
| **Architecture** | 4 pages, simulated pipeline | 5 pages, real pipeline end-to-end |
| **Database tables** | 3 (users, glucose_records, training_files) | 4 (+ user_files), with password/salt columns |

---

## 4. Features in Milestone 3

### Feature 1: Secure Authentication & Registration

Everything from MS2, plus:

- **Registration tab** on the login page — enter display name, username, password (min 6 chars, must match confirmation)
- Passwords stored as `PBKDF2-HMAC-SHA256(salt + password, 100000 iterations)` — even if the DB file leaks, passwords aren't recoverable
- Salt is `secrets.token_hex(16)` — unique per user
- Duplicate username check, empty-field validation
- Two demo accounts pre-seeded in the DB: `admin`/`123456` (Administrator) and `user`/`123456` (Standard User)

### Feature 2: Live Model Training

The Model Training page now runs the real algorithm:

1. **Upload** a 2-column Excel file (glucose + timestamp, 5-minute intervals)
2. **Generate training files** — the system converts your raw data into three 11-column sliding-window datasets (one per prediction horizon: 15min / 30min / 50min) and saves them to the database under your account
3. **Launch training** — clicks spawn `VMD_NOA_BILSTM.py` as a subprocess with your `user_id`; the algorithm reads your training data from the DB, runs through NOA optimization → VMD decomposition → component-wise BiLSTM → error evaluation, and writes all results back to the DB
4. **Watch it run** — real-time terminal output streams into the UI; progress bar updates as VMD/NOA/LSTM phases complete
5. **Review results** — after training, three horizon panels show prediction-vs-ground-truth plots and RMSE/MAE/MAPE metric cards, all pulled from your own rows in the database
<img width="1512" height="982" alt="6af8af4fc6ac30d95f2a676637adc89b" src="https://github.com/user-attachments/assets/c8814081-3c50-4ef6-8fd0-11c2cfb2fed5" />

### Feature 3: Real Glucose Prediction

The Glucose Prediction page now does real inference:

- Upload a 2-column Excel with your recent glucose history
- The system auto-builds 10-step sliding windows from your data
- Click "Execute VMD-NOA-BiLSTM Prediction" — it loads the three trained model packages (cached), runs VMD decomposition on your data, does BiLSTM inference per IMF component, and sums the results
  <img width="919" height="173" alt="469062106740680012641fff391a9693" src="https://github.com/user-attachments/assets/f0b3a8d6-3dff-4e80-b8b9-6d1591e86589" />

- Output: three metric cards showing predicted glucose at +15, +30, +50 minutes, plus a Plotly chart overlaying your full history and the AI prediction trajectory
- Results are synced to session state so the LLM Consultation page can pick them up
<img width="1512" height="982" alt="1dca46fe3718990ba8ca22b873fb7446" src="https://github.com/user-attachments/assets/ef5d615f-be53-4aa3-934c-e1db4eb8ced3" />


### Feature 4: AI LLM Consultation Hub
<img width="1512" height="982" alt="89d7d10a4a586e535a3157f7c5fac8b5" src="https://github.com/user-attachments/assets/14d01be5-83f4-4489-b17c-c84862774c28" />

A full chat experience:

- **Prediction dashboard** at the top shows your current glucose + all three future predictions + trend summary (auto-populated from the Glucose Prediction page)
- **Lifestyle inputs** — three columns for insulin, food, and exercise context, plus free-text notes. Radio buttons show/hide follow-up fields (e.g. selecting "Yes" for insulin reveals dosage and timing inputs)
- **Initial analysis** — clicking "Analyze & Get LLM Recommendations" sends a structured prompt to the LLM with your full prediction dashboard + all lifestyle context. The model returns a 4-part analysis: trajectory explanation, lifestyle impact, personalized recommendations, risk alerts
- **Follow-up chat** — a chat input widget at the bottom lets you ask additional questions. The model sees the full conversation history, so "should I eat something?" gets a contextual answer based on the predictions you already shared
- **Medical safety guardrails** — the system prompt hardcodes hypoglycemia alert thresholds, forbids exercise recommendations when glucose is low, and mandates a disclaimer on every response
<img width="1512" height="982" alt="0f00d9fa065986ecc9c9819898335d05" src="https://github.com/user-attachments/assets/22cd1a83-9ed5-45ba-958f-547b86d21d2a" />

### Feature 5: Management Console

New page for user and file oversight:

- **Admin view:** table of all registered users (username, name, role, registration date) + table of all files from all users (who uploaded what, what type, when)
- <img width="1512" height="982" alt="b417e5fc3669f6be2a6a021cb5e099e5" src="https://github.com/user-attachments/assets/a373d5c8-07a7-4d4d-91fb-e2ad0fcc5ca2" />

- **Standard user view:** own profile info + own file list
- File types are descriptive: `raw_upload` = original Excel, `15min_data` = generated sliding-window training file, `prediction_15min` = prediction results, `metrics_15min` = RMSE/MAE/MAPE CSV
<img width="1512" height="982" alt="b52b33f3325bb81a4b9d44f80039c6d2" src="https://github.com/user-attachments/assets/432cf936-ef22-4af5-9def-accb930a26e4" />


### Feature 6: VMD-NOA-BiLSTM Algorithmic Backend (Enhanced)

The algorithm itself was in MS2, but MS3 made it production-ready:

- **Per-horizon `zim` values** — 15min prediction looks 3 steps ahead, 30min looks 6, 50min looks 10 (MS2 hardcoded `zim=1` for all)
- **Database-driven I/O** — the subprocess reads training files from and writes results to `user_files` via `get_latest_user_file_content()` and `save_user_file()`; no local file paths anywhere in the training path
- **Model artifact packaging** — after training, each horizon's model is pickled as a package containing best_params, vmd_params, look_back, and all IMF model state_dicts + scalers — everything `predictor.py` needs to reconstruct and run inference
- **Safe VMD wrapper** — `_safe_vmd()` catches division-by-zero on short/noisy signals and retries with tiny noise injection, instead of crashing
- **Signal validation** — checks for constant signals (std < 1e-8), too-short sequences, and NaN values before feeding into VMD

---

## 5. System Architecture

GlucoGuard is a Streamlit web application backed by a SQLite database, with two external touchpoints: a training subprocess and an LLM API. Everything runs locally except the LLM calls.

### The Stack, Layer by Layer

**Frontend — Streamlit (app.py, ~980 lines)**

The entire UI is one Python file. Streamlit handles rendering, state management, and page routing. We use `streamlit-option-menu` for the sidebar navigation bar. The app is split into six function-based pages: `login_page()`, `dashboard_page()`, `management_page()`, `model_training_page()`, `blood_sugar_prediction_page()`, and `ai_consultation_page()`. A `main()` router at the bottom picks which page to render based on sidebar selection.

Login state is held in `st.session_state` — six keys track whether the user is logged in, their username, user_id, display name, role, and any active prediction context. When you switch pages, the state persists because Streamlit reruns the script but keeps `st.session_state` intact per browser session.

**Database Layer — db.py (~280 lines)**

All persistence goes through `db.py`. It's a flat module with a single SQLite file (`glucoguard.db`) and twelve exported functions. The module does three categories of work:

- **Auth**: `register_user()` inserts a new row with PBKDF2-hashed password and random salt. `verify_user()` looks up the username, re-hashes the supplied password with the stored salt, and compares. `get_all_users()` is for the admin Management view.
- **Records**: `add_glucose_record()` and `get_glucose_records()` handle the glucose tracking log. These are the oldest functions in the codebase, dating back to MS2, and have adaptive signatures to handle both 2-arg and 3-arg call patterns.
- **Files**: `save_user_file()` stores any file as a BLOB keyed to user_id + file_type. `get_user_files()` returns metadata only (no BLOB payload). `get_latest_user_file_content()` fetches the newest file of a given type for a user — this is the function the training subprocess and analytics display both rely on. `get_all_user_files()` joins against the users table for the admin view.

**Prediction Engine — predictor.py (~220 lines)**

The `GlucosePredictor` class loads the three trained model packages from `models/` and exposes `predict_all_horizons()`. Internally, for each horizon, it runs VMD decomposition on the user's data, feeds each of the 5 IMF components through a BiLSTM model, inverse-transforms the outputs, and sums them. The class is wrapped with `@st.cache_resource` in the app so models load once and stay in memory across reruns. The `excel_to_11col()` static method handles the sliding-window conversion from 2-column raw data to the 11-column format the models expect.

**Training Pipeline — VMD_NOA_BILSTM.py (~260 lines)**

This is a standalone script, not imported. The Model Training page launches it via `subprocess.Popen` with a `--user-id` argument. The script reads that user's three training files from the database (`get_latest_user_file_content()`), runs the full pipeline for each horizon, writes six result files back to the database (`save_user_file()`), and pickles three model packages to `models/` on disk. Real-time terminal output from the subprocess is captured line by line and streamed into the Streamlit UI.

**LLM Module — src/llm_chat.py (~140 lines)**

A thin wrapper around the OpenAI SDK pointed at NVIDIA's NIM endpoint. Two public functions: `ask_llm()` for one-shot structured prompts and `ask_llm_chat()` for multi-turn conversations with full message history. Both funnel through a shared `_call_chat_api()` that handles authentication errors, rate limits, connection failures, and malformed responses with user-friendly messages. The API key is loaded from a `.env` file via `python-dotenv`.

**Algorithm Libraries — src/**

- `src/models/lstm.py` — the BiLSTM model class in PyTorch: one bidirectional LSTM layer + one fully connected output layer
- `src/optimization/noa.py` — Nutcracker Optimization Algorithm: swarm-based search with foraging/caching phases, Lévy flight exploration, boundary handling
- `src/fitness.py` — the fitness function called by NOA during optimization: builds sliding-window datasets, trains a BiLSTM, returns RMSE on the test split
- `src/utils/metrics.py` — MAE, RMSE, MAPE calculations and Clarke Error Grid analysis

### How Data Moves Through the System

A user's data takes a five-stage journey from upload to AI recommendation:

**Stage 1 — Upload.** The user drops a 2-column Excel file (glucose value + timestamp) on the Model Training page. The file is validated (numeric glucose column, parseable timestamps, no missing values), then its bytes and metadata are saved to two places: `training_files` for the upload log, and `user_files` (type=`raw_upload`) as a BLOB keyed to the user's ID.

**Stage 2 — Generate.** When the user clicks "Generate Training Dataset", `generate_training_files()` in app.py converts the 2-column raw data into three 11-column sliding-window files. For the 15-minute horizon, each window looks 10 steps back and 3 steps ahead; for 30-minute, 6 steps ahead; for 50-minute, 10 steps ahead. The three resulting Excel files are saved to `user_files` with types `15min_data`, `30min_data`, `50min_data`.

**Stage 3 — Train.** Clicking "Start Training & Prediction" spawns `VMD_NOA_BILSTM.py --user-id <id>` as a subprocess. The script pulls the three training files from `user_files`, then for each horizon: runs NOA optimization to find the best BiLSTM hyperparameters, decomposes the glucose signal with VMD into 5 frequency components, trains one BiLSTM per component, sums the component predictions, evaluates against the held-out test set, and saves results. Six files go back to `user_files` (`prediction_15min/30min/50min` and `metrics_15min/30min/50min`). Three model packages go to `models/` on disk. All of this happens with the user watching real-time logs in the browser.

**Stage 4 — Predict.** On the Glucose Prediction page, the user uploads a history Excel. `excel_to_11col()` converts it to sliding windows. `GlucosePredictor` loads the three `.pkl` model packages (cached), runs VMD + BiLSTM inference, and returns three predicted glucose values. These are displayed as metric cards and a Plotly chart. The full prediction context — raw values, timestamps, predictions, trend summary — is saved to `st.session_state.prediction_context` so the Consultation page can pick it up.

**Stage 5 — Consult.** The LLM Consultation page reads `prediction_context` and renders a dashboard. The user fills in lifestyle inputs (insulin, food, exercise, notes). On clicking "Analyze", a structured prompt containing the full prediction data and all lifestyle context is sent to the NVIDIA NIM API. The LLM returns a 4-part analysis. The user can ask follow-up questions — the full conversation history is preserved in `st.session_state.ai_chat_messages` and sent with each subsequent request, so the model stays in context.

---

## 6. Database Design

GlucoGuard uses SQLite (`glucoguard.db`), managed through `db.py`.

### Table: `users`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment |
| username | TEXT (UNIQUE, NOT NULL) | Login username |
| password_hash | TEXT | PBKDF2-SHA256 hash (NEW in MS3) |
| salt | TEXT | 16-byte hex salt, unique per user (NEW in MS3) |
| name | TEXT | Display name (NEW in MS3) |
| role | TEXT | 'Administrator' or 'Standard User' |
| created_at | TEXT | Account creation timestamp |

### Table: `glucose_records`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment |
| glucose_value | REAL | Blood glucose in mmol/L |
| timestamp | TEXT (NOT NULL) | Reading timestamp |
| user_id | INTEGER | FK to users.id |

### Table: `training_files`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment |
| file_name | TEXT (NOT NULL) | Uploaded filename |
| file_size | INTEGER | Size in bytes |
| upload_time | TEXT | Upload timestamp |

### Table: `user_files` (NEW in MS3)

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment |
| user_id | INTEGER (NOT NULL) | FK to users.id — who owns this file |
| file_type | TEXT (NOT NULL) | Category: raw_upload, 15min_data, 30min_data, 50min_data, prediction_15min, prediction_30min, prediction_50min, metrics_15min, metrics_30min, metrics_50min |
| file_name | TEXT (NOT NULL) | Original filename |
| file_content | BLOB (NOT NULL) | Raw bytes of the file |
| created_at | TEXT | Insertion timestamp |

This table is the backbone of per-user data isolation. Every file — from the original Excel upload through to the final prediction results — lives here, keyed to a specific user. The training subprocess (`VMD_NOA_BILSTM.py`) and the web UI (`app.py`) both read from and write to this table, never touching shared local folders.

### Key DB Functions (added in MS3)

| Function | What it does |
|---|---|
| `register_user(username, password, name, role)` | Creates account with hashed password + salt |
| `verify_user(username, password)` | Checks credentials, returns user dict or None |
| `_hash_password(password, salt)` | PBKDF2-HMAC-SHA256, 100k iterations |
| `_ensure_demo_user(username, password, name, role)` | Seeds or backfills demo accounts |
| `get_all_users()` | Admin: lists all registered users |
| `save_user_file(user_id, file_type, file_name, content)` | Stores file BLOB in user_files |
| `get_user_files(user_id, file_type?)` | Lists a user's files (metadata only, no BLOB) |
| `get_all_user_files()` | Admin: lists every user's files |
| `get_user_file_content(file_id)` | Downloads one file's BLOB by ID |
| `get_latest_user_file_content(user_id, file_type)` | Gets the newest file of a given type for a user — used by the training subprocess |

---

## 7. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend / UI | Streamlit | Multi-page with sidebar navigation |
| Navigation | streamlit-option-menu | Tab-style sidebar |
| Charts | Plotly + Matplotlib | Plotly for interactive prediction charts, Matplotlib for training analytics |
| Backend Language | Python 3.8+ | |
| Database | SQLite | Via Python built-in `sqlite3` |
| Password Hashing | hashlib.pbkdf2_hmac | SHA-256, 100k iterations |
| Salt Generation | secrets.token_hex(16) | Cryptographically random |
| Data Processing | pandas, numpy | |
| Excel I/O | openpyxl (via pandas) | |
| Signal Processing | vmdpy | Variational Mode Decomposition |
| Deep Learning | PyTorch | Custom BiLSTM (src/models/lstm.py) |
| Optimization | Custom NOA | Nutcracker Optimization Algorithm (src/optimization/noa.py) |
| LLM API | OpenAI SDK → NVIDIA NIM | Model: meta/llama-3.1-8b-instruct |
| LLM Config | python-dotenv | API key from .env file |
| Subprocess | subprocess.Popen | Real-time training pipeline execution |
| Model Serialization | pickle | .pkl model packages for inference |

---

## 8. How to Run

### Prerequisites

- Python 3.8 or above
- pip
- An NVIDIA API key (free tier works) for the LLM Consultation feature — get one at [build.nvidia.com](https://build.nvidia.com)

## Step 1 — Prepare Your Data

Before running the app, make sure your glucose data is in the `data/` folder. The folder is organized by user:

```
data/
├── user1/
│   ├── user_train_dataset.xlsx    ← upload this for model training
│   └── user1_Predict_data.xlsx    ← upload this for glucose prediction
├── user2/
│   ├── user_train_dataset.xlsx
│   └── user2_Predict_data.xlsx
└── ...
```

Each user folder has two files: one for training your personalized model, one for running predictions against it. We've included sample data for `user1` so you can try the full workflow immediately.

**If you have your own CGM data:** export a 2-column Excel file from Dexcom Clarity or Freestyle Libre — Column 1 = glucose value (mmol/L), Column 2 = timestamp. Create a new folder under `data/` (e.g. `data/yourname/`) and drop your files there.

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

Full dependency list: `streamlit`, `streamlit-option-menu`, `pandas`, `numpy`, `matplotlib`, `plotly`, `openpyxl`, `vmdpy`, `torch`, `scikit-learn`, `openai`, `python-dotenv`

### Step 3 — Set Up the API Key

Create a `.env` file in the project root:

```
API_KEY=nvapi-your-key-here
```

If you skip this step, the LLM Consultation page will show a warning but everything else will work.

### Step 4 — Run the App

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### Step 5 — Log In
<img width="1512" height="982" alt="d39dc624e9c39fe0ee2ba79840fa15dc" src="https://github.com/user-attachments/assets/d13d7c6c-47bf-4c27-a89a-2c46c176c7a4" />

| Username | Password | Role |
|---|---|---|
| admin | 123456 | Administrator (sees all users + files) |
| user | 123456 | Standard User |

Or click the **Register** tab to create your own account.

---

## 9. New User Guide — Full Walkthrough

This guide walks you through the entire GlucoGuard workflow, from creating an account to getting AI-powered glucose insights. Follow it step by step.

### 9.1 First Launch: Create Your Account

When you open the app, you'll see the login page. If this is your first time, click the **📝 Register** tab.
<img width="923" height="554" alt="a43552613e5867ab578189c486e2025a" src="https://github.com/user-attachments/assets/3b514339-7b33-4b6b-9e4b-aeea1fcb1204" />

1. Enter your **Display Name** (e.g. "Jane Tan")
2. Choose a **Username** (e.g. "janetan")
3. Choose a **Password** (at least 6 characters)
4. Re-enter the password to confirm
5. Click **📝 Create Account**

You'll see a success message. Switch back to the **🔐 Login** tab and sign in with your new credentials.


After login, you land on the Dashboard — a welcome page showing your name, role, and a summary of available features.

> **Tip:** The sidebar on the left is your navigation hub. It stays visible on every page and shows your username + a green "Online" indicator. The **Log Out Safely** button is at the bottom.

### 9.2 Check the Management Page

Click **Management** in the sidebar. As a standard user, you'll see your profile info and an empty file list — that's normal, you haven't uploaded anything yet.

If you logged in as `admin`, you'll see all registered users and all files across every account. This is where an administrator monitors system usage.

### 9.3 Train Your Prediction Model

This is the core workflow. You need an Excel file with at least 20 rows of glucose data at 5-minute intervals — two columns: glucose value (mmol/L) and timestamp.

The repo includes sample data if you don't have your own: `glucose_record_patient1.xlsx` and `glucose_record_patient3.xlsx`.

**Step 3a — Upload Data**

1. Click **Model Training** in the sidebar
2. Under "1. Data Input", drag your Excel file into the upload area (or click to browse)
3. You'll see a green success message and a toast notification: "Data file successfully saved to DB!"
4. The system validates your file: numeric glucose column, parseable timestamps, no missing values. If something's wrong, you'll get a specific error telling you what to fix.

**Step 3b — Generate Training Files**
<img width="1512" height="982" alt="cefc082b1d9e24570eadf2a7d0e61ce7" src="https://github.com/user-attachments/assets/fa91b143-8522-4b7e-a28b-bd45d496a4bf" />

1. Scroll to "2. Generate Training Files"
2. You'll see a summary of your uploaded file (row count, column count)
3. Click **Generate Training Dataset**
4. Three metric cards appear showing how many sliding windows were created for each horizon (15min, 30min, 50min). A typical 100-row upload yields about 90 windows for 15min, 84 for 30min, and 80 for 50min — the longer the prediction horizon, the fewer windows, because each window needs more future data.
5. These generated files are saved to the database under your account. You can verify them on the Management page.

**Step 3c — Launch Training**

1. Scroll to "3. Model Training"
2. You should see a blue info box: "Training data ready in the database for your account"
3. Click **Start Training & Prediction**
4. The real work begins — you'll see:
   - A progress bar advancing through 4 stages (Signal Decomposition → Parameter Optimization → Neural Network Training → Result Generation)
   - A live terminal output panel showing the actual VMD-NOA-BiLSTM logs scrolling by
   - Status messages like "Executing: Nutcracker Optimization Algorithm (NOA)..."
5. **This takes 10–15 minutes** on a typical laptop. The NOA optimization is the slowest part — it's searching a 3D parameter space with 10 agents over 20 iterations, evaluating a full BiLSTM train-and-test cycle each time. Go get a coffee.
6. When it finishes, you'll see "Model training pipeline completed successfully!" and an expandable section with the full execution logs.

**Step 3d — Review Performance Analytics**

After training, scroll to "4. Integrated Performance Analytics". You'll see three sections — one per horizon — each containing:

- A **prediction tracking plot**: blue line = ground truth, red dashed line = model forecast, overlaid on the test set (up to 150 points). This lets you visually check how well the model tracks the actual glucose curve.
- Three **metric cards**: RMSE, MAE, and MAPE. Lower is better. MAPE below 10% is excellent; below 20% is usable. These metrics are calculated on the 40% held-out test data, so they reflect real generalization performance, not training set memorization.

If any horizon is missing, the section will show "Horizon profile pending" — that means that horizon's training file wasn't found in your account. Go back to Step 3b and make sure all three were generated.

> **What's actually happening during training:**
>
> For each horizon (15min, 30min, 50min):
> 1. **NOA** searches for the best BiLSTM hyperparameters (hidden units, epochs, learning rate) by evaluating different configurations on the full dataset
> 2. **VMD** decomposes the glucose signal into 5 frequency components (IMFs) — low-frequency trend, mid-frequency fluctuations, high-frequency noise
> 3. **BiLSTM** trains one neural network per IMF component — each network learns to predict that component's future value from the sliding-window history
> 4. **Reconstruction** — the 5 component predictions are summed to produce the final glucose prediction
> 5. **Error evaluation** — the summed prediction is compared against held-out test data to compute RMSE, MAE, MAPE
>
> The trained model is saved to `models/vmd_noa_bilstm_{horizon}.pkl`. This is a shared global file (not per-user in the DB) — it represents the model trained on your data, and whoever trains most recently updates it. Results (predictions + metrics) are stored per-user in the database.

### 9.4 Make a Glucose Prediction

Now that you have trained models, you can predict future glucose from any history file.
<img width="1512" height="982" alt="57cb9d912e760807e63efd2801bb757b" src="https://github.com/user-attachments/assets/14798546-1825-4560-a098-fa87bcc25aa6" />

1. Click **Glucose Prediction** in the sidebar
2. You should see a green banner: "VMD-NOA-BiLSTM Core Engine Status: Ready"
3. Upload a 2-column Excel file with your glucose history (it can be the same file you used for training, or a different one — the predictor uses the trained models, not the training data)
4. Expand "Data Preview" to verify the file loaded correctly
5. You'll see a caption showing how many sliding windows were constructed (e.g. "Sliding window constructed: 91 windows from 100 readings")
   <img width="1512" height="982" alt="9d9e01116e3d119a35ec031d3af361ba" src="https://github.com/user-attachments/assets/00158067-8551-449a-b911-cf934590eaa6" />

7. Click **🚀 Execute VMD-NOA-BiLSTM Prediction**
8. After a few seconds: three metric cards appear showing predicted glucose at +15, +30, and +50 minutes, with delta indicators (e.g. "+0.3" means glucose is predicted to rise 0.3 mmol/L)
9. Below the cards: an interactive Plotly chart showing your full historical glucose trace (faded blue) with the AI prediction trajectory overlaid (bold red, last 4 points). Hover over points for exact values and timestamps.
10. A green success message confirms: "Prediction synced to LLM Consultation"

### 9.5 Get AI-Powered Insights

This is where everything comes together.

1. Click **LLM Consultation** in the sidebar
2. At the top, you'll see your **Prediction Dashboard** — four metric cards (Current, +15 min, +30 min, +50 min) with delta indicators, plus a trend summary (e.g. "Glucose is rising in the normal range")
3. If the dashboard says "No prediction data loaded", go back to step 9.4 — you need to run a prediction first

**Fill in your lifestyle context:**
<img width="910" height="537" alt="d074ab85d4aca8217caf11723a116787" src="https://github.com/user-attachments/assets/a022bc0a-ffde-4eef-848a-3bc9c9a76749" />

4. **Insulin column:** Select "Yes" if you've injected recently, then enter dosage and timing
5. **Food column:** Select "Yes" if you've eaten, then describe what, estimate carbs (Low/Medium/High), and when
6. **Exercise column:** Select "Yes" if you've exercised, then pick type, duration, timing, and intensity
7. **Additional notes:** Anything else relevant — stress, medication, symptoms
8. Click **Analyze & Get LLM Recommendations**

The LLM will return a structured analysis:

- **Glucose Trajectory Analysis** — explains your current trend and what the predictions suggest
- **Lifestyle Impact & Micro-Adjustment** — how your insulin/food/exercise inputs are likely to shift the predicted values
- **Personalized Recommendations** — 3–5 specific, actionable tips for the next hour
- **Risk Alerts** — flags hypoglycemia risk (predicted below 3.9 mmol/L) or hyperglycemia concern (above 13.9 mmol/L)

**Follow-up questions:** Use the chat input at the bottom. Ask things like:
- "Is it safe for me to go for a walk right now?"
- "Should I eat a snack before bed?"
- "What would happen if I took 2 more units of insulin?"

The model remembers the full conversation, so follow-ups are short and contextual — you don't need to re-explain your situation.

> **Medical disclaimer:** The LLM provides educational guidance, not medical advice. It will never tell you to change your prescribed insulin regimen, and it's programmed with safety guardrails: it will flag dangerous situations, refuse to recommend exercise when glucose is low, and always include a disclaimer.

### 9.6 Quick Reference: Page-by-Page Summary

| Page | What you do there | When to use it |
|---|---|---|
| **Dashboard** | Welcome screen, logout | First thing you see after login |
| **Management** | View your profile + files; admins see everyone | Check what data you've uploaded/generated |
| **Model Training** | Upload raw data → generate training files → train the model → review performance | Once, when setting up the system, or when you want to retrain on new data |
| **Glucose Prediction** | Upload recent history → get AI prediction for next 50 minutes | Every time you want to check where your glucose is heading |
| **LLM Consultation** | Review predictions, add lifestyle context, get AI analysis + ask follow-ups | After each prediction, for personalized insights |

---

## 10. Testing

We did three kinds of testing for MS3: our own systematic functional testing, scenario-based user testing with people outside the development team, and edge-case stress testing. The goal was to catch bugs before submission and to see how real first-time users would experience the app without guidance.

### 10.1 Our Functional Testing

This is the checklist we ran ourselves, methodically, for every feature. Each test was run at least twice — once as admin, once as a standard user — to catch permission leaks.

**Authentication & Registration**

- Register a new account with valid data → account created in `users` table, can log in immediately
- Register with an existing username → "This username is already taken" error, no duplicate row created
- Register with mismatched password + confirm password → "Passwords do not match" error, form keeps filled fields
- Register with password shorter than 6 characters → validation error, specific message shown
- Register with empty username or password → "Username and password cannot be empty"
- Login with correct credentials → `st.session_state` populated with user_id, username, display_name, role
- Login with wrong password → "Invalid username or password", no hint about which field is wrong (security)
- Login with non-existent username → same generic error message as wrong password
- Logout from sidebar → all six session state keys cleared, redirect to login page
- Logout from Dashboard button → same behavior as sidebar logout
- Password stored as PBKDF2 hash in DB, not plaintext → opened `glucoguard.db` in sqlite3 CLI, confirmed `password_hash` column is 128-char hex, `salt` is 32-char hex, no plaintext password anywhere
- Registration inserts unique salt per user → registered two users with same password "123456", verified different `password_hash` values due to different salts

**Model Training Page**

- Upload valid 2-column Excel (glucose_record_patient1.xlsx, 1000+ rows) → file saved to both `training_files` and `user_files` (type=raw_upload), success toast shown
- Upload Excel with non-numeric values in glucose column (we hand-edited a file to put "N/A" in row 50) → "column 1 (glucose) must be numeric" error, file rejected
- Upload Excel with unparseable timestamps (we put random strings in column 2) → "column 2 (timestamp) could not be parsed" error
- Upload Excel with only 1 column → "at least 2 columns required" error
- Upload the same file twice → both uploads succeed, two separate rows in `user_files` (no overwrite — history preserved by design)
- Generate training files from 100-row upload → three horizon files created in `user_files`, metric cards show correct window counts (91 for 15min, 84 for 30min, 80 for 50min)
- Generate training files from only 15 rows → "Need at least 20 glucose readings" error with clear minimum requirement
- Launch training with training files present → subprocess spawns, real-time terminal output visible in UI, progress bar advances through 4 stages, takes ~12 minutes on MacBook Air M2
- Launch training without generating training files first → "No training files saved for your account" error, tells user to complete Step 2
- Training completes successfully (return code 0) → six result files in `user_files` (prediction_* + metrics_* for each horizon), three `.pkl` files in `models/`
- Training subprocess crashes mid-run (we simulated by deleting a training file between generate and launch) → error output shown in UI, return code checked, "Pipeline exited with an error" message
- Performance analytics render after training → prediction-vs-ground-truth Matplotlib plots visible for all three horizons, RMSE/MAE/MAPE metric cards populated with non-zero values
- Performance analytics with no results in DB → "Horizon profile pending" message instead of crash

**Glucose Prediction Page**

- Upload Excel with 100+ rows, all models present → sliding windows constructed, prediction returns three values, Plotly chart renders with two traces (historical + prediction)
- Upload Excel with only 8 rows → "Need at least 10 glucose readings" error before prediction button even appears
- Run prediction with no models in `models/` → "Trained model files not found" warning at top of page, prediction button either hidden or shows clear error
- Prediction output values are reasonable → for the sample patient data (glucose ~5-8 mmol/L range), predictions stayed within 4-12 mmol/L (no wild 0.0 or 999.0 values)
- Plotly chart interactivity → hover shows exact glucose value + timestamp, zoom works, legend toggles traces on/off
- Switch to LLM Consultation page after prediction → `prediction_context` in session state is populated, dashboard cards match the prediction output
- Upload a file with glucose values steadily rising from 4.0 to 12.0 → prediction correctly shows upward trend (predicted values higher than current)
- Upload a file with glucose values dropping from 10.0 to 4.5 → prediction correctly shows downward trend

**LLM Consultation Page**

- Load page with no prediction data → yellow warning banner: "No prediction data loaded. Go to Glucose Prediction → upload an Excel file → run prediction", dashboard section hidden, Analyze button still clickable but shows a second warning
- Load page with prediction data → four metric cards visible with current + 15/30/50min values and delta indicators, trend summary shown
- Insulin radio: select "Yes" → dosage number input, time text input appear; select "No" → they disappear
- Food radio: select "Yes" → description text input, time text input, carbs dropdown appear
- Exercise radio: select "Yes" → type dropdown, duration slider, time input, intensity slider appear
- All lifestyle fields filled + extra notes → click Analyze → LLM returns structured response with 4 clear sections (trajectory, lifestyle impact, recommendations, risk alerts), response time ~3-8 seconds
- Follow-up question: type "Should I go for a walk?" in chat input → response is short and contextual, references earlier glucose values without re-explaining them, does NOT repeat the full 4-part analysis
- Second follow-up: "What about food?" → response stays in context, doesn't mention walking
- Chat history visible → user messages on right, assistant messages on left, system prompt hidden, first user message summarized as "Please analyze my glucose data..."
- API key missing from .env → page loads with warning "LLM chat is unavailable", Analyze button disabled (greyed out), prediction dashboard still visible
- Hypoglycemia test: we crafted a prediction context with last_glucose=3.5 and predictions trending down → LLM response flagged hypoglycemia as #1 priority, recommended fast-acting carbs, explicitly did NOT recommend exercise
- Hyperglycemia test: prediction context with last_glucose=15.0 → LLM flagged hyperglycemia concern, mentioned light walking as potential option with appropriate cautions

**Management Page**

- Login as admin → "All Registered Users" table shows all accounts (including demo admin and user), "All Uploaded / Generated Files" table shows files from every user with username column
- Login as standard user → "My Profile" shows own info, "My Uploaded / Generated Files" shows only own files — no other users' data visible
- Fresh account with no uploads → "You haven't uploaded any data yet" message with link to Model Training
- After completing training → Management page file list updates to show new rows (raw_upload, 15min_data, ..., metrics_50min)
- File table columns are correct: File ID, Type, File Name, Created timestamp

**Database**

- Delete `glucoguard.db` and restart app → `init_db()` recreates all 4 tables, demo accounts auto-seeded
- Use an old MS2 database file (no password_hash/salt columns) → migration logic auto-adds columns, demo accounts backfilled with hashed passwords
- `save_user_file()` with a 500KB Excel file → BLOB stored correctly, `get_user_file_content()` returns identical bytes
- `get_latest_user_file_content()` with multiple files of same type → always returns the newest one (highest id), verified by checking created_at timestamp
- Concurrent users: logged in as admin in one browser tab, standard user in another → each session sees only their own data in Management page and analytics (Streamlit sessions are isolated by browser tab)

### 10.2 User Testing Sessions

We ran four structured testing sessions with people who had never seen GlucoGuard before. Each session lasted about 25–35 minutes. We gave them the app running on a laptop, the sample data files, and a one-sentence description ("this is a glucose monitoring and prediction app for diabetes"). We did not give them instructions — we wanted to see where they got stuck.

**Tester 1 — University student, no diabetes background**

- Registered an account in under 2 minutes, no issues with the form
- Found the Model Training page from the sidebar without prompting
- Uploaded `glucose_record_patient1.xlsx` successfully, but tried to click "Start Training" before generating training files — the error message told them to complete Step 2, and they figured it out
- Waited through the full training (~14 minutes), commented that the live terminal output made the wait feel shorter because "you can see it's actually working"
- Switched to Glucose Prediction, uploaded the same file, ran prediction — excited about the Plotly chart: "oh, the red dots go up, that's the prediction"
- Went to LLM Consultation, filled in food context (had eaten rice 30 minutes ago), got analysis — read the whole thing, said the hypoglycemia alert "makes me feel safer"
- **Issues found:** Tried to upload a `.csv` file to Model Training — got a generic Streamlit file type rejection (not our error message). We should support CSV or show a clearer message.
- **Overall:** Completed the full workflow in about 30 minutes. Said it "feels like a real medical app."

**Tester 2 — Graduate student, some machine learning background**

- Created an account, immediately went to Model Training
- Generated training files, understood the sliding-window concept from the metric cards showing different window counts
- During training, watched the real-time logs carefully — asked "the NOA is searching hyperparameters? What bounds?" (this person reads terminal output)
- After training, spent several minutes on the Performance Analytics section — zoomed into the Matplotlib plots, compared RMSE across horizons, noted that 50min MAPE was higher as expected
- On Glucose Prediction, uploaded a separate test file (`predict_testdata.xlsx`) instead of the training file — this was the intended workflow and it worked correctly
- On LLM Consultation, tested the safety guardrails deliberately: set glucose context low, asked "should I exercise?" — confirmed the LLM refused to recommend exercise
- **Issues found:** Wanted to download the prediction results as Excel. There's no export button. They right-clicked the Plotly chart expecting a "download data" option.
- **Overall:** "The ML pipeline is legit. The UI needs export features." Completed workflow in ~25 minutes.

**Tester 3 — Friend with a family member who has diabetes**

- This was the most valuable session. They approached the app as if helping a relative.
- Registration was smooth. They used their relative's name as the display name.
- On Model Training: "So I need to upload the CGM data? Where do I get that?" — This highlighted that we need a section explaining where CGM data comes from (Dexcom Clarity export, Freestyle Libre reports, etc.)
- Training wait time was a concern: "14 minutes is long if you're checking your glucose before a meal." They suggested adding a "use pre-trained model" option for first-time users who just want predictions.
- On Glucose Prediction: they tried to enter a single glucose value manually instead of uploading an Excel file — "I just want to type in my current reading, I don't have a file right now." This is a valid use case we don't support yet (MS2 had a manual entry form, MS3 replaced it with file upload for real predictions).
- LLM Consultation was the highlight: they filled in realistic context (their relative's typical meal and insulin timing) and found the recommendations "actually practical, not generic." They asked three follow-up questions about carb counting, bedtime snacks, and alcohol — all got reasonable responses.
- **Issues found:** (1) No manual glucose entry for quick single-point prediction, (2) no explanation of where to get CGM data files, (3) training time is a barrier for urgent use cases
- **Overall:** "This would help my aunt. But make it faster to get a prediction without training first."


### 10.3 Issues Found & Fixed from Testing

Based on the user testing sessions, here's what we fixed before MS3 submission:

| Issue | Found by | What we did |
|---|---|---|
| No CSV upload support on Model Training page | Tester 1 | Low priority — Streamlit's `file_uploader` type filter blocks non-xlsx. Added a caption telling users to convert CSV to Excel. Full CSV support deferred. |
| No export button for prediction results | Tester 2 | Added to future work list. The data is in `user_files` so admins can retrieve it via Management, but end users can't download directly from the Prediction page. |
| No explanation of where CGM data comes from | Tester 3 | Added a note in the Model Training page caption: "If you use Dexcom, export from Clarity. If you use Freestyle Libre, export from LibreView. Format: 2 columns, glucose (mmol/L) + timestamp." |
| Registration form clears on error | Tester 1 | Streamlit's default behavior. The form keeps values in `st.session_state` keys so re-typing isn't needed on validation errors — we verified this works correctly. |
| Training time is long for urgent use | Tester 3 | The sample models in `models/` are pre-trained on patient data included in the repo. New users can skip training and go straight to prediction using these pre-trained models. Added a note about this. |
| No session timeout | Tester 4 | Streamlit doesn't natively support session expiry. Added to future work. For now, the logout button is clearly visible in the sidebar. |

### 10.4 Edge Cases & Stress Testing

Beyond user testing, we deliberately broke things to make sure they failed gracefully:

- **Empty database**: Delete `glucoguard.db`, launch app → `init_db()` creates fresh schema, demo accounts auto-seeded, no crash
- **Missing dependency**: Remove `streamlit-option-menu` from environment → app catches `ImportError` at startup, shows clear "Missing required dependencies" message with the pip install command
- **Corrupted .pkl file**: Truncated `models/vmd_noa_bilstm_15min.pkl` to half size → `GlucosePredictor.__init__()` raises `pickle.UnpicklingError`, app catches it on the Prediction page, shows "Model file corrupted — please re-run training"
- **Database locked**: Opened `glucoguard.db` in sqlite3 CLI with a write transaction, then tried to register a user → SQLite's busy timeout handles it gracefully, app shows "Database initialization failed" error
- **Very large upload**: 200MB Excel file with random data → pandas parses it (slowly), sliding-window generator rejects it for wrong format, no OOM crash
- **Unicode in username**: Registered with username "用户测试" → works correctly, stored and displayed properly throughout the app
- **Special characters in password**: Password with `!@#$%^&*()` → PBKDF2 hashing handles any byte string, login works
- **Concurrent training launches**: Clicked "Start Training" twice rapidly → second click shows "Training data ready" message but the first subprocess is already running; second launch would fail because the first is using the DB. Added a session state flag after testing to disable the button during active training.
- **LLM returns empty response**: Simulated by temporarily pointing API to a non-existent endpoint → `_call_chat_api()` catches `APIConnectionError`, shows "LLM service unreachable" message
- **LLM returns malformed JSON**: The NVIDIA API occasionally returns responses with trailing whitespace or unusual Unicode → our `_call_chat_api()` catches `KeyError`/`IndexError`/`AttributeError` from the response parsing and shows a friendly error

---

## 11. Known Limitations & Future Work

### Current Limitations

- **Model training is slow** — 15–20 minutes for all three horizons, mostly in NOA optimization. This is algorithmic, not a bug: 10 agents × 20 iterations × full BiLSTM train+test per evaluation. A GPU would help but isn't required.
- **No hardware integration yet** — our ideal setup is a wearable CGM device with a split sensor-transmitter design, providing 24-hour real-time glucose tracking with needle-free, pain-free application. The sensor would stream readings directly into GlucoGuard, making the current Excel upload step unnecessary. This hardware doesn't exist yet — it's the long-term vision we're building toward. For now, data comes in via Excel files exported from existing CGM platforms (Dexcom Clarity, Freestyle Libre, etc.).
- **LLM requires an API key** — the NVIDIA NIM free tier works, but you need internet access and a key. Without it, the Consultation page is read-only (you can see predictions but not get AI analysis).
- **No alert push notifications** — the LLM can flag hypo/hyperglycemia risk in-chat, but there's no email/SMS/push alert system. With real-time hardware streaming, this would become essential and is a high-priority next step.
- **Single-file training** — you can upload multiple Excel files but training only uses the first one. Multi-file merging would be useful for patients with data split across exports.

### Ideas for Future Work

- **CGM hardware integration** — the big one. Our long-term vision is a custom wearable device: a split sensor-transmitter worn on the body, providing continuous 24-hour glucose monitoring with needle-free, pain-free application. The sensor would stream readings directly into GlucoGuard via Bluetooth or WiFi. No Excel exports, no manual uploads, no third-party CGM portals. A patient puts on the sensor, opens the app, and sees their live glucose trace overlaid with AI predictions — updated every 5 minutes. The data ingestion pipeline we designed in MS3 (per-user DB storage, sliding-window preprocessing, VMD-NOA-BiLSTM inference) is already structured to accept a real-time stream; the missing piece is the hardware itself and the Bluetooth/WiFi receiver layer. This is a multi-year goal that would require hardware prototyping, FDA/regulatory compliance, and clinical validation — but it's the destination everything else is designed to support.
- **GPU acceleration** — the BiLSTM training and NOA evaluations are embarrassingly parallel across agents. A CUDA-enabled PyTorch install would cut training time significantly, making the Train → Predict loop fast enough for near-real-time use.
- **Model comparison dashboard** — train multiple algorithm variants (LSTM-only, SVM, standard BiLSTM) and show side-by-side error metrics so users can pick the best model for their data pattern.
- **Push notifications on threshold crossing** — with real-time data streaming (from existing CGM APIs or our future hardware), trigger alerts when predicted glucose crosses hypo/hyperglycemia thresholds. This would turn GlucoGuard from a check-it-yourself tool into an active safety monitor.
- **PDF health report** — generate a shareable report with glucose trends, prediction summary, and LLM recommendations for doctor visits.

---

## 12. Team Contributions

### Li Yingzhuo 

- **Algorithm core** — implemented and tuned the full VMD-NOA-BiLSTM pipeline: VMD decomposition, NOA swarm optimization, component-wise BiLSTM training, signal reconstruction, error evaluation (MAE, RMSE, MAPE, Clarke Error Grid)
- **Predictor module** (`predictor.py`) — designed the `GlucosePredictor` class that loads trained model packages and runs real-time inference; implemented `excel_to_11col()` for sliding-window data conversion; added the safe VMD wrapper with fallback for edge cases
- **Training data generator** (`generate_training_files()` in app.py) — wrote the function that converts 2-column raw Excel into three horizon-specific 11-column sliding-window training files
- **Model Training page** — integrated the real subprocess execution with live terminal output streaming, progress bar synchronization, and post-training analytics display (prediction tracking plots + RMSE/MAE/MAPE cards)
- **Algorithm integration** — modified `VMD_NOA_BILSTM.py` to support per-horizon `zim` values, database-driven I/O, and subprocess execution from the Streamlit UI
- **Model tuning** — validated prediction accuracy across the three horizons, tuned NOA search bounds and BiLSTM architecture for the glucose prediction task
- **LLM Consultation Hub** — integrated the NVIDIA NIM API via `src/llm_chat.py`, built the lifestyle context inputs (insulin/food/exercise with show/hide logic), designed the safety-tuned system prompt, implemented multi-turn chat with conversation history
- **MS3 README** — prepared the milestone documentation and comparison with MS2

### Xiao Hongyu 

- **Database design & implementation** (`db.py`) — designed the 4-table schema, implemented all CRUD functions, added PBKDF2 password hashing with per-user salt, built the `user_files` BLOB storage system, wrote migration logic for old database versions
- **Authentication system** — replaced the MS2 hardcoded login with DB-backed `verify_user()` and `register_user()`; built the registration UI with validation
- **Management page** — built the role-based user and file management console
- **Database integration throughout** — connected all pages to read/write through `db.py` with per-user scoping; migrated training I/O from local disk to database BLOBs
- **UI/UX** — sidebar navigation,  chat interface styling, layouts designs
- **Testing & documentation** — verified all features end-to-end, maintained `project_log.md`

### Shared Work

- Project planning, milestone scoping, advisor consultations
- Peer evaluations (HealthSync, Lumina)
- Poster design and presentation materials
- Code review and debugging across the full stack

---

## 13. Appendix: Milestone 1 & 2 Summary

### Milestone 1 (31 May 2026)

A basic Streamlit login prototype:
- Username/password login with two simulated accounts
- Session state management
- Role-based welcome message
- Logout functionality
- No database, no prediction, no additional pages

### Milestone 2 (29 June 2026)

A working multi-page prototype with simulated backend:
- 4-page Streamlit app (Login, Dashboard, Model Training, Glucose Prediction)
- SQLite database with 3 tables (users, glucose_records, training_files)
- Model Training page with Excel upload + simulated 7-step progress bar
- Glucose Prediction page in demo mode (generated synthetic predictions)
- Offline VMD-NOA-BiLSTM pipeline in `main.py`
- Placeholder AI Consultation page
- Hardcoded user credentials, plaintext passwords

All MS1 and MS2 functionality is preserved and extended in the MS3 application described above.

---

*GlucoGuard — Orbital 2026 | Team: Xiao Hongyu & Li Yingzhuo*
