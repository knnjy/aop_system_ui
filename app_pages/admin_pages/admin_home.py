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
    book_stock = book_service.get_book_stock()

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

    df = pd.DataFrame(orders)

    # Filter only claimed orders
    sales_df = df[df["status"] == "claimed"].copy()

    # Convert date_created to datetime
    sales_df["date_created"] = pd.to_datetime(sales_df["date_created"])

    # --- Aggregations ---
    # Daily sales
    daily_sales = sales_df.groupby(sales_df["date_created"].dt.date)["total_amount"].sum().reset_index()
    daily_sales.rename(columns={"date_created":"Day"}, inplace=True)

    # Weekly sales
    weekly_sales = sales_df.groupby(sales_df["date_created"].dt.to_period("W"))["total_amount"].sum().reset_index()
    weekly_sales["Week"] = weekly_sales["date_created"].astype(str)

    # Monthly sales
    monthly_sales = sales_df.groupby(sales_df["date_created"].dt.to_period("M"))["total_amount"].sum().reset_index()
    monthly_sales["Month"] = monthly_sales["date_created"].astype(str)

    # --- Streamlit UI ---
    st.subheader("📊 Sales Dashboard")

    tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])

    with tab1:
        st.subheader("Daily Claimed Sales")
        col1, col2 = st.columns([1,1])
        with col1:
            st.bar_chart(daily_sales.set_index("Day"))
        with col2:
            st.line_chart(daily_sales.set_index("Day"))

    with tab2:
        st.subheader("Weekly Claimed Sales")
        col1, col2 = st.columns([1,1])
        with col1:
            st.bar_chart(weekly_sales.set_index("Week"))
        with col2:
            st.line_chart(weekly_sales.set_index("Week"))

    with tab3:
        st.subheader("Monthly Claimed Sales")
        col1, col2 = st.columns([1,1])
        with col1:
            st.bar_chart(monthly_sales.set_index("Month"))
        with col2:
            st.line_chart(monthly_sales.set_index("Month"))

    
    ## BOOK STOCK
    df = pd.DataFrame(list(book_stock.items()), columns=["Book Code", "Stock"])
    df["Stock"] = df["Stock"].astype(int)

    # Add notifier column
    # Convert to DataFrame
    df = pd.DataFrame(list(book_stock.items()), columns=["Book Code", "Stock"])
    df["Stock"] = df["Stock"].astype(int)

    # Add notifier column
    def stock_notifier(stock):
        if stock == 0:
            return "❌ Out of Stock"
        elif stock < 10:
            return "⚠️ Low"
        else:
            return "✅ OK"

    df["Notifier"] = df["Stock"].apply(stock_notifier)

    st.subheader("📊 Book Dashboard")
    col1, col2 = st.columns(2)
    # Horizontal bar chart
    with col1:
        st.subheader("Book Stock")
        st.bar_chart(df.set_index("Book Code")["Stock"])
    with col2:
        # Detailed table with notifier
        st.subheader("Book Table Stock")
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

