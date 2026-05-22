import streamlit as st

def show():
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
            Account Page
        </h1>
        """,
        unsafe_allow_html=True
    )