import streamlit as st
from components.navbar import navbar
from pages import (
    Home,
    Book_page,
    Login,
    Uniform_page,
    Checkout_page,
    Order_Status,
    Order_history,
    Account
)

st.set_page_config(page_title="AOP System", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = 'homepage'

# ROUTING
if not st.session_state.logged_in:
    Login.show()
else:
    page = navbar()   # ✅ only call navbar after login

    if st.session_state.current_page == 'homepage' or page == "Home":
        Home.show()
    elif st.session_state.current_page == 'books' or page == "Book Page":
        Book_page.show()
    elif st.session_state.current_page == 'uniforms' or page == "Uniform Page":
        Uniform_page.show()
    elif st.session_state.current_page == 'checkout' or page == "Checkout Page":
        Checkout_page.show()
    elif st.session_state.current_page == 'order_status' or page == "Order Status Page":
        Order_Status.show()
    elif st.session_state.current_page == 'order_history' or page == "Order History":
        Order_history.show()
    elif st.session_state.current_page == 'account_info' or page == "Account":
        Account.show()
