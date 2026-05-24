import streamlit as st


from components.navbar import navbar
from app_pages import Account, Book_page, Checkout_page, Home, Login, Order_Status, Order_history, Uniform_page

st.set_page_config(layout="wide")

# Global CSS to ensure navbar consistency across all pages
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = 'Home'

# ROUTING
if not st.session_state.logged_in:
    Login.show_login()
else:
    selected = navbar()  

    pages = {
        "Home": Home.show,
        "Books": Book_page.show,
        "Uniforms": Uniform_page.show,
        "Checkout Page": Checkout_page.show,
        "Order Status": Order_Status.show,
        "Order History": Order_history.show,
        "Account": Account.show,
    }

    pages[selected]()
