import streamlit as st

import pandas as pd
from services.book_client import BookClient
from services.order_client import OrderClient


def show():
    order_service = OrderClient()
    book_service = BookClient()
    data = book_service.get_book_stock()

    orders = order_service.list_orders()
    current_requests = len(orders)

    to_claim_count = len([o for o in orders if o["status"] == "to_claim"])
    st.title("Dashboard")

    col1, col2, col3 = st.columns(3)

    # Green card for Current Requests
    with col1:
        st.markdown(
            f"""
            <div style="padding:20px; background-color:#27ae60; border-radius:10px; text-align:center;">
                <h3 style="margin:0; color:white;">Pending Request Orders</h3>
                <p style="font-size:32px; font-weight:bold; color:white;">{current_requests}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Placeholder card 1
    with col2:
        st.markdown(
            f"""
            <div style="padding:20px; background-color:#95a5a6; border-radius:10px; text-align:center;">
                <h3 style="margin:0; color:white;">To Claim Orders</h3>
                <p style="font-size:32px; font-weight:bold; color:white;">{to_claim_count}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Placeholder card 2
    with col3:
        st.markdown(
            """
            <div style="padding:20px; background-color:#95a5a6; border-radius:10px; text-align:center;">
                <h3 style="margin:0; color:white;">Success Orders</h3>
                <p style="font-size:32px; font-weight:bold; color:white;">--</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    df = pd.DataFrame(list(data.items()), columns=["Book Code", "Stock"])
    df["Stock"] = df["Stock"].astype(int)

    st.title("📊 Book Dashboard")

    # Horizontal bar chart
    st.subheader("Book Stock")
    st.bar_chart(df.set_index("Book Code")["Stock"])

    # Simple table without matplotlib
    st.subheader("Detailed Table")
    st.dataframe(df)