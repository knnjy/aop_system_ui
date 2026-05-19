import streamlit as st
from services.order_client import OrderClient

order_client = OrderClient()

MOCK_ORDERS = [
    {"request_id": "ORD-2025-0087", "date_created": "2025-12-15T10:00:00", "order_items": [{"product_id": "Data Structures Textbook", "quantity": 1, "unit_price": 100, "subtotal": 100}, {"product_id": "Algorithm Design Manual", "quantity": 1, "unit_price": 85, "subtotal": 85}], "total_amount": 185.50, "status": "Item Received"},
    {"request_id": "ORD-2025-0056", "date_created": "2025-11-03T10:00:00", "order_items": [{"product_id": "School PE Uniform Set", "quantity": 1, "unit_price": 65, "subtotal": 65}], "total_amount": 65.00, "status": "Item Received"},
    {"request_id": "ORD-2025-0032", "date_created": "2025-10-18T10:00:00", "order_items": [{"product_id": "Chemistry Laboratory Manual", "quantity": 1, "unit_price": 45, "subtotal": 45}, {"product_id": "Safety Goggles", "quantity": 1, "unit_price": 13, "subtotal": 13}], "total_amount": 58.00, "status": "Item Received"},
    {"request_id": "ORD-2025-0021", "date_created": "2025-09-25T10:00:00", "order_items": [{"product_id": "Engineering Mathematics Textbook", "quantity": 1, "unit_price": 145, "subtotal": 145}], "total_amount": 145.00, "status": "Cancelled"},
    {"request_id": "ORD-2025-0012", "date_created": "2025-09-10T10:00:00", "order_items": [{"product_id": "School Polo Shirt - Navy", "quantity": 1, "unit_price": 40, "subtotal": 40}, {"product_id": "School Necktie", "quantity": 1, "unit_price": 13, "subtotal": 13}], "total_amount": 53.00, "status": "Declined"},
]

def show():
    from datetime import datetime

    def format_date(date_str):
        try:
            dt = datetime.fromisoformat(str(date_str))
            return dt.strftime("%B %d, %Y")
        except:
            return str(date_str)

    st.markdown("""<style>
        .oh-title{font-size:28px;font-weight:700;color:#1e3a8a;margin-bottom:20px;}
        .table-container{background-color:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);}
        .table-header{display:grid;grid-template-columns:1.5fr 1.5fr 3fr 1fr 1fr;background-color:white;padding:14px 24px;border-bottom:2px solid #e2e8f0;}
        .table-header span{font-weight:700;color:#1e3a8a;font-size:14px;}
        .table-row{display:grid;grid-template-columns:1.5fr 1.5fr 3fr 1fr 1fr;padding:18px 24px;border-bottom:1px solid #f1f5f9;align-items:start;background-color:white;}
        .table-row:last-child{border-bottom:none;}
        .order-id{color:#1e3a8a;font-weight:600;font-size:14px;}
        .order-date{color:#94a3b8;font-size:14px;}
        .order-items{color:#334155;font-size:14px;line-height:1.8;}
        .order-total{color:#1e293b;font-weight:600;font-size:14px;}
        .badge-received{background-color:#dcfce7;color:#16a34a;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-cancelled{background-color:#f1f5f9;color:#64748b;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
        .badge-declined{background-color:#fee2e2;color:#dc2626;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:500;display:inline-block;}
    </style>""", unsafe_allow_html=True)

    st.markdown("<div class='oh-title'>Order History</div>", unsafe_allow_html=True)

    try:
        orders = order_client.list_orders()
        if not orders:
            orders = MOCK_ORDERS
    except Exception:
        orders = MOCK_ORDERS

    completed_statuses = ["item received", "declined", "cancelled"]
    history_orders = [o for o in orders if isinstance(o, dict) and o.get("status", "").lower() in completed_statuses]

    if not history_orders:
        st.info("No completed orders in your history yet.")
        return

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("", placeholder="🔍 Search by Order ID or product...")
    with col_filter:
        status_filter = st.selectbox("", ["All Statuses", "Item Received", "Cancelled", "Declined"])

    if search_query:
        history_orders = [o for o in history_orders if search_query.lower() in str(o.get("request_id", "")).lower() or any(search_query.lower() in str(item.get("product_id", "")).lower() for item in o.get("order_items", []))]

    if status_filter != "All Statuses":
        history_orders = [o for o in history_orders if o.get("status", "").lower() == status_filter.lower()]

    st.markdown("<br>", unsafe_allow_html=True)

    def get_badge(status):
        s = status.lower()
        if s == "item received": return "<span class='badge-received'>Item Received</span>"
        elif s == "cancelled": return "<span class='badge-cancelled'>Cancelled</span>"
        elif s == "declined": return "<span class='badge-declined'>Declined</span>"
        return "<span class='badge-cancelled'>Unknown</span>"

    rows_html = ""
    for order in history_orders:
        items = order.get("order_items", [])
        items_html = "<br>".join([f"• {item.get('product_id','Unknown')} (x{item.get('quantity',1)}) — ₱{item.get('subtotal',0)}" for item in items]) if items else "—"
        rows_html += f"<div class='table-row'><div class='order-id'>{order.get('request_id','N/A')}</div><div class='order-date'>{format_date(order.get('date_created','—'))}</div><div class='order-items'>{items_html}</div><div class='order-total'>₱{order.get('total_amount','0.00')}</div><div>{get_badge(order.get('status',''))}</div></div>"

    st.markdown(f"<div class='table-container'><div class='table-header'><span>Order Number</span><span>Date</span><span>Items</span><span>Total</span><span>Status</span></div>{rows_html}</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    received = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() == "item received"])
    cancelled = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() == "cancelled"])
    declined = len([o for o in orders if isinstance(o, dict) and o.get("status","").lower() == "declined"])
    total_all = len([o for o in orders if isinstance(o, dict)])

    c1,c2,c3,c4 = st.columns(4)
    def stat_card(col,label,value,bg):
        col.markdown(f"<div style='background-color:{bg};color:white;padding:20px;border-radius:12px;text-align:center;'><p style='font-size:13px;margin:0;opacity:0.85;'>{label}</p><p style='font-size:28px;font-weight:bold;margin:4px 0 0 0;'>{value}</p></div>", unsafe_allow_html=True)

    stat_card(c1,"Total Orders",total_all,"#1e3a8a")
    stat_card(c2,"Item Received",received,"#16a34a")
    stat_card(c3,"Cancelled",cancelled,"#64748b")
    stat_card(c4,"Declined",declined,"#dc2626")
