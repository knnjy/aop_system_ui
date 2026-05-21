import streamlit as st

from pages import Home
from services.auth_client import AuthClient

# Page config - MUST be first
st.set_page_config(page_title="Student Portal Login", layout="wide", initial_sidebar_state="collapsed")
login_client = AuthClient()
st.markdown("""
    <style>
        /* Hide sidebar and toggle */
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Remove ALL default padding */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* Labels */
        .stTextInput label {
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* Input fields */
        .stTextInput > div > div > input {
            border-radius: 10px !important;
            border:1px solid #d5d9e5 !important;
            padding: 12px 14px !important;
            font-size: 15px !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #3949ab !important;
            box-shadow: 0 0 0 2px rgba(57,73,171,0.10) !important;
        }

        /* Login button */
        .stButton > button {
            background-color: #2d3a8c !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding-align: center !important;
            width: 100% !important;
            padding: 12px 18px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            letter-spacing: 0.4px !important;
            cursor: pointer !important;
            transition: background 0.2s ease !important;
            margin-top: 8px !important;
        }

        .stButton > button:hover {
            background-color: #1a237e !important;
        }

        /* White card using column background */
        [data-testid="column"]:nth-child(2) {
            background-color: #ffffff !important;
            border-radius: 20px !important;
            box-shadow: 0 6px 30px rgba(0, 0, 0, 0.08) !important;
            padding: 50px 40px 40px 40px !important;
            margin-top: 80px !important;
        }

        /* Forgot password link */
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
        # Title inside the card
        st.markdown(
            "<h2 style='text-align:center; color:#2d3a8c; font-weight:800; font-family:Arial; margin-bottom:26px;'>Student Portal Login</h2>",
            unsafe_allow_html=True
        )

        # Inputs inside the card
        username = st.text_input("Username", placeholder="")
        password = st.text_input("Password", type="password", placeholder="")

        # Button inside the card
        if st.button("Login"):
            response = login_client.login(username, password)
            if response.get("success"):
                st.session_state.logged_in = True
                st.session_state.role = response.get("role")
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                Home.show()

            else:
                st.error("Invalid username or password.")

        # Forgot password inside the card
        st.markdown(
            "<div class='forgot-link'><a href='#'>Forgot password?</a></div>",
            unsafe_allow_html=True
        )

show_login()