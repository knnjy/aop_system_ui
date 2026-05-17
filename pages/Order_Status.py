import streamlit as st
from services.order_client import OrderClient

st.set_page_config(
    page_title="Order Status",
    layout="wide"
)

order_client = OrderClient()

st.markdown(
    """
    <h1 style='color:#1e3a8a;'>
        Order Status
    </h1>
    """,
    unsafe_allow_html=True
)

# SAMPLE DATA
orders = [
    {
        "id": "ORD-2026-0001",
        "date": "May 10, 2026",
        "status": "To Claim",
        "items": [
            "Introduction to Computer Science Textbook",
            "School Polo Shirt"
        ],
        "total": "$159.99"
    },
    {
        "id": "ORD-2026-0002",
        "date": "May 12, 2026",
        "status": "Pending",
        "items": [
            "Laboratory Coat",
            "Official Academic Uniform Tie"
        ],
        "total": "$60.00"
    },
    {
        "id": "ORD-2026-0003",
        "date": "May 15, 2026",
        "status": "To Pay",
        "items": [
            "Calculus for Engineers",
            "Physics Laboratory Manual"
        ],
        "total": "$170.50"
    }
]

status_colors = {
    "To Pay": "#facc15",
    "Pending": "#fb923c",
    "To Claim": "#60a5fa",
    "Item Received": "#4ade80"
}

statuses = [
    "To Pay",
    "Pending",
    "To Claim",
    "Item Received"
]

for order in orders:

    current_index = statuses.index(order["status"])

    st.markdown(
        f"""
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

    top_col1, top_col2 = st.columns([4, 1])

    with top_col1:
        st.markdown(
            f"""
            <h3 style='color:#1e3a8a; margin-bottom:0;'>
                {order["id"]}
            </h3>

            <p style='color:#64748b;'>
                Ordered on {order["date"]}
            </p>
            """,
            unsafe_allow_html=True
        )

    with top_col2:

        badge_color = status_colors[order["status"]]

        st.markdown(
            f"""
            <div style="
                background-color:{badge_color};
                color:white;
                padding:10px;
                border-radius:20px;
                text-align:center;
                font-weight:bold;
                margin-top:10px;
            ">
                {order["status"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # TIMELINE
    timeline_cols = st.columns(4)

    for i, status in enumerate(statuses):

        with timeline_cols[i]:

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
                    ">
                        ✓ {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
                    ">
                        ● {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        background-color:#e2e8f0;
                        color:#475569;
                        padding:12px;
                        border-radius:10px;
                        text-align:center;
                    ">
                        ○ {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")
    st.write("")

    st.markdown(
        "<h4 style='color:#1e3a8a;'>Items</h4>",
        unsafe_allow_html=True
    )

    for item in order["items"]:
        st.write(f"• {item}")

    st.write("")

    footer_col1, footer_col2 = st.columns([4, 1])

    with footer_col1:

        st.markdown(
            f"""
            <h3 style='color:#1e3a8a;'>
                Total: {order["total"]}
            </h3>
            """,
            unsafe_allow_html=True
        )

    with footer_col2:

        st.button(
            "Cancel Order",
            key=order["id"]
        )

    st.markdown("</div>", unsafe_allow_html=True)