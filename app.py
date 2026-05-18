# app.py
import streamlit as st
from components.navbar import navbar
from pages import Home, Book_page, Uniform_page, Checkout_page, Order_Status, Order_history, Account



selected = navbar()

if selected == "Home":
    Home.show()
elif selected == "Book Page":
    Book_page.show()
elif selected == "Uniform Page":
    Uniform_page.show()
elif selected == "Checkout Page":
    Checkout_page.show()
elif selected == "Order Status Page":
    Order_Status.show()
elif selected == "Order History":
    Order_history.show()
elif selected == "Account":
    Account.show()
