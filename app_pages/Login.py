import streamlit as st
from services.auth_client import AuthClient

login_client = AuthClient()

# Custom CSS
st.markdown("""
<style>
    /* Hide sidebar and toggle */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    #MainMenu, footer, header {visibility: hidden;}

    /* Remove default padding */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Text inputs */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #d5d9e5 !important;
        padding: 12px 14px !important;
        font-size: 15px !important;
        background-color: #fff !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }

    /* Hover */
    .stTextInput input:hover {
        border-color: #3949ab !important;
    }

    /* Focus */
    .stTextInput input:focus {
        border-color: #3949ab !important;
        box-shadow: 0 0 0 2px rgba(57,73,171,0.10) !important;
        outline: none !important;
    }

    /* Button */
    .stButton > button {
        color: white !important;
        border: 1px solid #3949ab !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 12px 18px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        background-color: #2d3a8c !important;
        transition: background-color 0.2s ease !important;
        margin-top: 8px !important;
    }

    .stButton > button:hover {
        background-color: #1a237e !important;
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
    _, col, _ = st.columns([1.2, 1, 1.2])

    with col:
        st.markdown(
            "<h2 style='text-align:center; color:#2d3a8c; font-weight:800; font-family:Arial; margin-bottom:26px;'>Student Login</h2>",
            unsafe_allow_html=True
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        if st.button("Login"):
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
