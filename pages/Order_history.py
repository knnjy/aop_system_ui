import streamlit as st

def show():
    st.set_page_config(page_title="AOP System - Order History", page_icon="📋", layout="wide")
    # Inject custom CSS
    st.markdown(
        """
        <style>
        .stApp {
            background-color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <h1 style='color:#1e3a8a;'>
            Order History
        </h1>
        """,
        unsafe_allow_html=True
    )