import streamlit as st
from services.order_client import OrderClient
from datetime import datetime
import threading
import time
import traceback

order_client = OrderClient()

def _format_items(items):
    if not items:
        return "—"
    return ", ".join(str(i) for i in items)

def _safe_rerun():
    """Try to rerun the Streamlit script; fallback to toggling a session flag."""
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        elif hasattr(st, "rerun"):
            st.rerun()
        else:
            st.session_state["_refresh"] = not st.session_state.get("_refresh", False)
    except Exception:
        st.session_state["_refresh"] = not st.session_state.get("_refresh", False)

def _schedule_to_claim_then_claim(request_id: str, delay_to_claim: int = 30, delay_to_claimed: int = 30):
    """Schedule a background chain:
    1) after delay_to_claim seconds set status -> 'to_claim'
    2) after delay_to_claimed seconds from that point set status -> 'claimed'
    This runs in background threads and must not touch Streamlit objects.
    """
    def _job_to_claim():
        try:
            order_client.update_order(request_id, {"status": "to_claim"})
        except Exception:
            traceback.print_exc()
            return

        # schedule final transition to 'claimed'
        def _job_to_claimed():
            try:
                order_client.update_order(request_id, {"status": "claimed"})
            except Exception:
                traceback.print_exc()

        t2 = threading.Timer(delay_to_claimed, _job_to_claimed)
        t2.daemon = True
        t2.start()

    t1 = threading.Timer(delay_to_claim, _job_to_claim)
    t1.daemon = True
    t1.start()

def _normalize_orders(orders):
    """Return a list of order dicts regardless of backend shape."""
    if orders is None:
        return []
    if isinstance(orders, dict):
        return list(orders.values())
    if isinstance(orders, list):
        return orders
    try:
        return list(orders)
    except Exception:
        return []

# ---------- Flash message helpers ----------
def flash_set(level: str, message: str, details=None):
    """Store a flash message in session_state. level: 'success'|'warning'|'error'|'info'."""
    st.session_state["_flash"] = {"level": level, "message": message, "details": details}

def flash_pop():
    """Return and remove the flash message (or None)."""
    flash = st.session_state.pop("_flash", None) if "_flash" in st.session_state else None
    return flash

def flash_show():
    """Render flash message at top of page if present."""
    flash = st.session_state.get("_flash")
    if not flash:
        return
    level = flash.get("level")
    message = flash.get("message")
    details = flash.get("details")
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)
    if details is not None:
        st.write("Details:", details)

# ---------- Pages ----------
def claiming_page():
    """Claiming page: show 'Mark as Claimed' (to_claim orders) above claimed orders."""
    st.markdown("<h1 style='color:#1e3a8a;'>Claiming</h1>", unsafe_allow_html=True)

    orders = order_client.list_orders()
    orders = _normalize_orders(orders)

    # ---------- to_claim section ----------
    to_claim_orders = [o for o in orders if (o.get("status") or "").lower() == "to_claim"]

    st.markdown("<h2 style='color:#1e3a8a;'>Mark as Claimed</h2>", unsafe_allow_html=True)
    if not to_claim_orders:
        st.info("No orders waiting to be marked as claimed")
    else:
        header_cols = st.columns([1, 2, 3, 2, 2, 2])
        headers = ["Order #", "Date", "Items", "Total", "User ID", "Action"]
        for col, text in zip(header_cols, headers):
            col.markdown(f"<strong style='color:#1e3a8a;'>{text}</strong>", unsafe_allow_html=True)

        for o in to_claim_orders:
            request_id = o.get("request_id") or o.get("id") or "N/A"
            date = o.get("date_created") or o.get("date") or datetime.now().strftime("%Y-%m-%d")
            items = o.get("order_item_ids") or o.get("items") or []
            total = o.get("total_amount") or o.get("total_price") or 0
            user_id = o.get("user_id") or "N/A"

            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 3, 2, 2, 2])
            c1.write(request_id)
            c2.write(date)
            c3.write(_format_items(items))
            c4.write(f"${float(total):.2f}")
            c5.write(user_id)

            mark_key = f"mark_claimed_{request_id}"
            if c6.button("Mark Claimed", key=mark_key):
                with st.spinner(f"Marking {request_id} as claimed..."):
                    try:
                        resp = order_client.update_order(request_id, {"status": "claimed"})
                    except Exception as e:
                        resp = None
                        flash_set("error", f"API error while marking {request_id} as claimed", str(e))
                        _safe_rerun()
                        return

                    if resp:
                        flash_set("success", f"Order {request_id} marked as claimed.", details=resp)
                        _safe_rerun()
                        return
                    else:
                        flash_set("error", f"Failed to mark order {request_id} as claimed.")
                        _safe_rerun()
                        return

    st.markdown("---")

    # ---------- claimed section ----------
    st.markdown("<h2 style='color:#1e3a8a;'>Claimed Orders</h2>", unsafe_allow_html=True)
    claimed_orders = [o for o in orders if (o.get("status") or "").lower() in ("claimed", "received")]

    if not claimed_orders:
        st.info("No claimed orders yet")
        return

    header_cols = st.columns([1, 2, 3, 2, 2])
    headers = ["Order #", "Date", "Items", "Total", "User ID"]
    for col, text in zip(header_cols, headers):
        col.markdown(f"<strong style='color:#1e3a8a;'>{text}</strong>", unsafe_allow_html=True)

    for o in claimed_orders:
        request_id = o.get("request_id") or o.get("id") or "N/A"
        date = o.get("date_created") or o.get("date") or datetime.now().strftime("%Y-%m-%d")
        items = o.get("order_item_ids") or o.get("items") or []
        total = o.get("total_amount") or o.get("total_price") or 0
        user_id = o.get("user_id") or "N/A"

        c1, c2, c3, c4, c5 = st.columns([1, 2, 3, 2, 2])
        c1.write(request_id)
        c2.write(date)
        c3.write(_format_items(items))
        c4.write(f"${float(total):.2f}")
        c5.write(user_id)

def requests():
    st.markdown("<h1 style='color:#1e3a8a;'>Order Requests</h1>", unsafe_allow_html=True)
    orders = order_client.list_orders()
    orders = _normalize_orders(orders)

    actionable_statuses = {"pending"}

    header_cols = st.columns([1, 2, 3, 2, 2, 2])
    headers = ["Order #", "Date", "Items", "Total", "User ID", "Action"]
    for col, text in zip(header_cols, headers):
        col.markdown(f"<strong style='color:#1e3a8a;'>{text}</strong>", unsafe_allow_html=True)

    shown = False
    for o in orders:
        if not isinstance(o, dict):
            continue

        status = (o.get("status") or "").lower()
        if status not in actionable_statuses:
            continue

        shown = True
        request_id = o.get("request_id") or o.get("id") or "N/A"
        date = o.get("date_created") or o.get("date") or datetime.now().strftime("%Y-%m-%d")
        items = o.get("order_item_ids") or o.get("items") or []
        total = o.get("total_amount") or o.get("total_price") or 0
        user_id = o.get("user_id") or "N/A"

        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 3, 2, 2, 2])
        col1.write(request_id)
        col2.write(date)
        col3.write(_format_items(items))
        col4.write(f"${float(total):.2f}")
        col5.write(user_id)

        approve_key = f"approve_{request_id}"
        decline_key = f"decline_{request_id}"

        if col6.button("✅ Approve", key=approve_key):
            with st.spinner(f"Approving order {request_id}..."):
                try:
                    # set to 'to_pay' immediately
                    resp = order_client.update_order(request_id, {"status": "to_pay", "approved_by": st.session_state.get("account_id")})
                except Exception as e:
                    resp = None
                    flash_set("error", f"API error while approving {request_id}", str(e))
                    _safe_rerun()
                    return

                if resp:
                    # wait 30s in 'to_pay', then set to 'to_claim', then after another 30s set to 'claimed'
                    _schedule_to_claim_then_claim(request_id, delay_to_claim=30, delay_to_claimed=30)
                    flash_set("success", f"Order {request_id} set to 'to_pay'. It will move to 'to_claim' after 30s and to 'claimed' 30s after that.", details=resp)
                    _safe_rerun()
                    return
                else:
                    flash_set("error", f"Failed to approve order {request_id}.")
                    _safe_rerun()
                    return

        if col6.button("❌ Decline", key=decline_key):
            with st.spinner(f"Declining order {request_id}..."):
                try:
                    resp = order_client.update_order(request_id, {"status": "declined"})
                except Exception as e:
                    resp = None
                    flash_set("error", f"API error while declining {request_id}", str(e))
                    _safe_rerun()
                    return

                if resp:
                    flash_set("success", f"Order {request_id} successfully declined.", details=resp)
                    _safe_rerun()
                    return
                else:
                    flash_set("error", f"Failed to decline order {request_id}.")
                    _safe_rerun()
                    return

    if not shown:
        st.info("No pending/actionable orders")

def show():
    # render flash at top if present
    flash_show()

    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #1d4ed8;
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            border: none;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "page" not in st.session_state:
        st.session_state.page = "orders"

    if st.session_state.page == "orders":
        if st.button("Show Claimed Orders", key="show_claimed_btn"):
            st.session_state.page = "claimed"
        requests()

    elif st.session_state.page == "claimed":
        if st.button("Back to Order Requests", key="back_btn"):
            st.session_state.page = "orders"
        claiming_page()