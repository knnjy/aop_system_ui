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
        .table-header{display:grid;grid-template-columns:1.5fr 1.5fr 2fr 1fr 1fr 1fr;background-color:#1e3a8a;padding:14px 24px;}
        .table-header span{font-weight:700;color:white;font-size:14px;}
        .table-row{display:grid;grid-template-columns:1.5fr 1.5fr 2fr 1fr 1fr 1fr;padding:18px 24px;border-bottom:1px solid #f1f5f9;align-items:start;background-color:white;}
        .table-row:last-child{border-bottom:none;}
        .empty-row{padding:30px 24px;text-align:center;color:#94a3b8;font-size:14px;background-color:white;}
        .order-id{color:#1e3a8a;font-weight:600;font-size:14px;}
        .order-date{color:#94a3b8;font-size:14px;}
        .order-items{color:#334155;font-size:14px;line-height:1.8;}
        .order-total{color:#1e293b;font-weight:600;font-size:14px;}
        .badge-claimed{background-color:#dbeafe;color:#1e3a8a;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-cancelled{background-color:#fee2e2;color:#b91c1c;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
    </style>""", unsafe_allow_html=True)

    st.markdown("<div class='oh-title'>Order History</div>", unsafe_allow_html=True)

    # get user id
    current_user_id = st.session_state.get("user_id")

    try:
        orders = order_client.list_orders() or []
    except Exception:
        orders = []

    # Filter by user if logged in, else show all
    if current_user_id:
        user_orders = [o for o in orders if isinstance(o, dict) and str(o.get("user_id", "")) == str(current_user_id)]
    else:
        user_orders = [o for o in orders if isinstance(o, dict)]

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("Search Orders", placeholder="🔍 Search by Order ID...", label_visibility="collapsed")
    with col_filter:
        status_filter = st.selectbox("Filter Status", ["All Statuses", "claimed", "cancelled", "not claimed"], label_visibility="collapsed")

    filtered = user_orders[:]

    if search_query:
        filtered = [o for o in filtered if search_query.lower() in str(o.get("request_id", "")).lower()]

    if status_filter == "claimed":
        filtered = [o for o in filtered if o.get("status", "").lower() == "claimed"]
    elif status_filter == "cancelled":
        filtered = [o for o in filtered if o.get("status", "").lower() == "cancelled"]
    elif status_filter == "not claimed":
        filtered = [o for o in filtered if o.get("status", "").lower() not in {"claimed", "cancelled"}]

    def _parse_date(date_str):
        try:
            return datetime.fromisoformat(str(date_str))
        except Exception:
            return datetime.min

    filtered.sort(key=lambda o: _parse_date(o.get("date_created", "")), reverse=True)

    if "order_history_page" not in st.session_state:
        st.session_state["order_history_page"] = 1

    PAGE_SIZE = 10
    total_items = len(filtered)
    total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)

    if st.session_state["order_history_page"] > total_pages:
        st.session_state["order_history_page"] = total_pages
    if st.session_state["order_history_page"] < 1:
        st.session_state["order_history_page"] = 1

    current_page = st.session_state["order_history_page"]
    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    displayed_orders = filtered[start_idx:end_idx]

    st.markdown("<br>", unsafe_allow_html=True)

    def get_badge(status):
        s = status.lower()
        if s == "claimed":
            return "<span class='badge-claimed'>Claimed</span>"
        if s == "cancelled":
            return "<span class='badge-cancelled'>Cancelled</span>"
        return ""

    rows_html = ""
    for order in displayed_orders:
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

    if not rows_html:
        rows_html = "<div class='empty-row'>📭 No orders found.</div>"

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

    st.markdown("<br>", unsafe_allow_html=True)
    prev_col, info_col, next_col = st.columns([1, 2, 1])
    with prev_col:
        if st.button("← Previous", key="order_history_prev"):
            if st.session_state["order_history_page"] > 1:
                st.session_state["order_history_page"] -= 1
                st.experimental_rerun()
    with info_col:
        st.markdown(f"<div style='text-align:center;color:#475569;'>Page {current_page} of {total_pages} — Showing {min(start_idx+1, total_items)} to {min(end_idx, total_items)} of {total_items}</div>", unsafe_allow_html=True)
    with next_col:
        if st.button("Next →", key="order_history_next"):
            if st.session_state["order_history_page"] < total_pages:
                st.session_state["order_history_page"] += 1
                st.experimental_rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    total_orders = len(user_orders)
    claimed = len([o for o in user_orders if isinstance(o, dict) and o.get("status", "").lower() == "claimed"])
    cancelled = len([o for o in user_orders if isinstance(o, dict) and o.get("status", "").lower() == "cancelled"])

    c1, c2, c3 = st.columns(3)

    def stat_card(col, label, value, bg):
        col.markdown(f"""
            <div style='background-color:{bg};color:white;padding:20px;border-radius:12px;text-align:center;'>
                <p style='font-size:13px;margin:0;opacity:0.85;'>{label}</p>
                <p style='font-size:28px;font-weight:bold;margin:4px 0 0 0;'>{value}</p>
            </div>
        """, unsafe_allow_html=True)

    stat_card(c1, "Total Orders", total_orders, "#1e3a8a")
    stat_card(c2, "Claimed",      claimed,      "#1d4ed8")
    stat_card(c3, "Cancelled",    cancelled,    "#fbbf24")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Order Status", key="back_to_order_status"):
        st.session_state["current_page"] = "Order Status"
        st.rerun()