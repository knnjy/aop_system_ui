# components/navbar.py
import streamlit as st
from streamlit_option_menu import option_menu

def navbar():
    hide_default_menu = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """
    st.markdown(hide_default_menu, unsafe_allow_html=True)

    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=[
                "Home", "Books", "Uniforms",
                "Checkout Page", "Order Status",
                "Order History", "Account"
            ],
            icons=[
                "house", "book", "person-badge",
                "bag-check", "list", "clock-history", "person"
            ],
            menu_icon="list",
            default_index=0,
        )
    return selected
