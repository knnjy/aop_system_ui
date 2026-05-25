import streamlit as st


st.set_page_config(layout="wide")

from app_pages.admin_pages import admin_books, admin_home, admin_order_history, admin_order_request, admin_uniform
from components.navbar import admin_navbar, navbar
from app_pages import Account, Book_page, Checkout_page, Home, Login, Order_Status, Order_history, Uniform_page

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
if 'role' not in st.session_state:
    st.session_state.role = 'User'


# ROUTING
if not st.session_state.logged_in:
    Login.show_login()  
else:

    if st.session_state['role'] == 'Admin':
        selected = admin_navbar()
        pages = {
            "Home": admin_home.show,
            "Books": admin_books.show,
            "Uniforms": admin_uniform.show,
            "Order Request": admin_order_request.show,
            "Order History": admin_order_history.show,
            "Account": Account.show
        }
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
