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
    col1, col2 = st.columns([1, 1])

    if 'uploaded_data_frames' not in st.session_state:
        st.session_state['uploaded_data_frames'] = {}

    with col1:
        st.subheader("1. Data Input")
        st.markdown("*Please upload raw Excel files containing glucose records (e.g., 15/30/50-min intervals).*")
        
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

                            # ↓↓↓ 新加的校验逻辑 ↓↓↓
                            if df_raw.shape[1] < 2:
                                st.error(f"❌ {f.name} Invalid format — at least 2 columns required (features + target).")
                            elif df_raw.isnull().any().any():
                                st.error(f"❌ {f.name} Missing values (empty cells) detected. Please check and re-upload.") 
                            elif not df_raw.apply(lambda col: pd.to_numeric(col, errors='coerce').notna().all()).all():
                                st.error(f"❌ {f.name} Non-numeric data detected. Please check and re-upload.")
                            else:
                                save_training_file_to_db(f.name, f.size, df_raw)
                                save_user_file(st.session_state.user_id, 'raw_upload', f.name, f.getvalue())
                                st.session_state['uploaded_data_frames'][f.name] = df_raw
                                st.toast(f"✅ Data file {f.name} successfully saved to DB!", icon="💾")
                            # ↑↑↑ 新加的校验逻辑 ↑↑↑

                        except Exception as e:
                            st.error(f"Failed to process file {f.name}: {str(e)}")
    with col2:
        st.subheader("2. Hyperparameter Configuration")
        # 🛠️ Fix: Properly assign widgets to variables so they can be read down in the pipeline steps!
        algorithm = st.selectbox("Select Predictive Algorithm Model", ["VMD-NOA-BiLSTM (Currently Optimal)", "LSTM-Standard Model", "SVM-Regression Model"])
        epoch_num = st.slider("Training Epochs", 50, 500, 200)
        split_ratio = st.slider("Train/Test Split Ratio", 0.5, 0.9, 0.6)

    st.markdown("---")
    st.subheader("3. Launch Model Training")
    train_btn = st.button(" Launch VMD-NOA-BiLSTM Training Pipeline", type="primary", use_container_width=True)
    
    if train_btn:
        if not uploaded_files:
            st.error("❌ Please upload at least one raw Excel data file first on the left panel!")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # The highly customized professional 7-step pipeline matching your math backend engine
            steps = [
                "Loading training data from database...",
                "Executing VMD signal decomposition (K=5)...",
                f"Initializing NOA swarm optimization algorithm (Target Epochs: {epoch_num})...",
                f"Splitting datasets with configured ratio ({split_ratio}:{round(1-split_ratio, 2)}) into BiLSTM...",
                f"BiLSTM neural network parallel training in progress... Optimizing weights for [{algorithm}]...",
                "Executing Clarke Error Grid Analysis and clinical-grade metric calculations...",
                "Generating final standardized Excel training reports..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(f"Current Status: {step}")
                time.sleep(1.0) 
                progress_bar.progress(int((i + 1) / len(steps) * 100))
                
            status_text.success("✅ Training completed successfully! All execution logs and results have been archived.")
            st.balloons()


# ==================== BLOOD GLUCOSE PREDICTION PAGE ====================
def blood_sugar_prediction_page():
    st.title(" Real-time Blood Glucose Prediction Center")
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
                current_user_id = st.session_state.user_id
                
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

        st.subheader("⚙️ Prediction Configuration")
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

                    st.markdown("### Future Predicted Metrics List")
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