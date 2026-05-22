import streamlit as st

from pages import Home
from services.auth_client import AuthClient

login_client = AuthClient()
st.markdown("""
    <style>
        /* Hide sidebar and toggle */
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        #MainMenu, footer, header {visibility: hidden;}

        /* Background - full screen */
        .stApp {
            background-color: #e8eaf2;
        }

        /* Remove ALL default padding */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* Labels */
        .stTextInput label {
            font-weight: 600 !important;
            color: #333 !important;
            font-size: 14px !important;
        }

        /* Input fields */
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1.5px solid #d0d5e8 !important;
            padding: 12px 14px !important;
            font-size: 15px !important;
            background: #fff !important;
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
        st.markdown(
            "<h2 style='text-align:center; color:#1a237e; font-weight:800; font-family:Arial; margin-bottom:26px;'>Student Portal Login</h2>",
            unsafe_allow_html=True
        )

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            response = login_client.login(username, password)
            if response:
                st.session_state.logged_in = True
                st.session_state.role = response.get("role")
                st.session_state.username = username
                st.session_state.current_page = "homepage" 
                st.switch_page("pages/Home.py")
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")

        st.markdown(
            "<div class='forgot-link'><a href='#'>Forgot password?</a></div>",
            unsafe_allow_html=True
        )

show_login()