import streamlit as st
from services.auth_client import AuthClient

login_client = AuthClient()
# st.set_page_config(layout="centered")

# Custom CSS
st.markdown("""
<style>
    /* Hide sidebar and toggle */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    #MainMenu, footer, header {visibility: hidden;}

    /*container*/
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        background-color: #ffffff !important;
    }

    /* Login container */
    .login-container {
        max-width: 350px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    /* Forgot password */
    .forgot-link {
        text-align: center;
        margin-top: 16px;
    }

    .forgot-link a {
        color: #3a5bd9;
        text-decoration: none;
        font-size: 14px;
    }

    .forgot-link a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)


def show_login():
    st.markdown(
        "<div class='login-container'><h2 style='text-align:center; color:#2d3a8c; font-weight:800; font-family:Arial; margin-bottom:26px;'>Student Portal Login</h2>",
        unsafe_allow_html=True
    )
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login", use_container_width=True):
        response = login_client.login(username, password)
        print(response)
        if response:
            st.session_state.logged_in = True
            st.session_state.role = response.get("role")
            st.session_state.username = username
            st.session_state.user_data = response.get("user_data", {})
            st.session_state.current_page = "homepage" 
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    # Forgot password
    st.markdown(
        "<div class='forgot-link'><a href='#'>Forgot password?</a></div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

