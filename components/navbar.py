# components/navbar.py
import streamlit as st

def navbar():
    st.markdown(
        """
        <style>
        .navbar {background-color:#2C3E50; padding:10px;}
        .navbar a {color:white; margin:0 15px; text-decoration:none;}
        </style>
        <div class="navbar">
            <a href="/">Home</a>
            <a href="/Catalog_Books">Books</a>
            <a href="/Catalog_Uniforms">Uniforms</a>
            <a href="/Orders">Orders</a>
            <a href="/Payments">Payments</a>
        </div>
        """,
        unsafe_allow_html=True
    )
