from app_pages import Account, Book_page, Checkout_page, Home, Login, Order_Status, Order_history, Uniform_page
import streamlit as st
from components.navbar import navbar

st.set_page_config(layout="wide")

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
    Login.show_login()
else:
    selected = navbar() # ✅ only call navbar after login

    # if st.session_state.current_page == 'homepage' or selected == "Home":
    #     Home.show()
    # elif st.session_state.current_page == 'books' or selected == "Book Page":
    #     Book_page.show()
    # elif st.session_state.current_page == 'uniforms' or selected == "Uniform Page":
    #     Uniform_page.show()
    # elif st.session_state.current_page == 'checkout' or selected == "Checkout Page":
    #     Checkout_page.show()
    # elif st.session_state.current_page == 'order_status' or selected == "Order Status Page":
    #     Order_Status.show()
    # elif st.session_state.current_page == 'order_history' or selected == "Order History":
    #     Order_history.show()
    # elif st.session_state.current_page == 'account_info' or selected == "Account":
    #     Account.show()

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
