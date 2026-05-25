import streamlit as st

import pandas as pd
from services.book_client import BookClient
from services.order_client import OrderClient
from services.uniform_client import UniformClient


def show():
    order_service = OrderClient()
    book_service = BookClient()
    uniform_service = UniformClient()
    
    uniform_stock = uniform_service.get_stocks()
    data = book_service.get_book_stock()

    orders = order_service.list_orders()
    current_requests = len([o for o in orders if o["status"] == "pending"])

    to_claim_count = len([o for o in orders if o["status"] == "to_claim"])
    success_order = len([o for o in orders if o["status"] == "claimed"])
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
            <div style="padding:20px; background-color:#65a5a6; border-radius:10px; text-align:center;">
                <h3 style="margin:0; color:white;">To Claim Orders</h3>
                <p style="font-size:32px; font-weight:bold; color:white;">{to_claim_count}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Placeholder card 2
    with col3:
        st.markdown(
            f"""
            <div style="padding:20px; background-color:#25a5a6; border-radius:10px; text-align:center;">
                <h3 style="margin:0; color:white;">Success Orders</h3>
                <p style="font-size:32px; font-weight:bold; color:white;">{success_order}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)
    with col1:
        df = pd.DataFrame(list(data.items()), columns=["Book Code", "Stock"])
        df["Stock"] = df["Stock"].astype(int)

        st.title("📊 Book Dashboard")

        # Horizontal bar chart
        st.subheader("Book Stock")
        st.bar_chart(df.set_index("Book Code")["Stock"])
    with col2:
        # Simple table without matplotlib
        st.subheader("Detailed Table")
        st.dataframe(df)

    col1, col2 = st.columns(2)
    

    import altair as alt

    # Flatten uniform stock into product_id, size, stock
    flat_uniform = []
    for item in uniform_stock:
        for product_id, sizes in item.items():
            for size_code, stock in sizes.items():
                size = size_code.split("-")[-1]  # extract size (S, M, L, etc.)
                flat_uniform.append({
                    "Product ID": product_id,
                    "Size": size,
                    "Stock": stock
                })

    df_uniforms = pd.DataFrame(flat_uniform)
    df_uniforms["Stock"] = df_uniforms["Stock"].astype(int)

    st.subheader("Uniform Stock")
    chart = alt.Chart(df_uniforms).mark_bar().encode(
        x=alt.X("Product ID:N", title="Product"),
        y=alt.Y("Stock:Q", title="Stock"),
        color="Size:N",
        xOffset="Size:N",  # ensures grouping by size
        tooltip=["Product ID", "Size", "Stock"]
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)
