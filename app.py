"""
CGM Glucose Monitoring System - Login Module
A simple authentication interface for the glucose monitoring system
"""

import streamlit as st

# ==================== USER DATABASE ====================
# Simulated user database with credentials and user information
USERS = {
    'admin': {
        'password': '123456', 
        'role': 'Administrator', 
        'name': 'Super Admin', 
        'email': 'superAdmin@163.com'
    },
    'user': {
        'password': '123456', 
        'role': 'Standard User', 
        'name': 'Normal User', 
        'email': 'user@example.com'
    }
}

# ==================== SESSION STATE INITIALIZATION ====================
# Initialize session state variables to maintain login status across page refreshes
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'username' not in st.session_state:
    st.session_state.username = ''

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title='CGM Glucose Monitoring System',
    page_icon='🩸',
    layout='centered',
    initial_sidebar_state='collapsed'
)

# ==================== LOGIN PAGE ====================
def login_page():
    """
    Display the login interface with username and password fields.
    Authenticates user credentials and manages session state.
    """
    
    # Create three columns for centering the login box
    # The middle column takes 2/3 width, side columns take 1/3 each
    left_col, center_col, right_col = st.columns([1, 2, 1])
    
    with center_col:
        # Add spacing for vertical centering
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        
        # Welcome card with system title
        st.markdown('''
        <div style='background-color: #2c3e50; padding: 30px; border-radius: 10px; text-align: center; color: white;'>
            <h1>Welcome to CGM Glucose Monitoring System</h1>
            <p style='margin-top: 10px; opacity: 0.9;'>Real-time Glucose Tracking & Prediction</p >
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Username input field with placeholder
        username = st.text_input(
            'Username', 
            placeholder='Enter your username (e.g., admin)',
            key='login_username'
        )
        
        # Password input field with password masking
        password = st.text_input(
            'Password', 
            type='password', 
            placeholder='Enter your password',
            key='login_password'
        )
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Login button - full width for better UX
        if st.button('🔐 Login', use_container_width=True, type='primary'):
            # Authentication logic
            if username in USERS and USERS[username]['password'] == password:
                # Successful login - update session state
                st.session_state.logged_in = True
                st.session_state.username = username
                
                # Display success message
                st.success(f'✅ Welcome back, {USERS[username]["name"]}!')
                st.balloons()  # Celebration animation
                
                # Rerun the app to switch to main interface
                st.rerun()
            else:
                # Failed login - show error message with hint
                st.error('❌ Invalid username or password. (Default: admin / 123456)')
                
                # Provide helpful hint for first-time users
                with st.expander('ℹ️ Need help logging in?'):
                    st.markdown("""
                    **Default Test Accounts:**
                    - Username: `admin` | Password: `123456` (Administrator access)
                    - Username: `user` | Password: `123456` (Standard user access)
                    
                    **Note:** This is a demo system. Passwords are not encrypted.
                    """)

# ==================== MAIN APPLICATION ====================
def main():
    """
    Main application entry point.
    Routes between login page and main app based on authentication status.
    """
    
    # Show login page if not authenticated
    if not st.session_state.logged_in:
        login_page()
    else:
        # Display welcome message for authenticated users
        st.title('🏥 CGM Glucose Monitoring System')
        st.markdown(f"### Welcome, **{USERS[st.session_state.username]['name']}**!")
        st.markdown(f"**Role:** {USERS[st.session_state.username]['role']}")
        
        st.divider()
        
        # Main application interface
        st.info("""
        ✅ You have successfully logged into the CGM Glucose Monitoring System.
        
        **Features available in full version:**
        - 📊 Real-time glucose dashboard
        - 👥 User management (Admin only)
        - 🤖 AI-powered glucose prediction
        - 📈 Interactive data visualization
        - 📄 Health report generation
        """)
        
        # Logout button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button('🚪 Logout', use_container_width=True):
                # Clear session state on logout
                st.session_state.logged_in = False
                st.session_state.username = ''
                st.rerun()

# ==================== ENTRY POINT ====================
if __name__ == '__main__':
    main()