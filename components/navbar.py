# components/navbar.py
import streamlit as st
from streamlit_option_menu import option_menu

def Navbar():
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
                "Home", "Book Page", "Uniform Page",
                "Checkout Page", "Order Status Page",
                "Order History", "Account"
            ],
            icons=[
                "house", "book", "person-badge",
                "bag-check", "list", "clock-history", "person"
            ],
            menu_icon="cast",
            default_index=0,
        )
    return selected
