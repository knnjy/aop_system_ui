import streamlit as st
from services.order_client import OrderClient

st.set_page_config(page_title="Order Status", layout="wide")

order_client = OrderClient()

st.markdown(
    "<h1 style='color:#1e3a8a;'>Order Status</h1>",
    unsafe_allow_html=True
)

# =========================
# FETCH FROM BACKEND
# =========================
orders = order_client.list_orders()

if not orders:
    st.warning("No orders found.")
    st.stop()

# =========================
# CONFIG
# =========================
status_colors = {
    "To Pay": "#facc15",
    "Pending": "#fb923c",
    "To Claim": "#60a5fa",
    "Item Received": "#4ade80",
    "cancelled": "#ef4444"
}

statuses = ["To Pay", "Pending", "To Claim", "Item Received"]

# =========================
# DISPLAY ORDERS
# =========================
for order in orders:

    # 🔥 FIX: ensure dict
    if not isinstance(order, dict):
        continue

    status_raw = order.get("status", "pending")
    status = status_raw.capitalize()

    # match status index safely
    current_index = statuses.index(status) if status in statuses else 0

    st.markdown(
        """
        <div style="
            background-color:white;
            padding:25px;
            border-radius:15px;
            border:1px solid #e2e8f0;
            margin-bottom:25px;
            box-shadow:0 2px 8px rgba(0,0,0,0.05);
        ">
        """,
        unsafe_allow_html=True
    )

    # HEADER
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
            <h3 style='color:#1e3a8a;'>{order.get("id", "No ID")}</h3>
            <p style='color:#64748b;'>Ordered on {order.get("date", "Unknown")}</p>
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
            if i < current_index:
                st.markdown(f"✓ {s}")
            elif i == current_index:
                st.markdown(f"● {s}")
            else:
                st.markdown(f"○ {s}")

    st.write("")
    st.write("")

    # ITEMS (backend already gives list)
    st.markdown("<h4 style='color:#1e3a8a;'>Items</h4>", unsafe_allow_html=True)

    for item in order.get("items", []):
        st.write(f"• {item}")

    st.write("")

    # TOTAL
    st.markdown(
        f"<h3 style='color:#1e3a8a;'>Total: {order.get('total')}</h3>",
        unsafe_allow_html=True
    )

    st.button("Cancel Order", key=str(order.get("id")))
    st.markdown("</div>", unsafe_allow_html=True)