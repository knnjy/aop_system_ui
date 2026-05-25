import streamlit as st
from services.order_client import OrderClient


def show():
    order_client = OrderClient()

    st.markdown(
        "<h1 style='color:#1e3a8a;'>Order Status</h1>",
        unsafe_allow_html=True
    )


    # FETCH FROM BACKEND
    orders = order_client.list_orders()

    if not orders:
        st.warning("No orders found.")
        st.stop()

    # CONFIG
    status_colors = {
        "To Pay": "#facc15",
        "Pending": "#fb923c",
        "To Claim": "#60a5fa",
        "Item Received": "#4ade80",
        "cancelled": "#ef4444"
    }

    statuses = ["Pending", "To Pay", "To Claim", "Item Received"]

 
    # DISPLAY ORDERS 
    for order in orders:

        # FIX: ensure dict
        if not isinstance(order, dict):
            continue

        status_raw = order.get("status", "Unknown")
        status = status_raw.capitalize()

        # match status index safely
        current_index = statuses.index(status) if status in statuses else 0

        # boxes
        with st.container(border=True):

            # HEADER
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"""
                    <h3 style='color:#1e3a8a;'>{order.get("request_id", "No ID")}</h3>
                    <p style='color:#64748b;'>Ordered on {order.get("date_created", "Unknown")}</p>
                """, unsafe_allow_html=True)

            with col2:
                badge_color = status_colors.get(order.get("status", "pending"), "#94a3b8")

                st.markdown(f"""
                    <div style="
                        background-color:{badge_color};
                        color:white;
                        padding:10px;
                        border-radius:20px;
                        text-align:center;
                        font-weight:bold;
                    ">
                        {status}
                    </div>
                """, unsafe_allow_html=True)

            st.write("")

            # TIMELINE
            timeline_cols = st.columns(4)

            for i, s in enumerate(statuses):

                with timeline_cols[i]:

                    # DONE STEP
                    if i < current_index:

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#1e3a8a;
                                color:white;
                                padding:12px;
                                border-radius:10px;
                                text-align:center;
                                font-weight:bold;
                                box-shadow:0 2px 6px rgba(0,0,0,0.15);
                            ">
                                ✓ {s}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # CURRENT STEP
                    elif i == current_index:

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#2563eb;
                                color:white;
                                padding:12px;
                                border-radius:10px;
                                text-align:center;
                                font-weight:bold;
                                border:2px solid #bfdbfe;
                                box-shadow:0 4px 10px rgba(37,99,235,0.35);
                            ">
                                ● {s}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # FUTURE STEP
                    else:

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#e2e8f0;
                                color:#475569;
                                padding:12px;
                                border-radius:10px;
                                text-align:center;
                                border:1px solid #cbd5e1;
                            ">
                                ○ {s}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.write("")
            st.write("")

            # ITEMS
            st.markdown("<h4 style='color:#1e3a8a;'>Items</h4>", unsafe_allow_html=True)

            for item in order.get("order_item_ids", []):
                st.write(f"• {item}")

            st.write("")

            # TOTAL
            st.markdown(
                f"<h3 style='color:#1e3a8a;'>Total: {order.get('total_amount')}</h3>",
                unsafe_allow_html=True
            )

            disable_cancel = status in ["To Claim", "Item Received"]

            st.button(
                "Cancel Order",
                key=str(order.get("request_id")),
                disabled=disable_cancel
            )

            st.write("")