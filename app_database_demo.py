import streamlit as st
from datetime import datetime
import pandas as pd

from db import init_db, add_glucose_record, get_glucose_records


st.set_page_config(
    page_title="GlucoGuard Database Demo",
    layout="wide"
)

init_db()

st.title("GlucoGuard Database MVP")

st.write(
    "This page demonstrates a basic database flow: "
    "add glucose records, save them into SQLite, read them back, and visualize the trend."
)

st.subheader("Add Glucose Record")

with st.form("add_glucose_form"):
    glucose = st.number_input(
        "Glucose value (mmol/L)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.1
    )

    record_date = st.date_input(
        "Date",
        value=datetime.now().date()
    )

    record_time = st.time_input(
        "Time",
        value=datetime.now().time()
    )

    source = st.selectbox(
        "Source",
        ["manual", "historical", "realtime"]
    )

    notes = st.text_input("Notes")

    submitted = st.form_submit_button("Save Record")

    if submitted:
        combined_datetime = datetime.combine(record_date, record_time)

        add_glucose_record(
            user_id=1,
            timestamp=combined_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            glucose=glucose,
            source=source,
            notes=notes
        )

        st.success("Glucose record saved to database!")


st.subheader("Glucose History")

df = get_glucose_records(user_id=1)

if df.empty:
    st.info("No glucose records yet.")
else:
    st.dataframe(df, use_container_width=True)

    chart_df = df.copy()
 chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], format="mixed")
    chart_df = chart_df.sort_values("timestamp")
    chart_df = chart_df.set_index("timestamp")

    st.subheader("Glucose Trend")
    st.line_chart(chart_df["glucose"])

    latest_glucose = float(df.iloc[-1]["glucose"])

    st.subheader("Latest Risk Level")

    if latest_glucose < 3.9:
        st.error(f"Low glucose risk: {latest_glucose} mmol/L")
    elif latest_glucose > 7.8:
        st.warning(f"High glucose level: {latest_glucose} mmol/L")
    else:
        st.success(f"Within target range: {latest_glucose} mmol/L")