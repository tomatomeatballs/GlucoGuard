# GlucoGuard / CGM Glucose Monitor - Milestone 1 Login Demo

## Project Overview

GlucoGuard is a Continuous Glucose Monitoring (CGM) support system designed to help users monitor glucose-related data and eventually receive AI-assisted glucose prediction and health reports.

For Orbital Milestone 1, this repository contains a basic technical proof of concept: a Streamlit-based login module for the CGM Glucose Monitoring System.

This prototype demonstrates the initial authentication flow of the system. It is not the full final version of GlucoGuard.

---

## Milestone 1 Scope

For Milestone 1, we implemented a simple login interface as a proof of concept.

The current prototype demonstrates:

- Username and password login
- Simulated user database
- Session management using Streamlit session state
- Role-based welcome message
- Admin and standard user test accounts
- Logout functionality
- Basic preview of future system features

This version does not yet include the full glucose prediction model, real database integration, or complete dashboard functions.

---

## Features Implemented

### 1. Login Page

Users can enter a username and password to access the system.

### 2. Simulated User Database

The prototype includes two test accounts:

| Username | Password | Role |
|---|---|---|
| admin | 123456 | Administrator |
| user | 123456 | Standard User |

### 3. Session Management

The app uses `st.session_state` to keep track of whether the user is logged in.

### 4. Role-Based Welcome Page

After successful login, the app displays the user's name and role.

### 5. Logout Function

Users can click the logout button to clear the session and return to the login page.

---

## Technology Stack

- Python
- Streamlit
- GitHub

Future versions may include:

- AI glucose prediction model integration
- Database support
- User glucose history storage
- Interactive dashboard
- Health report generation

---

## Requirements

Please make sure Python 3.8 or above is installed.

Install Streamlit using:

```bash
python3 -m pip install streamlit
```

If `python3` is not available on your system, try:

```bash
pip install streamlit
```

---

## How to Run

Clone or download this repository.

Open a terminal in the project folder and run:

```bash
python3 -m streamlit run app.py
```

If the above command does not work, try:

```bash
streamlit run app.py
```

The app should automatically open in your browser.

If it does not open automatically, go to:

```text
http://localhost:8501
```

---

## Login Credentials

Use one of the following test accounts:

### Admin Account

```text
Username: admin
Password: 123456
```

### Standard User Account

```text
Username: user
Password: 123456
```

---

## Project Structure

```text
GlucoGuard-M1-Login-Demo/
├── app.py              # Main Streamlit application
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
└── project_log.md      # Project progress log
```

---

## Current Limitations

This is a Milestone 1 prototype only.

Current limitations include:

- User credentials are stored directly in the code for demonstration purposes.
- Passwords are not encrypted.
- There is no real database connection yet.
- The AI glucose prediction model is not integrated yet.
- The dashboard and health report functions are shown only as future feature previews.
- This prototype should not be used for real medical decision-making.

---

## Future Development Plan

In later milestones, we plan to extend the system with:

1. Real user database integration
2. Secure authentication
3. Glucose data input and storage
4. Interactive glucose trend visualization
5. AI-powered glucose prediction
6. Health report generation
7. Improved user interface
8. Deployment for adviser and user testing

---

## Milestone 1 Proof of Concept

This prototype satisfies the Milestone 1 technical proof of concept by demonstrating an integrated login flow in a working web application.

The app can be run locally and shows the basic structure of the future CGM Glucose Monitoring System.

---

## Team Notes

This prototype is part of our Orbital 2026 project, GlucoGuard.

The current focus is to establish the basic system structure and authentication flow before integrating the full prediction model and data visualization modules in future milestones.