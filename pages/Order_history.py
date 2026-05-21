import streamlit as st
from datetime import datetime
from services.order_client import OrderClient

order_client = OrderClient()

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(str(date_str))
        return dt.strftime("%B %d, %Y")
    except:
        return str(date_str)

def show():
    st.markdown("""<style>
        .oh-title{font-size:28px;font-weight:700;color:#1e3a8a;margin-bottom:20px;}
        .table-container{background-color:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);}
        .table-header{display:grid;grid-template-columns:1.5fr 1.5fr 2fr 1fr 1fr 1fr;background-color:white;padding:14px 24px;border-bottom:2px solid #e2e8f0;}
        .table-header span{font-weight:700;color:#1e3a8a;font-size:14px;}
        .table-row{display:grid;grid-template-columns:1.5fr 1.5fr 2fr 1fr 1fr 1fr;padding:18px 24px;border-bottom:1px solid #f1f5f9;align-items:start;background-color:white;}
        .table-row:last-child{border-bottom:none;}
        .order-id{color:#1e3a8a;font-weight:600;font-size:14px;}
        .order-date{color:#94a3b8;font-size:14px;}
        .order-items{color:#334155;font-size:14px;line-height:1.8;}
        .order-total{color:#1e293b;font-weight:600;font-size:14px;}
        .badge-approved{background-color:#dcfce7;color:#16a34a;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-pending{background-color:#fef9c3;color:#ca8a04;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-cancelled{background-color:#f1f5f9;color:#64748b;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-claimed{background-color:#dbeafe;color:#1e3a8a;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
    </style>""", unsafe_allow_html=True)

    st.markdown("<div class='oh-title'>Order History</div>", unsafe_allow_html=True)

    orders = order_client.list_orders()

    if not orders:
        st.info("No order history found.")
        return

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("", placeholder="🔍 Search by Order ID or User ID...")
    with col_filter:
        status_filter = st.selectbox("", ["All Statuses", "approved", "approve", "pending", "claimed", "cancelled"])

    filtered = [o for o in orders if isinstance(o, dict)]

    if search_query:
        filtered = [o for o in filtered if
            search_query.lower() in str(o.get("request_id", "")).lower() or
            search_query.lower() in str(o.get("user_id", "")).lower()]

    if status_filter != "All Statuses":
        filtered = [o for o in filtered if o.get("status", "").lower() == status_filter.lower()]

    st.markdown("<br>", unsafe_allow_html=True)

    def get_badge(status):
        s = status.lower()
        if s in ["approved", "approve"]: return "<span class='badge-approved'>Approved</span>"
        elif s == "claimed": return "<span class='badge-claimed'>Claimed</span>"
        elif s == "cancelled": return "<span class='badge-cancelled'>Cancelled</span>"
        return "<span class='badge-pending'>Pending</span>"

    rows_html = ""
    for order in filtered:
        items = order.get("order_item_ids", [])
        items_html = "<br>".join([f"• {item}" for item in items]) if items else "—"
        rows_html += f"""
        <div class='table-row'>
            <div class='order-id'>{order.get('request_id', 'N/A')}</div>
            <div class='order-date'>{format_date(order.get('date_created', '—'))}</div>
            <div class='order-items'>{items_html}</div>
            <div class='order-total'>₱{order.get('total_amount', '0.00')}</div>
            <div class='order-id'>{order.get('user_id', '—')}</div>
            <div>{get_badge(order.get('status', ''))}</div>
        </div>
        """

    st.markdown(f"""
        <div class='table-container'>
            <div class='table-header'>
                <span>Order Number</span>
                <span>Date</span>
                <span>Items</span>
                <span>Total</span>
                <span>User</span>
                <span>Status</span>
            </div>
            {rows_html}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    total_all = len(filtered)
    approved  = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() in ["approved","approve"]])
    claimed   = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() == "claimed"])
    cancelled = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() == "cancelled"])

    c1, c2, c3, c4 = st.columns(4)

    def stat_card(col, label, value, bg):
        col.markdown(f"""
            <div style='background-color:{bg};color:white;padding:20px;border-radius:12px;text-align:center;'>
                <p style='font-size:13px;margin:0;opacity:0.85;'>{label}</p>
                <p style='font-size:28px;font-weight:bold;margin:4px 0 0 0;'>{value}</p>
            </div>
        """, unsafe_allow_html=True)

    stat_card(c1, "Total Orders", total_all, "#1e3a8a")
    stat_card(c2, "Approved",     approved,  "#16a34a")
    stat_card(c3, "Claimed",      claimed,   "#1d4ed8")
    stat_card(c4, "Cancelled",    cancelled, "#64748b")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Order Status", key="back_to_order_status"):
        st.session_state["page"] = "Order Status Page"
        st.rerun()

show()