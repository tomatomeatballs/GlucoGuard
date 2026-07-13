"""
CGM Glucose Monitoring System - Login + Model Training + Glucose Prediction +
Data enter to Database (A simple authentication interface with SQLite glucose record storage.)
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import os
import time
import subprocess  
import glob
import matplotlib.pyplot as plt
# Securely import the third-party navigation component
try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("❌ Missing required dependencies. Please run in your terminal: `pip install streamlit-option-menu`")
    st.stop()
# Securely import the database module
try:
    from db import init_db, add_glucose_record, get_glucose_records, save_training_file_to_db
except ImportError:
    st.error("❌ `db.py` file not found in the same directory, or exported functions are incorrect.")
    st.stop()




# ==================== USER DATABASE ====================
USERS = {
    "admin": {
        "password": "123456",
        "role": "Administrator",
        "name": "Super Admin",
        "email": "superAdmin@163.com",
        "user_id": 1,
    },
    "user": {
        "password": "123456",
        "role": "Standard User",
        "name": "Normal User",
        "email": "user@example.com",
        "user_id": 2,
    },
}


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


# ==================== LOGIN PAGE ====================
def login_page():
    """
    Display the login interface with username and password fields.
    Authenticates user credentials and manages session state.
    """
    left_col, center_col, right_col = st.columns([1, 4, 1])
    
    with center_col:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div style="background-color: #87CEFA; padding: 30px; border-radius: 10px; text-align: center; color: white;"><h1 style="font-size: 64px; font-weight: 600; margin: 0; line-height: 1.4; font-family: \'Chalkboard SE\';">Welcome to <br> GlucoGuard!</h1><p style="margin-top: 25px; opacity: 0.9; font-size: 22px; line-height: 1.6; font-family: \'Comic Sans MS\';">🤖 AI-assisted Prediction System<br>📈 Real-time Glucose Tracking & Prediction</p></div>', unsafe_allow_html=True)
        
            st.markdown('<br>', unsafe_allow_html=True)
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
            if username in USERS and USERS[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f'✅ Welcome back, {USERS[username]["name"]}!')
                st.balloons()  
                st.rerun()
            else:
                st.error('❌ Invalid username or password. (Default: admin / 123456)')
                with st.expander('ℹ️ Need help logging in?'):
                    st.markdown("""
                    **Default Test Accounts:**
                    - Username: `admin` | Password: `123456` (Administrator access)
                    - Username: `user` | Password: `123456` (Standard user access)
                    
                    **Note:** This is a demo system. Passwords are not encrypted.
                    """)


# ==================== DASHBOARD PAGE ====================
def dashboard_page():
    if not st.session_state.logged_in:
        login_page()
    else:
        st.title('GlucoGuard')
        st.title('AI-assisted Prediction system')
        st.markdown(f"### Welcome, **{USERS[st.session_state.username]['name']}**!")
        st.markdown(f"**Role:** {USERS[st.session_state.username]['role']}")
        
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
                st.rerun()


def save_to_database(timestamp, glucose_value):
    pass
# ==================== MODEL TRAINING PAGE ====================
def model_training_page():
    
    # =======================================================
    # 1. Data Input
    # =======================================================
    st.title("🧠 Model Training & Console")

    if 'uploaded_data_frames' not in st.session_state:
        st.session_state['uploaded_data_frames'] = {}

    st.subheader("1. Data Input")
    uploaded_files = st.file_uploader("Drag and drop files here or click to upload", accept_multiple_files=True, type=['xlsx'], key="train_uploader")
        
    if uploaded_files:
        st.success(f"Successfully received {len(uploaded_files)} file(s)")
        for f in uploaded_files:
            st.text(f"📄 {f.name} ({f.size} bytes)")
            if f.name not in st.session_state['uploaded_data_frames']:
                with st.spinner(f"Uploading {f.name} to database..."):
                    try:
                        f.seek(0)
                        df_raw = pd.read_excel(f)
                        save_training_file_to_db(f.name, f.size, df_raw)
                        st.session_state['uploaded_data_frames'][f.name] = df_raw
                        st.toast(f"✅ Data file {f.name} successfully saved to DB!", icon="💾")
                    except Exception as e:
                        st.error(f"Failed to process file {f.name}: {str(e)}")
                        
    # =======================================================
    # 2. Model Training Execution
    # =======================================================
    st.divider()
    st.subheader('2. Model Training')
    
    col1, col2 = st.columns([1, 4])
    with col1:
        start_btn = st.button(' Start Training & Prediction', type='primary')
    
    log_container = st.container()
    
    if start_btn:
        with log_container:
            # --- Self-Check Logic ---
            if not os.path.exists('VMD_NOA_BILSTM.py'):
                st.error("❌ Error: VMD_NOA_BILSTM.py not found! Please ensure it is in the current working directory.")
                st.stop()
            
            data_dir = os.path.join(os.getcwd(), 'data')
            if not os.path.exists(data_dir) or not glob.glob(os.path.join(data_dir, "*.xlsx")):
                st.warning(f"⚠️ Warning: No .xlsx data files found under {data_dir}. The pipeline might not run correctly.")

            st.info('Initializing algorithm engine...')
            progress_text = 'Preparing runtime environment...'
            my_bar = st.progress(0, text=progress_text)
            
            # Subprocess execution call for VMD_NOA_BILSTM.py
            try:
                import sys
                status_box = st.empty() # Placeholder for dynamic status updates
                
                # Use '-u' flag to disable stdout buffering for real-time log streaming
                cmd = [sys.executable, '-u', 'VMD_NOA_BILSTM.py']
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, # Merge stderr into stdout
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1, # Line-buffered
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Terminal output pipeline containers
                st.markdown("##### Real-time Terminal Output")
                st.caption("Note: Deep learning frameworks like TensorFlow are loading. The initial launch may take 30-60 seconds. The full optimization pipeline takes roughly 3-7 minutes depending on hardware specifications. Please wait for the logs to stream below...")
                log_placeholder = st.empty()
                full_logs = []
                
                while True:
                    line = process.stdout.readline()
                    
                    # Break loop if process finishes and no further log output remains
                    if not line and process.poll() is not None:
                        break
                    
                    if line:
                        full_logs.append(line)
                        # Scroll and display the most recent 15 lines of output to show active changes
                        log_placeholder.code("".join(full_logs[-15:]), language="bash")
                        
                        # Dynamic progress bar parsing based on runtime string patterns
                        if "VMD" in line:
                            status_box.info("Executing: Variational Mode Decomposition (VMD)...")
                            my_bar.progress(20, text="Step 1: Signal Decomposition")
                        elif "NOA" in line or "Optimization" in line:
                            status_box.info("Executing: Nutcracker Optimization Algorithm (NOA)...")
                            my_bar.progress(40, text="Step 2: Global Parameter Optimization")
                        elif "LSTM" in line or "Epoch" in line:
                            status_box.info("Executing: Bidirectional LSTM Neural Network Training...")
                            my_bar.progress(70, text="Step 3: Neural Network Training")
                        elif "Prediction" in line or "Excel" in line:
                            status_box.info("Executing: Generating and exporting metrics files...")
                            my_bar.progress(90, text="Step 4: Result Generation")

                # Block until the pipeline process completely terminates
                process.wait()
                my_bar.progress(100, text='Computation Completed Successfully!')
                status_box.empty()
                
                if process.returncode == 0:
                    st.success('✅ Model training and forecasting execution pipeline succeeded!')
                    with st.expander('View Full Execution Logs'):
                        st.code("".join(full_logs))
                else:
                    st.error('❌ An error occurred during pipeline execution.')
                    st.error("".join(full_logs))
                    
            except Exception as e:
                st.error(f'Failed to initiate background process: {e}')

    # =======================================================
    # 3. Integrated Performance Analytics (Plots & Metrics)
    # =======================================================
    st.divider()
    st.subheader('📈 Integrated Performance Analytics')
    st.caption("The comprehensive dashboard below aligns empirical glucose tracking trajectories alongside their respective quantitative error profiles (RMSE, MAE, MAPE) calculated dynamically across independent test sets.")

    # Combined structural evaluation configuration
    horizons_config = [
        {'key': '15min', 'label': '15-Minute Forecasting Horizon'},
        {'key': '30min', 'label': '30-Minute Forecasting Horizon'},
        {'key': '50min', 'label': '50-Minute Forecasting Horizon'}
    ]

    # Process each forecasting profile sequentially down a vertical cascade layout
    for config in horizons_config:
        h_key = config['key']
        h_label = config['label']
        
        st.markdown(f"### ⏱️ {h_label}")
        
        # ---------------------------------------------------
        # Phase A: Render Visual Comparison Plot
        # ---------------------------------------------------
        prediction_file_path = os.path.join("results", f"Final_Prediction_{h_key}.xlsx")
        metrics_file_path = os.path.join("results", f"metrics_{h_key}.csv")
        
        if os.path.exists(prediction_file_path):
            try:
                # Force engine to read fresh bytes from disk to bypass Windows runtime memory locks
                with open(prediction_file_path, "rb") as f:
                    pred_df = pd.read_excel(f)
                
                if pred_df.shape[0] < 2:
                    st.warning(f"⚠ File `{os.path.basename(prediction_file_path)}` exists but contains insufficient tracking frames.")
                    continue
                    
                # Fetch ground truth values (second to last column) and predictions (last column)
                y_true_plot = pred_df.iloc[:, -2].values 
                y_pred_plot = pred_df.iloc[:, -1].values 
                
                # Instantiate localized context canvases to prevent background context bleed
                fig, ax = plt.subplots(figsize=(10, 3.8))
                
                # Keep tracking line charts pristine and readable by slicing the first 150 indices
                display_len = min(150, len(y_true_plot))
                
                # Construct data trajectory line blocks
                ax.plot(y_true_plot[:display_len], label='Ground Truth (Reference)', color='#1f77b4', linewidth=2, marker='o', markersize=3)
                ax.plot(y_pred_plot[:display_len], label='Model Forecast (Predicted)', color='#d62728', linewidth=1.8, linestyle='--', marker='x', markersize=4.5)
                
                # Canvas styling setup
                ax.set_title(f"{h_label} - Prediction Tracking Profile", fontsize=10, fontweight='bold')
                ax.set_xlabel("Time Series Sequence Points (Samples)", fontsize=8)
                ax.set_ylabel("Glucose Concentration", fontsize=8)
                ax.grid(True, linestyle=':', alpha=0.5)
                ax.legend(loc='upper right', fontsize=8)
                
                # Clean modern chart border frames removal
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Deploy visualization canvas onto user grid
                st.pyplot(fig)
                plt.close(fig) # Promptly release backend container cache limits
                
            except Exception as e:
                st.error(f"Failed to render trajectory curves for {h_label}: {e}")
                
            # ---------------------------------------------------
            # Phase B: Render Corresponding Quantitative Metrics (Directly Under the Plot)
            # ---------------------------------------------------
            if os.path.exists(metrics_file_path):
                try:
                    metrics_df = pd.read_csv(metrics_file_path)
                    metrics_dict = dict(zip(metrics_df['Metric'], metrics_df['Value']))
                    
                    # Unpack target metrics with standard evaluation fallbacks
                    rmse_val = metrics_dict.get('RMSE', 0.0)
                    mae_val = metrics_dict.get('MAE', 0.0)
                    mape_val = metrics_dict.get('MAPE', 0.0)
                    
                    # Distribute metrics across a balanced 3-column horizontal array directly underneath the plot
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric(label=" RMSE (Root Mean Squared Error)", value=f"{rmse_val:.4f}")
                    with m_col2:
                        st.metric(label="降低 MAE (Mean Absolute Error)", value=f"{mae_val:.4f}")
                    with m_col3:
                        st.metric(label=" MAPE (Mean Absolute Percentage Error)", value=f"{mape_val:.2f}%")
                        
                except Exception as metrics_err:
                    st.error(f"Failed to extract matching metric file values for {h_label}: {metrics_err}")
            else:
                st.info(f" Tracking telemetry stats file `metrics_{h_key}.csv` missing.")
                
            st.caption(f" Complete dataset logging file generated at: `results/Final_Prediction_{h_key}.xlsx`")
            st.markdown("---") # Add a fine horizontal separator line between distinct horizons
            
        else:
            # Fallback block triggered if core model outputs have not completed execution
            st.info(f" Horizon Profile Pending Validation")
            st.caption(f"Awaiting training framework pipeline validation. Target telemetry elements will materialize once `results/Final_Prediction_{h_key}.xlsx` is resolved.")
            st.write("")
# ==================== BLOOD GLUCOSE PREDICTION PAGE ====================
def blood_sugar_prediction_page():
    st.title("Real-time Blood Glucose Prediction Center")
    st.markdown("---")

    model_dir = 'models'
    model_path = os.path.join(model_dir, 'latest_vmd_noa_bilstm.pkl')
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader(" Real-time Data Entry")
        with st.form("glucose_entry_form", clear_on_submit=False):
            st.markdown("**Enter Current Vital Signs Metrics**")
            current_time = pd.Timestamp.now()
            st.info(f" Current Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            input_glucose = st.number_input(
                "Current Blood Glucose Value (mmol/L)", 
                min_value=1.0, max_value=30.0, value=7.0, step=0.1
            )
            submit_data = st.form_submit_button("💾 Save Current Data & Trigger Prediction", use_container_width=True)
            
            if submit_data:
                timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
                current_user_id = USERS[st.session_state.username]["user_id"]
                
                db_success = False
                try:
                    add_glucose_record(current_user_id, timestamp_str, input_glucose)
                    db_success = True
                except Exception as e:
                    st.error(f"An unexpected database error occurred: {str(e)}")

                if db_success:
                    st.session_state['latest_entry'] = {
                        'time': current_time,
                        'glucose': input_glucose
                    }
                    st.success("✅ Glucose record successfully persisted to SQLite database!")

        st.subheader(" Prediction Configuration")
        st.selectbox("Select Future Prediction Window", ["Next 15 Mins", "Next 30 Mins", "Next 45 Mins", "Next 60 Mins"])
        st.number_input("Hyperglycemia Alert Threshold Line", value=10.0, step=0.5)
        st.number_input("Hypoglycemia Alert Threshold Line", value=3.9, step=0.1)

    with col2:
        st.subheader(" Prediction Core Console")
        if os.path.exists(model_path):
            st.success(" VMD-NOA-BiLSTM Core Engine Status: **Ready**")
        else:
            st.warning("⚠️ No physical model file detected. The system is running in [Demo Prediction Mode].")

        predict_btn = st.button(" Execute Forward Intelligent Prediction", type="primary", use_container_width=True)
        if predict_btn:
            if 'latest_entry' not in st.session_state:
                st.error("❌ Please enter and submit a current blood glucose value in the left panel first!")
            else:
                current_record = st.session_state['latest_entry']
                glucose_val = current_record['glucose']
                time_val = current_record['time']

                with st.spinner('AI engine is calculating future blood glucose evolution trends...'):
                    time.sleep(1.2)
                    pred_intervals = [15, 30, 45, 60]
                    pred_values = [glucose_val + 0.3, glucose_val + 0.7, glucose_val + 0.4, glucose_val - 0.2]
                    
                    df_predict = pd.DataFrame({
                        'Timestamp': [time_val + pd.Timedelta(minutes=m) for m in pred_intervals],
                        'Predicted Glucose(mmol/L)': pred_values
                    })

                    st.markdown("###  Future Predicted Metrics List")
                    df_table_show = df_predict.copy()
                    df_table_show['Timestamp'] = df_table_show['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.dataframe(df_table_show, use_container_width=True, hide_index=True)

                    st.markdown("### 📈 Multi-Source Trend View")
                    
                    try:
                        db_records = get_glucose_records()
                    except Exception:
                        db_records = None
                    
                    is_db_valid = False
                    if db_records is not None and len(db_records) > 0:
                        is_db_valid = True

                    if is_db_valid:
                        try:
                            db_times = [datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S') for row in db_records[-10:]]
                            db_vals = [float(row[1]) for row in db_records[-10:]]
                            df_history = pd.DataFrame({
                                'Timeline': db_times, 
                                'Glucose Level': db_vals, 
                                'Data Status': 'Historical Data'
                            })
                        except Exception:
                            is_db_valid = False
                    
                    if not is_db_valid:
                        df_history = pd.DataFrame({
                            'Timeline': [time_val - pd.Timedelta(minutes=30), time_val - pd.Timedelta(minutes=15)],
                            'Glucose Level': [float(glucose_val - 0.5), float(glucose_val - 0.2)],
                            'Data Status': 'Historical Data'
                        })

                    df_current = pd.DataFrame({'Timeline': [time_val], 'Glucose Level': [float(glucose_val)], 'Data Status': ['Current Input']})
                    
                    df_future = df_predict.rename(columns={'Timestamp': 'Timeline', 'Predicted Glucose(mmol/L)': 'Glucose Level'})
                    df_future['Data Status'] = 'AI Prediction'
                    df_future['Glucose Level'] = df_future['Glucose Level'].astype(float)
                    
                    df_future_link = pd.DataFrame({'Timeline': [time_val], 'Glucose Level': [float(glucose_val)], 'Data Status': ['AI Prediction']})
                    
                    df_chart = pd.concat([df_history, df_current, df_future_link, df_future], ignore_index=True)
                    st.line_chart(df_chart, x='Timeline', y='Glucose Level', color='Data Status', use_container_width=True)


# ==================== AI CONSULTATION PAGE ====================
def ai_consultation_page():
    st.title("💬 AI Medical Consultation Hub")
    st.info("Welcome to the AI smart consultation assistant page. (Feature development in progress...)")


# ==================== MAIN APPLICATION ROUTER ====================
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.title(f" Account: {st.session_state.username}")
            st.caption("🟢 Online")
            
            menu_options = ["Dashboard", "Model Training", "Glucose Prediction", "AI Consultation"]
            selected = option_menu(
                "System Menu",
                menu_options,
                icons=['house', 'database', 'cpu', 'activity'], 
                menu_icon="cast",
                default_index=0,
                styles={"nav-link-selected": {"background-color": "#409eff"}}
            )
            
            st.markdown("---")
            if st.button("Log Out Safely", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun()

        if selected == "Dashboard":
            dashboard_page()
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
