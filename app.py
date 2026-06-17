"""
CGM Glucose Monitoring System - Login + Database Dashboard
A simple authentication interface with SQLite glucose record storage.
"""

import streamlit as st
from datetime import datetime
import pandas as pd

from db import init_db, add_glucose_record, get_glucose_records


# ==================== USER DATABASE ====================
# Simulated user database with credentials and user information
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
        "user_id": 1,
    },
}


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="CGM Glucose Monitoring System",
    page_icon="🩸",
    layout="wide",##！！
    initial_sidebar_state="expanded",
)


# ==================== SESSION STATE INITIALIZATION ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ==================== DATABASE INITIALIZATION ====================
init_db()


# ==================== LOGIN PAGE ====================
def login_page():
    """
    Display the login interface with username and password fields.
    Authenticates user credentials and manages session state.
    """

    left_col, center_col, right_col = st.columns([1, 2, 1])

    with center_col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style='background-color: #2c3e50; padding: 30px; border-radius: 10px; text-align: center; color: white;'>
                <h1>Welcome to CGM Glucose Monitoring System</h1>
                <p style='margin-top: 10px; opacity: 0.9;'>Real-time Glucose Tracking & Prediction</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input(
            "Username",
            placeholder="Enter your username (e.g., admin)",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔐 Login", use_container_width=True, type="primary"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(f"✅ Welcome back, {USERS[username]['name']}!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Invalid username or password. (Default: admin / 123456)")

                with st.expander("ℹ️ Need help logging in?"):
                    st.markdown(
                        """
                        **Default Test Accounts:**
                        - Username: `admin` | Password: `123456` (Administrator access)
                        - Username: `user` | Password: `123456` (Standard user access)

                        **Note:** This is a demo system. Passwords are not encrypted.
                        """
                    )


# ==================== DASHBOARD ====================
def dashboard_page():
    """
    Main dashboard after login.
    Includes glucose record input, SQLite storage, history table, trend chart, and risk level.
    """

    current_username = st.session_state.username
    current_user = USERS[current_username]
    current_user_id = current_user["user_id"]

    st.sidebar.title("🩸 GlucoGuard")
    st.sidebar.markdown(f"**User:** {current_user['name']}")
    st.sidebar.markdown(f"**Role:** {current_user['role']}")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("🏥 CGM Glucose Monitoring System")
    st.markdown(f"### Welcome, **{current_user['name']}**!")
    st.markdown(f"**Role:** {current_user['role']}")

    st.divider()

    st.info(
        """
        This dashboard demonstrates the current database MVP:
        glucose records can be added through Streamlit, saved to SQLite,
        read back from the database, displayed as history, and visualized as a trend chart.
        """
    )

    # ==================== ADD GLUCOSE RECORD ====================
    st.subheader("➕ Add Glucose Record")

    with st.form("add_glucose_form"):
        glucose = st.number_input(
            "Glucose value (mmol/L)",
            min_value=0.0,
            max_value=30.0,
            value=6.0,
            step=0.1,
        )

        record_date = st.date_input("Date", value=datetime.now().date())

        record_time = st.time_input("Time", value=datetime.now().time())

        source = st.selectbox("Source", ["manual", "historical", "realtime"])

        notes = st.text_input("Notes")

        submitted = st.form_submit_button("Save Record")

        if submitted:
            combined_datetime = datetime.combine(record_date, record_time)

            add_glucose_record(
                user_id=current_user_id,
                timestamp=combined_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                glucose=glucose,
                source=source,
                notes=notes,
            )

            st.success("Glucose record saved to database!")

    st.divider()

    # ==================== GLUCOSE HISTORY ====================
    st.subheader("📋 Glucose History")

    df = get_glucose_records(user_id=current_user_id)

    if df.empty:
        st.info("No glucose records yet.")
        return

    st.dataframe(df, use_container_width=True)

    # ==================== GLUCOSE TREND ====================
    st.subheader("📈 Glucose Trend")

    chart_df = df.copy()

    try:
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], format="mixed")
    except TypeError:
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], errors="coerce")

    chart_df = chart_df.dropna(subset=["timestamp"])
    chart_df = chart_df.sort_values("timestamp")
    chart_df = chart_df.set_index("timestamp")

    st.line_chart(chart_df["glucose"])

    # ==================== LATEST RISK LEVEL ====================
    st.subheader("⚠️ Latest Risk Level")

    latest_glucose = float(df.iloc[-1]["glucose"])

    if latest_glucose < 3.9:
        st.error(f"Low glucose risk: {latest_glucose} mmol/L")
    elif latest_glucose > 7.8:
        st.warning(f"High glucose level: {latest_glucose} mmol/L")
    else:
        st.success(f"Within target range: {latest_glucose} mmol/L")


# ==================== MAIN APPLICATION ====================
def main():
    """
    Main application entry point.
    Routes between login page and dashboard based on authentication status.
    """

    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    main()