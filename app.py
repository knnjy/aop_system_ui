import streamlit as st

# IMPORT PAGES DIRECTLY (NO PACKAGE PREFIX)
from components.navbar import navbar

from pages import (
    Home,
    Book_page,
    Uniform_page,
    Checkout_page,
    Order_Status,
    Order_history,
    Account
)

st.set_page_config(page_title="AOP System", layout="wide")

# NAVBAR
navbar()

# SIMPLE PAGE NAVIGATION (STREAMLIT STYLE)
page = st.sidebar.selectbox(
    "Navigate",
    [
        "Home",
        "Book Page",
        "Uniform Page",
        "Checkout Page",
        "Order Status Page",
        "Order History",
        "Account"
    ]
)

if page == "Home":
    Home.show()

elif page == "Book Page":
    Book_page.show()

elif page == "Uniform Page":
    Uniform_page.show()

elif page == "Checkout Page":
    Checkout_page.show()

elif page == "Order Status Page":
    Order_Status.show()

elif page == "Order History":
    Order_history.show()

elif page == "Account":
    Account.show()