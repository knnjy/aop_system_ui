import streamlit as st

def show():

    st.set_page_config(page_title="AOP System - Home", page_icon="house.svg", layout="wide")
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
        <div style='border:2px solid #6e6e6e; background-color:#f9f9f9; padding:20px; border-radius:8px'>
            <span style='color:#1e3a8a; font-weight:bold; font-size:24px'>
                Welcome to the AOP System
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )