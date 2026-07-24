"""
CGM Glucose Monitoring System - Login + Model Training + Glucose Prediction +
Data enter to Database (A simple authentication interface with SQLite glucose record storage.)
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import os
import sys
import time
import glob
import subprocess
import io  # [KYLE] 2026-07-24 -- needed to read/write DB-stored file bytes as if they were files
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Real VMD-NOA-BiLSTM inference (lazy-loaded so a missing model dir doesn't crash import)
try:
    from predictor import GlucosePredictor
except ImportError:
    GlucosePredictor = None

# Real AI consultation chat (requires src/llm_chat.py + a valid .env API key)
try:
    from src.llm_chat import ask_llm, ask_llm_chat  # ask_llm_chat: [KYLE] 2026-07-24, real multi-turn conversation
except ImportError:
    ask_llm = None
    ask_llm_chat = None

# Securely import the database module (Unified at the top)
try:
    from db import (
        init_db,
        add_glucose_record,
        get_glucose_records,
        save_training_file_to_db,
        register_user,
        verify_user,
        get_all_users,
        save_user_file,
        get_user_files,
        get_all_user_files,
        get_latest_user_file_content,  # [KYLE] 2026-07-24 -- for the DB-driven training/results pipeline
    )
except ImportError:
    st.error("❌ `db.py` file not found in the same directory, or exported functions are incorrect.")
    st.stop()

# Securely import the third-party navigation component
try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("❌ Missing required dependencies. Please run in your terminal: `pip install streamlit-option-menu`")
    st.stop()


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="CGM Glucose Monitoring System",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== DATABASE INITIALIZATION ====================
try:
    init_db()
except Exception as e:
    st.error(f"❌ Database initialization failed! Reason: {str(e)}")
    st.stop()


# ==================== SESSION STATE INITIALIZATION ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

if "role" not in st.session_state:
    st.session_state.role = "standard"


# ==================== LOGIN PAGE ====================
def login_page():
    """
    Display the login/registration interface.
    Authenticates credentials against the database (hashed passwords via db.verify_user)
    and manages session state.
    """
    left_col, center_col, right_col = st.columns([1, 4, 1])

    with center_col:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div style="background-color: #87CEFA; padding: 30px; border-radius: 10px; text-align: center; color: white;"><h1 style="font-size: 64px; font-weight: 600; margin: 0; line-height: 1.4; font-family: \'Chalkboard SE\';">Welcome to <br> GlucoGuard!</h1><p style="margin-top: 25px; opacity: 0.9; font-size: 22px; line-height: 1.6; font-family: \'Comic Sans MS\';">🤖 AI-assisted Prediction System<br>📈 Real-time Glucose Tracking & Prediction</p></div>', unsafe_allow_html=True)

            st.markdown('<br>', unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        with login_tab:
            username = st.text_input(
                'Username',
                placeholder='Enter your username (e.g., admin)',
                key='login_username'
            )

            password = st.text_input(
                'Password',
                type='password',
                placeholder='Enter your password',
                key='login_password'
            )

            st.markdown('<br>', unsafe_allow_html=True)

            if st.button('🔐 Login', use_container_width=True):
                user = verify_user(username, password)
                if user is not None:
                    st.session_state.logged_in = True
                    st.session_state.username = user["username"]
                    st.session_state.user_id = user["user_id"]
                    st.session_state.display_name = user["name"]
                    st.session_state.role = user["role"]
                    st.success(f'✅ Welcome back, {user["name"]}!')
                    st.balloons()
                    st.rerun()
                else:
                    st.error('❌ Invalid username or password.')
                    with st.expander('ℹ️ Need help logging in?'):
                        st.markdown("""
                        **Default Test Accounts:**
                        - Username: `admin` | Password: `123456` (Administrator access)
                        - Username: `user` | Password: `123456` (Standard user access)

                        Or create your own account under the **Register** tab.
                        """)

        with register_tab:
            st.markdown("Create a new GlucoGuard account.")
            new_name = st.text_input('Display Name', placeholder='e.g., Jane Tan', key='register_name')
            new_username = st.text_input('Choose a Username', key='register_username')
            new_password = st.text_input('Choose a Password', type='password', key='register_password')
            confirm_password = st.text_input('Confirm Password', type='password', key='register_confirm')

            if st.button('📝 Create Account', use_container_width=True):
                if not new_username or not new_password:
                    st.error('❌ Username and password are required.')
                elif new_password != confirm_password:
                    st.error('❌ Passwords do not match.')
                elif len(new_password) < 6:
                    st.error('❌ Password must be at least 6 characters long.')
                else:
                    success, message = register_user(new_username, new_password, new_name or new_username)
                    if success:
                        st.success(f'✅ {message} You can now log in from the Login tab.')
                    else:
                        st.error(f'❌ {message}')


# ==================== DASHBOARD PAGE ====================
def dashboard_page():
    if not st.session_state.logged_in:
        login_page()
    else:
        st.title('GlucoGuard')
        st.title('AI-assisted Prediction system')
        st.markdown(f"### Welcome, **{st.session_state.display_name}**!")
        st.markdown(f"**Role:** {st.session_state.role}")
        
        st.divider()
        st.info("""
        ✅ You have successfully logged into the GlucoGuard AI-assisted Prediction System.
        
        **Features available in full version:**
        - 📊 Real-time glucose dashboard
        - 👥 User management (Admin only)
        - 🤖 AI-powered glucose prediction
        - 📈 Interactive data visualization
        - 📄 Health report generation
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button('Logout', use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.session_state.user_id = None
                st.session_state.display_name = ''
                st.session_state.role = 'standard'
                st.rerun()


def save_to_database(timestamp, glucose_value):
    pass


# ==================== SLIDING-WINDOW TRAINING DATA GENERATOR ====================
def generate_training_files(df_2col, data_dir='data'):
    """
    Convert a 2-column Excel (glucose_value + timestamp) into the three 11-column
    training files required by VMD_NOA_BILSTM.py.

    Each output file follows the sliding-window format:
      cols 0-9 : 10 consecutive glucose readings (50-min look-back at 5-min intervals)
      col 10   : the glucose value h steps ahead (prediction target)

    look_back is fixed at 10; horizon (steps ahead) is 3/6/10 for 15/30/50 minutes —
    this is what actually makes the three files predict different distances into the
    future, not just the same next-5-minute value with a different column count.
    """
    df = df_2col.copy()
    df = df.iloc[:, :2]
    df.columns = ['glucose', 'timestamp']
    df = df.sort_values('timestamp').reset_index(drop=True)

    glucose = df['glucose'].values.astype(float)
    n = len(glucose)

    horizons = {'15min': 3, '30min': 6, '50min': 10}
    look_back = 10
    max_offset = max(horizons.values())
    min_required = look_back + max_offset

    if n < min_required:
        raise ValueError(
            f"Need at least {min_required} glucose readings (5-min intervals) to build "
            f"training windows for all horizons. Only {n} rows provided."
        )

    os.makedirs(data_dir, exist_ok=True)
    output_paths = {}

    for horizon_name, h_steps in horizons.items():
        rows = []
        for i in range(look_back - 1, n - h_steps):
            history = glucose[i - (look_back - 1): i + 1]
            target = glucose[i + h_steps]
            rows.append(list(history) + [target])

        df_out = pd.DataFrame(rows)
        file_path = os.path.join(data_dir, f'{horizon_name}_data.xlsx')
        df_out.to_excel(file_path, index=False, header=False)
        output_paths[horizon_name] = file_path

    return output_paths


def _describe_trend(glucose_series):
    """Return a short text summary of the glucose trend (direction + range)."""
    vals = np.array(glucose_series)
    if len(vals) < 3:
        return "Insufficient data for trend analysis."
    recent = vals[-6:] if len(vals) >= 6 else vals[-3:]
    slope = np.polyfit(np.arange(len(recent)), recent, 1)[0]
    avg = np.mean(recent)
    if avg > 10.0:
        level = "hyperglycemic range"
    elif avg < 3.9:
        level = "hypoglycemic range"
    else:
        level = "normal range"
    if slope > 0.05:
        direction = "rising"
    elif slope < -0.05:
        direction = "falling"
    else:
        direction = "stable"
    return f"Glucose is {direction} in the {level} (recent avg: {avg:.1f} mmol/L, trend slope: {slope:+.2f}/step)."


@st.cache_resource
def load_predictor():
    """Cache the loaded VMD-NOA-BiLSTM predictor across Streamlit reruns."""
    if GlucosePredictor is None:
        return None
    return GlucosePredictor(model_dir='models')


def check_models_ready():
    """Check whether all 3 trained horizon model files exist."""
    model_files = [os.path.join('models', f'vmd_noa_bilstm_{h}.pkl') for h in ['15min', '30min', '50min']]
    return all(os.path.exists(f) for f in model_files)


# ==================== MANAGEMENT PAGE ====================
def management_page():
    """
    Role-based view of user profiles and files.
    Standard users see only their own profile + files; Administrators see everyone's.
    """
    st.title("👤 Management")
    st.markdown("---")

    is_admin = st.session_state.role == "Administrator"

    if is_admin:
        st.subheader("All Registered Users")
        users = get_all_users()
        if not users:
            st.info("No registered users found.")
        else:
            users_df = pd.DataFrame(
                users, columns=["ID", "Username", "Name", "Role", "Registered"]
            )
            st.dataframe(users_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("All Uploaded / Generated Files")
        all_files = get_all_user_files()
        if not all_files:
            st.info("No files have been uploaded or generated by any user yet.")
        else:
            files_df = pd.DataFrame(
                all_files, columns=["File ID", "Username", "Type", "File Name", "Created"]
            )
            st.dataframe(files_df, use_container_width=True, hide_index=True)

    else:
        st.subheader("My Profile")
        st.markdown(f"**Username:** {st.session_state.username}")
        st.markdown(f"**Display Name:** {st.session_state.display_name}")
        st.markdown(f"**Role:** {st.session_state.role}")

        st.divider()
        st.subheader("My Uploaded / Generated Files")
        my_files = get_user_files(st.session_state.user_id)
        if not my_files:
            st.info("You haven't uploaded any data yet. Go to Model Training to get started.")
        else:
            files_df = pd.DataFrame(
                my_files, columns=["File ID", "Type", "File Name", "Created"]
            )
            st.dataframe(files_df, use_container_width=True, hide_index=True)


# ==================== MODEL TRAINING PAGE ====================
def model_training_page():
    st.title("Model Training & Console")
    st.markdown("---")

    if 'uploaded_data_frames' not in st.session_state:
        st.session_state['uploaded_data_frames'] = {}
    if 'training_files_generated' not in st.session_state:
        st.session_state['training_files_generated'] = False

    # =======================================================
    # 1. Data Input
    # =======================================================
    st.subheader("1. Data Input")
    st.caption(
        "Upload a 2-column Excel file: Column 1 = Glucose Value (mmol/L), "
        "Column 2 = Timestamp. Data should be at regular 5-minute intervals."
    )

    uploaded_files = st.file_uploader(
        "Drag and drop files here or click to upload",
        accept_multiple_files=True,
        type=['xlsx'],
        key="train_uploader"
    )
    if uploaded_files:
        st.success(f"Successfully received {len(uploaded_files)} file(s)")
        for f in uploaded_files:
            st.text(f" {f.name} ({f.size} bytes)")
            if f.name not in st.session_state['uploaded_data_frames']:
                with st.spinner(f"Uploading {f.name} to database..."):
                    try:
                        f.seek(0)
                        df_raw = pd.read_excel(f)

                        # Raw upload is 2 columns: glucose value + timestamp.
                        if df_raw.shape[1] < 2:
                            st.error(f"❌ {f.name}: at least 2 columns required (glucose + timestamp).")
                        elif not pd.to_numeric(df_raw.iloc[:, 0], errors='coerce').notna().all():
                            st.error(f"❌ {f.name}: column 1 (glucose) must be numeric with no missing values.")
                        elif pd.to_datetime(df_raw.iloc[:, 1], errors='coerce').isna().any():
                            st.error(f"❌ {f.name}: column 2 (timestamp) could not be parsed as dates/times.")
                        else:
                            save_training_file_to_db(f.name, f.size, df_raw)
                            save_user_file(st.session_state.user_id, 'raw_upload', f.name, f.getvalue())
                            st.session_state['uploaded_data_frames'][f.name] = df_raw
                            st.toast(f"✅ Data file {f.name} successfully saved to DB!", icon="💾")

                    except Exception as e:
                        st.error(f"Failed to process file {f.name}: {str(e)}")

    # =======================================================
    # 2. Generate Training Files (2-col upload -> 3x 11-col sliding windows)
    # =======================================================
    if st.session_state['uploaded_data_frames']:
        st.divider()
        st.subheader("2. Generate Training Files")
        st.caption(
            "The uploaded raw glucose data is converted into three 11-column "
            "sliding-window files (15/30/50-minute horizons) required by VMD-NOA-BiLSTM."
        )

        file_name = list(st.session_state['uploaded_data_frames'].keys())[0]
        df_uploaded = st.session_state['uploaded_data_frames'][file_name]

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.info(f"Source: `{file_name}` — {len(df_uploaded)} rows × {df_uploaded.shape[1]} columns")
        with col_b:
            generate_btn = st.button("Generate Training Data", type="primary", use_container_width=True)

        if generate_btn:
            try:
                paths = generate_training_files(df_uploaded, data_dir='data')
                st.session_state['training_files_generated'] = True

                st.success("✅ Training files generated successfully!")
                cols = st.columns(3)
                for col_obj, (horizon, path) in zip(cols, paths.items()):
                    df_check = pd.read_excel(path, header=None)
                    with col_obj:
                        st.metric(horizon, f"{df_check.shape[0]} windows", delta=f"{df_check.shape[1]} cols")
                        st.caption(f"`{os.path.basename(path)}`")
                    # Persist each generated training file into the database too
                    with open(path, 'rb') as gen_f:
                        save_user_file(st.session_state.user_id, f'{horizon}_data', os.path.basename(path), gen_f.read())
            except Exception as e:
                st.error(f"❌ Failed to generate training files: {str(e)}")

        if st.session_state['training_files_generated']:
            st.success("✅ Training data ready — proceed to Step 3 below.")

    # =======================================================
    # 3. Model Training Execution
    # =======================================================
    st.divider()
    st.subheader('3. Model Training')

    # [KYLE] 2026-07-24 -- was: glob.glob('data/*min*.xlsx'), which just checks "are
    # there ANY training files sitting in the shared local folder" -- no concept of
    # whose they are. Now: ask the database directly whether THIS logged-in user has
    # all 3 training file types saved. This is the check that actually matches what the
    # training subprocess will look for (it queries the DB by user_id too, see
    # VMD_NOA_BILSTM.py's main()).
    _training_horizons = ['15min_data', '30min_data', '50min_data']
    _user_training_types_present = {
        ft for (_id, ft, _name, _created) in get_user_files(st.session_state.user_id)
        if ft in _training_horizons
    }
    has_all_training_data = len(_user_training_types_present) == len(_training_horizons)

    if has_all_training_data:
        st.info(f"Training data ready in the database for your account: {sorted(_user_training_types_present)}")
    else:
        st.warning("⚠️ No training files saved for your account yet. Complete Step 2 first.")

    col1, col2 = st.columns([1, 4])
    with col1:
        start_btn = st.button('Start Training & Prediction', type='primary')

    log_container = st.container()

    if start_btn:
        with log_container:
            if not os.path.exists('VMD_NOA_BILSTM.py'):
                st.error("❌ VMD_NOA_BILSTM.py not found in the working directory.")
                st.stop()

            if not has_all_training_data:
                st.error("❌ No training files saved for your account. Generate them in Step 2 first.")
                st.stop()

            st.info('Initializing algorithm engine...')
            my_bar = st.progress(0, text='Preparing runtime environment...')

            try:
                status_box = st.empty()
                # [KYLE] 2026-07-24 -- was: cmd = [sys.executable, '-u',
                # 'VMD_NOA_BILSTM.py'] with no arguments -- the subprocess had no way to
                # know whose data to train on, so it just grabbed whatever was in
                # data/. Now it's told explicitly via --user-id, which it uses to pull
                # this user's own files from the database (see VMD_NOA_BILSTM.py).
                cmd = [sys.executable, '-u', 'VMD_NOA_BILSTM.py', '--user-id', str(st.session_state.user_id)]

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                st.markdown("##### Real-time Terminal Output")
                st.caption(
                    "VMD-NOA-BiLSTM is training. Initial launch ~30-60s; "
                    "full optimization ~3-7 min depending on hardware."
                )
                log_placeholder = st.empty()
                full_logs = []

                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        full_logs.append(line)
                        log_placeholder.code("".join(full_logs[-15:]), language="bash")

                        if "VMD" in line:
                            status_box.info("Executing: Variational Mode Decomposition (VMD)...")
                            my_bar.progress(20, text="Step 1: Signal Decomposition")
                        elif "NOA" in line or "Optimization" in line:
                            status_box.info("Executing: Nutcracker Optimization Algorithm (NOA)...")
                            my_bar.progress(40, text="Step 2: Global Parameter Optimization")
                        elif "LSTM" in line or "Epoch" in line:
                            status_box.info("Executing: BiLSTM Neural Network Training...")
                            my_bar.progress(70, text="Step 3: Neural Network Training")
                        elif "Prediction" in line or "Excel" in line or "Model saved" in line:
                            status_box.info("Executing: Exporting results & model files...")
                            my_bar.progress(90, text="Step 4: Result Generation")

                process.wait()
                my_bar.progress(100, text='Computation Completed!')
                status_box.empty()

                if process.returncode == 0:
                    st.success('✅ Model training pipeline completed successfully!')
                    st.session_state['training_files_generated'] = False

                    # Persist the 6 generated result files into the database
                    for horizon in ['15min', '30min', '50min']:
                        pred_path = os.path.join("results", f"Final_Prediction_{horizon}.xlsx")
                        metrics_path = os.path.join("results", f"metrics_{horizon}.csv")
                        if os.path.exists(pred_path):
                            with open(pred_path, 'rb') as rf:
                                save_user_file(st.session_state.user_id, f'prediction_{horizon}', os.path.basename(pred_path), rf.read())
                        if os.path.exists(metrics_path):
                            with open(metrics_path, 'rb') as rf:
                                save_user_file(st.session_state.user_id, f'metrics_{horizon}', os.path.basename(metrics_path), rf.read())

                    with st.expander('View Full Execution Logs'):
                        st.code("".join(full_logs))
                else:
                    st.error('❌ Pipeline exited with an error.')
                    st.error("".join(full_logs))

            except Exception as e:
                st.error(f'Failed to launch training process: {e}')

    # =======================================================
    # 4. Integrated Performance Analytics (Plots & Metrics)
    # =======================================================
    st.divider()
    st.subheader('Integrated Performance Analytics')
    st.caption(
        "Aligns empirical glucose tracking trajectories alongside their error profiles "
        "(RMSE, MAE, MAPE), calculated on the held-out test set for each horizon."
    )

    horizons_config = [
        {'key': '15min', 'label': '15-Minute Forecasting Horizon'},
        {'key': '30min', 'label': '30-Minute Forecasting Horizon'},
        {'key': '50min', 'label': '50-Minute Forecasting Horizon'}
    ]

    for config in horizons_config:
        h_key = config['key']
        h_label = config['label']

        st.markdown(f"### {h_label}")

        # [KYLE] 2026-07-24 -- was: os.path.exists("results/Final_Prediction_{h_key}.xlsx")
        # + open(..., "rb") reading the shared local results/ folder -- whichever user
        # trained most recently would silently show up in everyone else's dashboard too.
        # Now: fetch THIS logged-in user's own latest prediction/metrics rows straight
        # from user_files (same file_type naming VMD_NOA_BILSTM.py now saves under:
        # 'prediction_{horizon}' / 'metrics_{horizon}'). io.BytesIO turns the raw bytes
        # from the database back into something pandas can read like a file.
        pred_file_name, pred_content = get_latest_user_file_content(st.session_state.user_id, f'prediction_{h_key}')
        metrics_file_name, metrics_content = get_latest_user_file_content(st.session_state.user_id, f'metrics_{h_key}')

        if pred_content is not None:
            try:
                pred_df = pd.read_excel(io.BytesIO(pred_content))

                if pred_df.shape[0] < 2:
                    st.warning(f"File `{pred_file_name}` has too few rows to plot.")
                    continue

                y_true_plot = pred_df.iloc[:, -2].values
                y_pred_plot = pred_df.iloc[:, -1].values

                fig, ax = plt.subplots(figsize=(10, 3.8))
                display_len = min(150, len(y_true_plot))

                ax.plot(y_true_plot[:display_len], label='Ground Truth (Reference)', color='#1f77b4', linewidth=2, marker='o', markersize=3)
                ax.plot(y_pred_plot[:display_len], label='Model Forecast (Predicted)', color='#d62728', linewidth=1.8, linestyle='--', marker='x', markersize=4.5)

                ax.set_title(f"{h_label} - Prediction Tracking Profile", fontsize=10, fontweight='bold')
                ax.set_xlabel("Time Series Sequence Points (Samples)", fontsize=8)
                ax.set_ylabel("Glucose Concentration", fontsize=8)
                ax.grid(True, linestyle=':', alpha=0.5)
                ax.legend(loc='upper right', fontsize=8)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                st.pyplot(fig)
                plt.close(fig)

            except Exception as e:
                st.error(f"Failed to render trajectory curves for {h_label}: {e}")

            if metrics_content is not None:
                try:
                    metrics_df = pd.read_csv(io.BytesIO(metrics_content))
                    metrics_dict = dict(zip(metrics_df['Metric'], metrics_df['Value']))
                    rmse_val = metrics_dict.get('RMSE', 0.0)
                    mae_val = metrics_dict.get('MAE', 0.0)
                    mape_val = metrics_dict.get('MAPE', 0.0)

                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric(label="RMSE (Root Mean Squared Error)", value=f"{rmse_val:.4f}")
                    with m_col2:
                        st.metric(label="MAE (Mean Absolute Error)", value=f"{mae_val:.4f}")
                    with m_col3:
                        st.metric(label="MAPE (Mean Absolute Percentage Error)", value=f"{mape_val:.2f}%")

                except Exception as metrics_err:
                    st.error(f"Failed to read metrics for {h_label}: {metrics_err}")
            else:
                st.info(f"Metrics for {h_label} not found in the database yet.")

            st.caption(f"Source (database): file_type=`prediction_{h_key}`, saved as `{pred_file_name}`")
            st.markdown("---")

        else:
            st.info("Horizon profile pending — run training above to generate it.")
            st.caption(f"Will appear here once training saves `prediction_{h_key}` to your account in the database.")


# ==================== BLOOD GLUCOSE PREDICTION PAGE ====================
def blood_sugar_prediction_page():
    st.title("Real-time Blood Glucose Prediction Center")
    st.markdown("---")

    # =======================================================
    # Section 1: Log a single reading (real DB write, unchanged)
    # =======================================================
    st.subheader("Log a Glucose Reading")
    with st.form("glucose_entry_form", clear_on_submit=False):
        st.markdown("**Enter Current Reading**")
        current_time = pd.Timestamp.now()
        st.info(f"Current Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        input_glucose = st.number_input(
            "Current Blood Glucose Value (mmol/L)",
            min_value=1.0, max_value=30.0, value=7.0, step=0.1
        )
        submit_data = st.form_submit_button("💾 Save Reading to Database", use_container_width=True)

        if submit_data:
            timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                add_glucose_record(st.session_state.user_id, timestamp_str, input_glucose)
                st.success("✅ Glucose record successfully persisted to SQLite database!")
            except Exception as e:
                st.error(f"An unexpected database error occurred: {str(e)}")

    st.number_input("Hyperglycemia Alert Threshold Line", value=10.0, step=0.5, key="hyper_threshold")
    st.number_input("Hypoglycemia Alert Threshold Line", value=3.9, step=0.1, key="hypo_threshold")

    st.divider()

    # =======================================================
    # Section 2: Real AI prediction from an uploaded history
    # =======================================================
    st.subheader("AI Prediction from Uploaded Data")

    all_models_ready = check_models_ready()
    if all_models_ready:
        st.success("🧬 VMD-NOA-BiLSTM Core Engine Status: **Ready** — 3 horizon models loaded (15min / 30min / 50min)")
    else:
        st.warning("⚠️ Trained model files not found in `models/`. Run Model Training first.")

    st.caption("Upload a 2-column Excel file: Column 1 = Glucose Value (mmol/L), Column 2 = Timestamp.")
    uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"], key="glucose_excel_upload")

    if uploaded_file is not None:
        try:
            df_raw = pd.read_excel(uploaded_file)

            if df_raw.shape[1] < 2:
                st.error("❌ The Excel file must have at least 2 columns: glucose_value + timestamp.")
            elif GlucosePredictor is None:
                st.error("❌ predictor.py could not be imported — prediction unavailable.")
            else:
                st.info(f"Loaded {len(df_raw)} rows.")
                with st.expander("Data Preview", expanded=False):
                    st.dataframe(df_raw.head(15), use_container_width=True, hide_index=True)

                X_aux, target_series, raw_series, timestamps = GlucosePredictor.excel_to_11col(df_raw)
                st.caption(f"Sliding window constructed: {len(target_series)} windows from {len(raw_series)} readings")

                if st.button("🚀 Execute VMD-NOA-BiLSTM Prediction", type="primary", use_container_width=True):
                    if all_models_ready:
                        with st.spinner('VMD decomposition + BiLSTM inference across 3 horizons...'):
                            predictor = load_predictor()
                            results = predictor.predict_all_horizons(X_aux, target_series)
                        mode_label = "VMD-NOA-BiLSTM"
                    else:
                        st.error("❌ Cannot predict — trained models are missing. Run Model Training first.")
                        st.stop()

                    st.markdown(f"### Future Glucose Predictions — *{mode_label}*")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("15 Minutes", f"{results['15min']:.2f} mmol/L")
                    col_b.metric("30 Minutes", f"{results['30min']:.2f} mmol/L")
                    col_c.metric("50 Minutes", f"{results['50min']:.2f} mmol/L")

                    try:
                        parsed_timestamps = pd.to_datetime(timestamps)
                    except Exception:
                        parsed_timestamps = pd.date_range(end=pd.Timestamp.now(), periods=len(raw_series), freq='5min')
                    last_ts = parsed_timestamps[-1]

                    pred_times = [last_ts, last_ts + pd.Timedelta(minutes=15), last_ts + pd.Timedelta(minutes=30), last_ts + pd.Timedelta(minutes=50)]
                    pred_vals = [float(raw_series[-1]), float(results['15min']), float(results['30min']), float(results['50min'])]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=parsed_timestamps, y=raw_series.astype(float),
                        mode='lines+markers', name='Historical Data',
                        line=dict(color='#90B4CE', width=1.5), marker=dict(size=4, color='#90B4CE'),
                        opacity=0.55,
                    ))
                    fig.add_trace(go.Scatter(
                        x=pred_times, y=pred_vals,
                        mode='lines+markers', name='AI Prediction',
                        line=dict(color='#E63946', width=2.5),
                        marker=dict(size=10, color='#E63946', line=dict(width=2, color='white')),
                    ))
                    fig.update_layout(
                        xaxis_title='Time', yaxis_title='Glucose (mmol/L)',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                        hovermode='x unified', margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='white',
                    )
                    st.markdown("### Glucose Trend & AI Prediction")
                    st.plotly_chart(fig, use_container_width=True)

                    # Save for the AI Consultation page to use as context
                    st.session_state['prediction_context'] = {
                        'raw_series': raw_series.astype(float).tolist(),
                        'timestamps': [str(t) for t in parsed_timestamps],
                        'predictions': results,
                        'last_glucose': float(raw_series[-1]),
                        'last_time': str(last_ts),
                        'mode': mode_label,
                        'glucose_trend': _describe_trend(raw_series.astype(float)),
                    }
                    st.success("✅ Prediction synced to AI Consultation — switch tabs for personalized insights.")

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")


# ==================== AI CONSULTATION PAGE ====================
def ai_consultation_page():
    st.title("💬 AI Medical Consultation Hub")
    st.markdown("---")

    if ask_llm_chat is None:
        st.error("❌ AI chat is unavailable — src/llm_chat.py could not be imported, or the API key is missing from .env.")
        return

    has_prediction = 'prediction_context' in st.session_state

    # ---- Prediction dashboard, if available ----
    if has_prediction:
        ctx = st.session_state['prediction_context']
        st.subheader("Your Glucose Prediction Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        delta_15 = ctx['predictions']['15min'] - ctx['last_glucose']
        delta_30 = ctx['predictions']['30min'] - ctx['last_glucose']
        delta_50 = ctx['predictions']['50min'] - ctx['last_glucose']
        col1.metric("Current", f"{ctx['last_glucose']:.1f} mmol/L")
        col2.metric("+15 min", f"{ctx['predictions']['15min']:.1f} mmol/L", f"{delta_15:+.1f}")
        col3.metric("+30 min", f"{ctx['predictions']['30min']:.1f} mmol/L", f"{delta_30:+.1f}")
        col4.metric("+50 min", f"{ctx['predictions']['50min']:.1f} mmol/L", f"{delta_50:+.1f}")
        st.info(f"Trend: {ctx['glucose_trend']}  |  Prediction engine: *{ctx['mode']}*")
    else:
        st.warning(
            "⚠️ No prediction data loaded. Go to **Glucose Prediction** → upload an Excel "
            "file → run prediction → then return here for AI analysis."
        )

    st.markdown("---")

    # ---- Patient context inputs ----
    st.subheader("Tell Me About Your Current Situation")
    st.caption("This helps the AI micro-adjust the predictions and give personalized recommendations.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Insulin**")
        insulin_taken = st.radio("Injected recently?", ["No", "Yes"], key="insulin_radio", horizontal=True)
        if insulin_taken == "Yes":
            insulin_dose = st.number_input("Dosage (units)", 0.0, 100.0, 0.0, 0.5, key="insulin_dose")
            insulin_time = st.text_input("Time since injection", placeholder="e.g. 30 minutes ago", key="insulin_time")
            insulin_details = f"Injected {insulin_dose} units, {insulin_time}."
        else:
            insulin_details = "No recent insulin injection."

    with col_b:
        st.markdown("**Food Intake**")
        meal_eaten = st.radio("Eaten recently?", ["No", "Yes"], key="meal_radio", horizontal=True)
        if meal_eaten == "Yes":
            meal_desc = st.text_input("What did you eat?", placeholder="e.g. rice, bread, fruit", key="meal_desc")
            meal_time = st.text_input("How long ago?", placeholder="e.g. 20 minutes ago", key="meal_time")
            meal_carbs = st.selectbox("Estimated carbs", ["Low (<30g)", "Medium (30-60g)", "High (>60g)"], key="meal_carbs")
            meal_details = f"Ate: {meal_desc} ({meal_carbs}), {meal_time}."
        else:
            meal_details = "No recent food intake."

    with col_c:
        st.markdown("**Exercise**")
        exercise_done = st.radio("Exercised recently?", ["No", "Yes"], key="exercise_radio", horizontal=True)
        if exercise_done == "Yes":
            exercise_type = st.selectbox("Type", ["Walking", "Running", "Cycling", "Gym / Weights", "Swimming", "Other"], key="exercise_type")
            exercise_dur = st.number_input("Duration (minutes)", 5, 180, 30, 5, key="exercise_dur")
            exercise_time = st.text_input("When?", placeholder="e.g. 15 minutes ago", key="exercise_time")
            exercise_intensity = st.select_slider("Intensity", ["Light", "Moderate", "Vigorous"], key="exercise_intensity")
            exercise_details = f"{exercise_intensity} {exercise_type} for {exercise_dur} min, {exercise_time}."
        else:
            exercise_details = "No recent exercise."

    extra_notes = st.text_area(
        "Additional notes (optional)",
        placeholder="e.g. feeling stressed, took other medication, unusual symptoms...",
        key="extra_notes"
    )

    st.markdown("---")

    # [KYLE] 2026-07-24 -- REWRITTEN to use real multi-turn chat instead of "paste the
    # whole context in again every time". Kyle tested the first version of this and
    # found every follow-up answer re-explained the full trajectory/lifestyle analysis
    # (see PROJECT_NOTES.md) -- root cause was ask_llm()'s hardcoded one-shot prompt
    # template. Fix here uses the new ask_llm_chat() (src/llm_chat.py) which accepts a
    # real conversation history (system/user/assistant turns), same as how ChatGPT-style
    # apps work -- the model naturally treats a follow-up as a follow-up because it can
    # SEE it's a follow-up in the message history, instead of us re-describing
    # everything in one giant blob each time.
    if st.button("Analyze & Get AI Recommendations", type="primary", use_container_width=True):
        glucose_context = ""

        if has_prediction:
            ctx = st.session_state['prediction_context']
            glucose_context += f"""
=== PREDICTION DASHBOARD ===
Current glucose: {ctx['last_glucose']:.1f} mmol/L (measured at {ctx['last_time']})
Predicted +15 min: {ctx['predictions']['15min']:.1f} mmol/L
Predicted +30 min: {ctx['predictions']['30min']:.1f} mmol/L
Predicted +50 min: {ctx['predictions']['50min']:.1f} mmol/L
Trend: {ctx['glucose_trend']}
Historical (last 10): {[f'{v:.1f}' for v in ctx['raw_series'][-10:]]}
Prediction engine: {ctx['mode']}
"""
        else:
            try:
                records = get_glucose_records()
                if records:
                    recent = [float(r[1]) for r in records[-10:]]
                    glucose_context += f"\n=== DATABASE RECORDS ===\nRecent glucose readings: {recent}\n"
            except Exception:
                pass

        glucose_context += f"""
=== PATIENT CONTEXT ===
Insulin: {insulin_details}
Food: {meal_details}
Exercise: {exercise_details}
Additional notes: {extra_notes if extra_notes else 'None'}
"""

        opening_question = f"""Glucose data and context:
{glucose_context}

Based on the glucose data and my current situation above, please provide a thorough analysis:

1. **Glucose Trajectory Analysis** — Explain the current trend and what the 15/30/50 min predictions suggest.
2. **Lifestyle Impact & Micro-Adjustment** — Explain how insulin, food, and exercise are likely to shift the predicted values.
3. **Personalized Recommendations** — Give 3-5 specific, actionable tips for the next hour.
4. **Risk Alerts** — Flag any hypoglycemia risk (below 3.9 mmol/L) or hyperglycemia concern (above 13.9 mmol/L).

Format with clear headings and bullet points. Keep it practical and easy to understand."""

        system_prompt = (
            "You are GlucoGuard AI, a professional diabetes education specialist and glucose management coach. "
            "You analyze CGM data and AI-predicted glucose trajectories to give users practical, science-based insights. "
            "You explain how insulin, food, and exercise interact with blood glucose. "
            "Your recommendations are educational and lifestyle-focused. "
            "The user may ask follow-up questions after your first analysis -- for those, answer ONLY what "
            "they actually asked, briefly and naturally, like a real conversation. Do not repeat your full "
            "earlier analysis unless they specifically ask you to. "
            "You NEVER provide medical diagnoses, prescribe medication, or tell users to change their prescribed insulin regimen. "
            "Always end every reply with a brief reminder that this is educational guidance, not medical advice."
        )

        # This IS the conversation, from the very first turn. Follow-ups just keep
        # appending to this same list -- see the chat_input handler below.
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": opening_question},
        ]

        with st.spinner("GlucoGuard AI is analyzing your glucose trajectory and generating personalized insights..."):
            try:
                answer = ask_llm_chat(messages, max_tokens=1200)
            except Exception as e:
                st.error(f"❌ AI request failed: {e}")
                answer = None

        if answer:
            messages.append({"role": "assistant", "content": answer})
            st.session_state['ai_chat_messages'] = messages

    # ---- Render the conversation so far as real chat bubbles, and let the user keep
    # talking via a chat input box at the bottom of the page. Both persist in
    # session_state so they survive Streamlit's rerun-the-whole-script-on-every-click
    # behaviour (same reason as noted elsewhere in this file). ----
    if 'ai_chat_messages' in st.session_state:
        st.markdown("---")
        st.subheader("AI Health Assistant")

        for msg in st.session_state['ai_chat_messages']:
            if msg["role"] == "system":
                continue  # not part of the visible conversation
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # st.chat_input renders pinned at the bottom, like a real chat app -- this is
        # what teammate described as the "Patient question" box + "Get LLM answer"
        # button, just using Streamlit's built-in chat widget instead of a plain
        # text_input + button pair.
        patient_question = st.chat_input("Ask a follow-up question, e.g. \"Can I eat in the next hour?\"")

        if patient_question:
            st.session_state['ai_chat_messages'].append({"role": "user", "content": patient_question})
            with st.spinner("GlucoGuard AI is answering..."):
                try:
                    followup_answer = ask_llm_chat(st.session_state['ai_chat_messages'], max_tokens=600)
                except Exception as e:
                    st.error(f"❌ AI request failed: {e}")
                    followup_answer = None

            if followup_answer:
                st.session_state['ai_chat_messages'].append({"role": "assistant", "content": followup_answer})
                st.rerun()


# ==================== MAIN APPLICATION ROUTER ====================
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.title(f" Account: {st.session_state.username}")
            st.caption("🟢 Online")
            
            menu_options = ["Dashboard", "Management", "Model Training", "Glucose Prediction", "AI Consultation"]
            selected = option_menu(
                "System Menu",
                menu_options,
                icons=['house', 'people', 'database', 'cpu', 'activity'],
                menu_icon="cast",
                default_index=0,
                styles={"nav-link-selected": {"background-color": "#409eff"}}
            )
            
            st.markdown("---")
            if st.button("Log Out Safely", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_id = None
                st.session_state.display_name = ""
                st.session_state.role = "standard"
                st.rerun()

        if selected == "Dashboard":
            dashboard_page()
        elif selected == "Management":
            management_page()
        elif selected == "Model Training":
            model_training_page() 
        elif selected == "Glucose Prediction":
            blood_sugar_prediction_page()
        elif selected == "AI Consultation":
            ai_consultation_page()
        else:
            st.error("The requested page does not exist.")


if __name__ == "__main__":
    try:
        main()
    except Exception as top_e:
        st.error(f"System encountered a critical runtime error: {str(top_e)}")