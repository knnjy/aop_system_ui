# app.py
import streamlit as st
from aop_system_ui.components.navbar import Navbar
from aop_system_ui.pages import Home, Book_page, Uniform_page, Checkout_page, Order_status_page, Order_history, Account
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


selected = Navbar()

if selected == "Home":
    Home.show()
elif selected == "Book Page":
    Book_page.show()
elif selected == "Uniform Page":
    Uniform_page.show()
elif selected == "Checkout Page":
    Checkout_page.show()
elif selected == "Order Status Page":
    Order_status_page.show()
elif selected == "Order History":
    Order_history.show()
elif selected == "Account":
    Account.show()
