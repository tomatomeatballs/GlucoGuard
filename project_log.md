# Project Log

## Effort & Time Investment Log

Estimated time invested by each member across the project (Liftoff through late July 2026).
Hours are approximate but grounded in meeting records, commit history, and task tracking.
Li Yingzhuo led overall architecture, algorithm, prediction pipeline, LLM integration,
training workflow, user testing, MS3 README/log, MS2/MS3 poster & video. Xiao Hongyu focused on
the database layer, management page, and MS1 & MS2 documentation.

| S/N | Task | Date | Xiao Hongyu (hrs) | Li Yingzhuo (hrs) | Remarks |
|---|---|---|---|---|---|
| 1 | [Meeting] Liftoff project planning | 12 May 2026 | 2 | 2 | Team meeting. Discussed project idea, motivation, and Liftoff scope. Li Yingzhuo proposed the CGM glucose prediction concept. |
| 2 | Liftoff poster & pitch video | 13–15 May 2026 | 3 | 2 | Xiao Hongyu recorded and edited the pitch video. Li Yingzhuo designed the poster layout. |
| 3 | Self-learning: Python & Streamlit basics | 15–20 May 2026 | 5 | 6 | Li Yingzhuo studied Streamlit's session state, page routing, and component model in depth. Xiao Hongyu focused on basic Python and Streamlit tutorials. |
| 4 | Milestone 1 login prototype (Streamlit) | 20–28 May 2026 | 3 | 9 | Li Yingzhuo built the full login prototype: authentication flow, session state management, role-based routing, welcome page, and logout. |
| 5 | [Meeting] Milestone 1 scope & submission | 29 May 2026 | 2 | 2 | Team meeting. Confirmed MS1 proof-of-concept scope and planned submission. |
| 6 | Milestone 1 README, requirements & project log | 30–31 May 2026 | 6 | 1 | Xiao Hongyu wrote the MS1 README, requirements.txt, and project log. Li Yingzhuo reviewed. |
| 7 | Milestone 1 testing & GitHub submission | 31 May 2026 | 3 | 1 | Xiao Hongyu tested, prepared, and pushed the GitHub submission. Li Yingzhuo reviewed. |
| 8 | Self-learning: SQLite & database design | 3–10 June 2026 | 8 | 2 | Xiao Hongyu studied SQLite schema design and CRUD operations. Li Yingzhuo reviewed for architecture compatibility. |
| 9 | Login card redesign & system titles | 5 June 2026 | 1 | 4 | Li Yingzhuo redesigned the login card UI with clearer fonts, color scheme, and personalised system branding. |
| 10 | SQLite database MVP (db.py) | 18 June 2026 | 13 | 1 | Xiao Hongyu built the initial db.py: users and glucose_records tables, init/insert/read functions. Li Yingzhuo specified the API surface. |
| 11 | Integrating the database dashboard into the app | 18 June 2026 | 3 | 4 | Li Yingzhuo connected login to the database dashboard, added glucose input form, history table display, and trend chart. |
| 12 | Self-learning: ML & time-series (VMD/NOA/BiLSTM) | 15–24 June 2026 | 3 | 10 | Li Yingzhuo studied VMD signal decomposition theory, NOA swarm optimization, and BiLSTM architectures in depth — reading papers, implementing prototypes, and testing on sample glucose data. Xiao Hongyu read introductory materials on the same topics. |
| 13 | VMD-NOA-BiLSTM prediction pipeline (main.py) | 25 June 2026 | 2 | 11 | Li Yingzhuo implemented the full pipeline: VMD decomposition (via vmdpy), NOA hyperparameter optimization (custom implementation), component-wise BiLSTM training, signal reconstruction, and error evaluation (MAE, RMSE, MAPE, Clarke Error Grid). |
| 14 | Aligning the algorithm backend with the UI | 27 June 2026 | 4 | 5 | Li Yingzhuo piped user entries from Streamlit into SQLite and connected training parameters from the UI sliders to the algorithm backend. |
| 15 | Integrating the pipeline & trend charts (app.py) | 28 June 2026 | 2 | 5 | Li Yingzhuo integrated the prediction pipeline into app.py: multi-source trend chart overlay, historical data + prediction visualization, form-to-DB-to-chart data flow. Xiao Hongyu worked on the DB read path for chart data. |
| 16 | [Meeting] Milestone 2 progress & deliverables | 26 June 2026 | 2 | 2 | Team meeting. Reviewed MS2 progress, identified gaps, planned report/poster/video deliverables. |
| 17 | Milestone 2 report/README & poster & video | 26–29 June 2026 | 4 | 6 | Xiao Hongyu wrote the MS2 README and project log. Li Yingzhuo designed the MS2 poster and recorded/edited the MS2 video. |
| 18 | Milestone 2 submission | 29 June 2026 | 2 | 1 | Xiao Hongyu prepared and pushed the MS2 GitHub submission. Li Yingzhuo reviewed. |
| 19 | Advisor demo & consultation | late June 2026 | 2 | 2 | Both met with advisor Kwa Jian Quan to demonstrate the app and collect feedback on poster design, feature prioritization, and MS3 direction. |
| 20 | Peer Evaluation 1 (HealthSync) | June 2026 | 0.25 | 0.25 | Quick review (~15 min). Completed the Orbital peer evaluation for HealthSync. |
| 21 | Peer Evaluation 2 (Lumina) | June–July 2026 | 0.25 | 0.25 | Quick review (~15 min). Completed the Orbital peer evaluation for Lumina. |
| 22 | Data validation for uploaded training files | 5 July 2026 | 4 | 2 | Added validation logic for training file uploads: column count check, missing value detection, non-numeric data rejection. |
| 23 | Poster redesign (advisor feedback) | early July 2026 | 1 | 3 | Li Yingzhuo redesigned the poster based on advisor feedback. Xiao Hongyu reviewed. |
| 24 | MS3 architecture planning & design | 1–3 July 2026 | 1 | 4 | Li Yingzhuo designed the MS3 system architecture: per-user data isolation strategy, subprocess-based training integration, BLOB-based file storage in user_files table, the Train → Predict → Consult pipeline structure, and the LLM chat architecture. All major MS3 architectural decisions were made in this period. |
| 25 | [Meeting] MS3 kickoff & task division | 6 July 2026 (Sun) | 4 | 4 | Weekly Sunday meeting (~4h). Broke down MS3 tasks: algorithm side assigned to Li Yingzhuo; DB side assigned to Xiao Hongyu. Set MS3 timeline. |
| 26 | predictor.py — GlucosePredictor class | 6–9 July 2026 | 0 | 4 | Li Yingzhuo designed and implemented the GlucosePredictor class: loads 3 trained .pkl model packages, runs VMD decomposition + BiLSTM inference per horizon, sums IMF predictions, caches with @st.cache_resource. Also wrote excel_to_11col() for sliding-window conversion from 2-column raw data. Added _safe_vmd() fallback for division-by-zero edge cases. |
| 27 | generate_training_files() — sliding-window generator | 9–10 July 2026 | 0 | 3 | Li Yingzhuo wrote the training file generator in app.py: converts raw 2-column Excel into three 11-column sliding-window files (15min/30min/50min horizons), with per-horizon step-ahead parameters (zim=3/6/10). Includes row-count validation and clear error messages. |
| 28 | VMD_NOA_BILSTM.py — DB-driven refactoring | 10–13 July 2026 | 1 | 4 | Li Yingzhuo refactored VMD_NOA_BILSTM.py: added --user-id CLI argument, replaced all local file I/O with get_latest_user_file_content() and save_user_file() calls, added per-horizon zim support (3/6/10), switched results output from local disk to DB BLOBs. |
| 29 | db.py MS3 enhancements — user_files table & auth | 10–14 July 2026 | 14 | 1 | Xiao Hongyu designed and implemented the user_files table (BLOB storage with user_id + file_type indexing), added PBKDF2 password hashing with per-user salt (register_user, verify_user, _hash_password, _ensure_demo_user), wrote get_user_files, get_all_user_files, get_user_file_content, get_latest_user_file_content. Li Yingzhuo specified the API surface and file_type taxonomy. |
| 30 | [Meeting] Mid-July progress review | 13 July 2026 (Sun) | 3 | 3 | Weekly Sunday meeting (~3h). Reviewed progress on predictor.py, VMD_NOA_BILSTM.py, and db.py. Planned subprocess integration and LLM chat module. |
| 31 | Model Training page — subprocess integration | 14–16 July 2026 | 3 | 5 | Li Yingzhuo integrated the real training subprocess into the Model Training page: subprocess.Popen with --user-id, real-time stdout streaming into Streamlit UI, progress bar synced to log keywords (VMD→20%, NOA→40%, Epoch→70%, Prediction→90%), post-training analytics display (prediction-vs-ground-truth Matplotlib plots + RMSE/MAE/MAPE metric cards per horizon). |
| 32 | src/llm_chat.py — LLM chat module | 14–17 July 2026 | 0 | 3 | Li Yingzhuo built the LLM chat module: OpenAI SDK wrapper pointed at NVIDIA NIM API (llama-3.1-8b-instruct), ask_llm() for one-shot structured analysis, ask_llm_chat() for multi-turn conversation with full message history, shared _call_chat_api() error handler covering AuthenticationError, RateLimitError, APIConnectionError, APIError, and malformed responses. API key loaded from .env via python-dotenv. |
| 33 | LLM Consultation page — full chat interface | 17–20 July 2026 | 1 | 6 | Li Yingzhuo built the LLM Consultation page: prediction dashboard (4 metric cards with delta indicators + trend summary auto-populated from prediction_context), 3-column lifestyle context inputs (insulin/food/exercise with radio-button show/hide logic), structured 4-part LLM prompt (trajectory + lifestyle impact + recommendations + risk alerts), multi-turn follow-up chat via st.chat_input, conversation history preserved in st.session_state.ai_chat_messages. Designed safety-tuned system prompt with hard hypo/hyperglycemia guardrails. |
| 34 | Management page | 18–20 July 2026 | 8 | 1 | Xiao Hongyu built the role-based Management page: admin sees all users table + all files table (joined with usernames), standard user sees own profile + own files only. |
| 35 | [Meeting] Pre-testing review & bug triage | 20 July 2026 (Sun) | 4 | 4.5 | Weekly Sunday meeting (~4h). End-to-end walkthrough of Train→Predict→Consult flow, identified 8 bugs. Divided fixes between team members. |
| 36 | Bug fixes, edge cases & stability | 20–22 July 2026 | 4 | 4 | Li Yingzhuo fixed: safe VMD fallback for constant/zero-variance signals, subprocess crash recovery with clear error messages, Plotly chart time-axis formatting, LLM empty-response handling, concurrent training launch guard (session state flag to disable button during active training), prediction context sync edge case when switching pages. Xiao Hongyu fixed: DB migration logic for old MS2 databases (auto-add password_hash/salt/name columns), file list empty-state handling. |
| 37 | Model tuning & validation across 3 horizons | 22–23 July 2026 | 0 | 4 | Li Yingzhuo ran full training on sample patient data for all 3 horizons, validated prediction accuracy, tuned NOA search bounds (lb/ub arrays) and BiLSTM architecture parameters, verified RMSE/MAE/MAPE metrics were reasonable (~0.3-0.8 RMSE on 15min, ~0.5-1.2 on 30min, ~0.8-1.8 on 50min), confirmed Clarke Error Grid results in clinically acceptable zones. |
| 38 | User testing — session design & recruitment | 22–23 July 2026 | 0.5 | 2 | Li Yingzhuo designed the user testing protocol. |
| 39 | User testing — running sessions | 23–24 July 2026 | 0.5 | 4 | Li Yingzhuo ran all 4 user testing sessions (~25-35 min each): set up the app on a laptop, gave testers sample data files and a one-sentence description, observed without guidance, recorded issues, collected feedback and direct quotes. Key findings: CSV upload not supported, no manual single-value glucose entry, training time too long for urgent use, CGM data source unclear to non-technical users. |
| 40 | User testing — analysis & fixes | 24–25 July 2026 | 0.5 | 3 | Li Yingzhuo analyzed all user testing findings, categorized issues by severity, implemented fixes: added CGM data source guidance in Model Training caption, added pre-trained model note so new users can skip training, verified form state preservation on validation errors. Documented all findings in README Section 10.3. |
| 41 | Advisor meeting + team sync | 24 July 2026 | 3 | 3 | Both met with advisor Kwa Jian Quan to demonstrate MS3 progress and collect feedback. Continued with internal team meeting afterwards to plan final steps. |
| 42 | MS3 poster design | 24–25 July 2026 | 0 | 4 | Li Yingzhuo designed the MS3 poster from scratch. |
| 43 | MS3 video — scripting, recording & editing | 25–26 July 2026 | 0 | 5 | Li Yingzhuo wrote the script, recorded the full app walkthrough, and edited the final video. |
| 44 | [Meeting] Final MS3 submission review | 27 July 2026 (Sun) | 2 | 2 | Weekly Sunday meeting (~2h). Reviewed all MS3 deliverables, README, and project log. Assigned final submission tasks. |
| 45 | MS3 README & project log — full documentation | 25–27 July 2026 | 0 | 5 | Li Yingzhuo wrote the comprehensive MS3 README (~790 lines): project overview with hardware vision, MS3 progress summary, detailed MS2→MS3 comparison across 9 areas, 6 feature descriptions, system architecture walkthrough (5 layers + 5-stage data flow), database design in prose, new user guide with step-by-step walkthrough, 3-part testing section (functional checklist + 2 user testing narratives + edge cases), limitations & future work, team contributions. |
| | **Total (hours)** | | **125** | **160** | **Combined: 285 hours** |

---

## Milestone 3 Summary

For Milestone 3, GlucoGuard completed the transition from a prototype with simulated internals to a fully functional, end-to-end application. Every MS2 placeholder was replaced with real, working code.

**Completed in Milestone 3**

- **Real authentication** — replaced the hardcoded login dict with DB-backed PBKDF2-SHA256 password hashing, per-user random salts, full registration UI with validation, and auto-migration for old databases.
- **Live model training** — the Model Training page now spawns `VMD_NOA_BILSTM.py` as a real subprocess. Users watch actual NOA optimization, VMD decomposition, and BiLSTM training logs stream into the browser in real time. Training reads from and writes to the database — no shared local files.
- **Real glucose prediction** — `predictor.py` loads trained .pkl model packages and runs actual VMD decomposition + BiLSTM inference on user-uploaded data. Outputs genuine predicted glucose values at +15, +30, and +50 minutes, displayed as metric cards and an interactive Plotly chart.
- **AI LLM Consultation Hub** — full multi-turn chat interface powered by NVIDIA NIM API (LLaMA 3.1 8B Instruct). Lifestyle context inputs (insulin, food, exercise) feed into a structured 4-part analysis. Safety-tuned system prompt with hard hypo/hyperglycemia guardrails. Follow-up questions stay contextual via full conversation history.
- **Per-user data isolation** — new `user_files` table stores every file (uploads, training data, predictions, metrics) as BLOBs keyed to user_id. The training subprocess, web UI, and analytics display all read/write through this table. No shared local folders on any critical path.
- **Management console** — role-based page: admins see all registered users and all files across every account; standard users see only their own profile and files.
- **Automatic sliding-window generation** — raw 2-column Excel uploads are converted into three 11-column training files (15min/30min/50min horizons) with correct per-horizon forecast steps (zim=3/6/10).
- **Integrated performance analytics** — after training, prediction-vs-ground-truth plots and RMSE/MAE/MAPE metric cards are shown for all three horizons, pulled from per-user database rows.
- **End-to-end Train → Predict → Consult pipeline** — the full user workflow is wired: upload raw data → generate training files → train model → predict future glucose → get AI-powered lifestyle recommendations → ask follow-up questions.

**Architecture decisions made in MS3**

- Li Yingzhuo designed the overall MS3 architecture: the subprocess-based training model (keeping the Streamlit UI responsive while heavy computation runs), the BLOB-based per-user file storage strategy (eliminating shared folders entirely), the Train → Predict → Consult pipeline structure, the LLM chat architecture with multi-turn conversation history, and the session-state bridge between Glucose Prediction and LLM Consultation pages.

---

## Detailed July 2026 Work Log

### 27 July 2026 (Sunday)

**[Meeting] Final MS3 submission review (Sunday, ~2h)**
- Team meeting. Reviewed all deliverables, confirmed everything complete.
- Li Yingzhuo: 2 hrs | Xiao Hongyu: 2 hrs

### 25–27 July 2026

**MS3 README & documentation**
- Li Yingzhuo wrote the MS3 README and updated the project log.
- Li Yingzhuo: 5 hrs

### 25–26 July 2026

**MS3 video — scripting, recording & editing**
- Li Yingzhuo wrote the script, recorded the full app walkthrough, edited with voiceover and captions.
- Li Yingzhuo: 5 hrs

### 24–25 July 2026

**MS3 poster design**
- Li Yingzhuo designed the MS3 poster.
- Li Yingzhuo: 1 hr | Xiao Hongyu: 3 hr


**User testing — analysis & fixes**
- Li Yingzhuo analyzed findings, implemented fixes, documented results.
- Li Yingzhuo: 3 hrs | Xiao Hongyu: 0.5 hrs

### 23–24 July 2026

**User testing — running sessions**
- Li Yingzhuo ran 4 user testing sessions with diverse testers, recorded issues and quotes.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 0.5 hrs

**User testing — session design & recruitment**
- Li Yingzhuo designed the testing protocol, recruited 4 testers, scheduled sessions.
- Li Yingzhuo: 2 hrs | Xiao Hongyu: 0.5 hrs

### 22–23 July 2026

**Model tuning & validation across 3 horizons**
- Li Yingzhuo trained on sample data, validated RMSE/MAE/MAPE metrics across all 3 horizons, tuned NOA bounds and BiLSTM parameters.
- Li Yingzhuo: 4 hrs

### 20–22 July 2026

**[Meeting] Pre-testing review & bug triage (20 July, Sunday, ~4h)**
- Team meeting. Walkthrough of full Train→Predict→Consult flow, identified bugs, divided fixes.
- Li Yingzhuo: 4.5 hrs | Xiao Hongyu: 4 hrs

**Bug fixes, edge cases & stability**
- Li Yingzhuo fixed: VMD crash on constant signals, subprocess error handling, Plotly formatting, LLM error handling, concurrent training guard. Xiao Hongyu fixed: DB migration for old databases, empty-state handling on Management page.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 4 hrs

### 17–20 July 2026

**LLM Consultation page — full chat interface**
- Li Yingzhuo built the full chat interface: prediction dashboard, lifestyle context inputs, structured LLM prompt, multi-turn follow-up chat, safety-tuned system prompt.
- Li Yingzhuo: 6 hrs | Xiao Hongyu: 1 hr

**Management page**
- Xiao Hongyu built the role-based Management page.
- Li Yingzhuo: 1 hr | Xiao Hongyu: 8 hrs

### 14–17 July 2026

**Model Training page — subprocess integration**
- Li Yingzhuo integrated real subprocess execution with live output streaming, progress bar, and analytics display.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 4 hrs

**src/llm_chat.py — LLM chat module**
- Li Yingzhuo built the LLM chat wrapper (NVIDIA NIM API, ask_llm + ask_llm_chat, error handling, .env config).
- Li Yingzhuo: 3 hrs

### 10–14 July 2026

**db.py MS3 enhancements**
- Xiao Hongyu implemented user_files table, PBKDF2 password hashing, and file storage functions.
- Li Yingzhuo: 1 hr | Xiao Hongyu: 14 hrs

**VMD_NOA_BILSTM.py — DB-driven refactoring**
- Li Yingzhuo added --user-id argument, switched I/O from local disk to DB (get_latest_user_file_content / save_user_file), added per-horizon zim support.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 1 hr

### 9–10 July 2026

**generate_training_files() — sliding-window generator**
- Li Yingzhuo wrote the 2-col→11-col sliding-window converter with per-horizon zim values.
- Li Yingzhuo: 3 hrs

### 6–9 July 2026

**predictor.py — GlucosePredictor class**
- Li Yingzhuo implemented GlucosePredictor: loads .pkl models, VMD+BiLSTM inference, excel_to_11col converter, @st.cache_resource.
- Li Yingzhuo: 4 hrs

### 6 July 2026 (Sunday)

**[Meeting] MS3 kickoff & task division (Sunday, ~4h)**
- Team meeting. Broke down MS3 tasks, set timeline.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 4 hrs

### 1–5 July 2026

**MS3 architecture planning & design**
- Li Yingzhuo designed the MS3 architecture: per-user data isolation, subprocess-based training, Train→Predict→Consult pipeline, LLM chat structure.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 1 hr

**Data validation for uploaded training files**
- Added upload validation (column count, missing values, numeric/timestamp checks).
- Li Yingzhuo: 2 hrs | Xiao Hongyu: 2 hrs

**Poster redesign (advisor feedback)**
- Li Yingzhuo redesigned the poster based on advisor feedback.
- Li Yingzhuo: 3 hrs | Xiao Hongyu: 1 hr

### Late June – Early July 2026

**Advisor demo & consultation**
- Both met with advisor Kwa Jian Quan to demonstrate the app and collect feedback.
- Li Yingzhuo: 2 hrs | Xiao Hongyu: 2 hrs

---

## 28 June 2026

**Pipeline & trend chart integration into app.py**
- Li Yingzhuo integrated prediction pipeline and trend charts. Xiao Hongyu worked on DB logging integration.
- Li Yingzhuo: 5 hrs | Xiao Hongyu: 3 hrs

## 27 June 2026

**Algorithm backend ↔ UI alignment**
- Li Yingzhuo connected algorithm to UI. Xiao Hongyu worked on the form→DB→chart data path.
- Li Yingzhuo: 5 hrs | Xiao Hongyu: 3 hrs

## 25 June 2026

**VMD-NOA-BiLSTM prediction pipeline (main.py)**
- Li Yingzhuo implemented VMD decomposition, NOA optimization, component-wise BiLSTM, and error evaluation.
- Li Yingzhuo: 8 hrs | Xiao Hongyu: 2 hrs

## 18 June 2026

**Database dashboard integration**
- Li Yingzhuo connected login to DB dashboard, added glucose input form, history table, and trend chart.
- Li Yingzhuo: 4 hrs | Xiao Hongyu: 5 hrs

**SQLite database MVP (db.py)**
- Xiao Hongyu built the initial db.py: users and glucose_records tables, CRUD functions.
- Li Yingzhuo: 1 hr | Xiao Hongyu: 13 hrs

## 5 June 2026

**Login card redesign**
- Li Yingzhuo redesigned the login card with new fonts and branding.
- Li Yingzhuo: 3 hrs | Xiao Hongyu: 1 hr

## 31 May 2026

**Milestone 1 submission**

Li Yingzhuo:
- Prepared the initial Streamlit login module prototype
- Implemented the basic authentication flow with username and password
- Added simulated admin and standard user accounts
- Added role-based welcome messages and logout functionality
- Confirmed the Milestone 1 scope as login-only prototype

Xiao Hongyu:
- Wrote the MS1 README and requirements.txt
- Created and maintained the project log
- Recorded and edited the Liftoff/MS1 pitch video
- Set up and organized the GitHub repository
- Tested the login flow locally and verified logout function

---

## Milestone 1 Summary (31 May 2026)

A basic Streamlit login prototype demonstrating username/password authentication, session state management, role-based welcome page, and logout functionality. This was a technical proof of concept only — no database, no prediction model, no additional pages. The full glucose prediction model, database integration, dashboard, and health report generation were planned for later milestones.

---

*GlucoGuard — Orbital 2026 | Team: Li Yingzhuo & Xiao Hongyu*
