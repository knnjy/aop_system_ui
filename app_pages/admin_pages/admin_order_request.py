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
    st.markdown("<h1 style='color:#1e3a8a;'>CLAIMING</h1>", unsafe_allow_html=True)

    orders = order_client.list_orders()
    orders = _normalize_orders(orders)

    # ---------- to_claim section ----------
    to_claim_orders = [o for o in orders if (o.get("status") or "").lower() == "to_claim"]

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
            if c6.button("Marked as Claimed", key=mark_key):
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



def requests():
    st.markdown(
        "<h1 style='color:#1e3a8a;'>ORDER REQUEST</h1>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <style>
    .request-card {
        border: 1px solid #1e3a8a;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 18px;
        background-color: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    .request-title {
        color: #1e3a8a;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
    }

    .table-header {
        color: #1e3a8a;
        font-weight: 700;
        font-size: 16px;
    }

    .request-id {
        color: #1e3a8a;
        font-size: 28px;
        font-weight: bold;
        margin-top: 8px;
    }

    .request-text {
        color: #374151;
        font-size: 16px;
        margin-top: 12px;
    }

    .request-total {
        color: #111827;
        font-size: 18px;
        font-weight: bold;
        margin-top: 12px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

    # GET ORDERS
    orders = order_client.list_orders()
    orders = _normalize_orders(orders)

    actionable_statuses = {"pending"}

    # TABLE HEADERS
    header_cols = st.columns([1, 2, 3, 2, 2, 2])

    headers = [
        "Order #",
        "Date",
        "Items",
        "Total",
        "User ID",
        "Action"
    ]

    for col, text in zip(header_cols, headers):
        col.markdown(
            f"<div class='table-header'>{text}</div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    shown = False

    # DISPLAY ORDERS
    for o in orders:

        if not isinstance(o, dict):
            continue

        status = (o.get("status") or "").lower()

        if status not in actionable_statuses:
            continue

        shown = True

        request_id = o.get("request_id") or o.get("id") or "N/A"

        date = (
            o.get("date_created")
            or o.get("date")
            or datetime.now().strftime("%Y-%m-%d")
        )

        items = o.get("order_item_ids") or o.get("items") or []

        total = (
            o.get("total_amount")
            or o.get("total_price")
            or 0
        )

        user_id = o.get("user_id") or "N/A"

        # CARD CONTAINER
        with st.container(border=True):
            col1, col2, col3, col4, col5, col6 = st.columns(
                [1, 2, 3, 2, 2, 2]
            )
            # ORDER ID
            col1.markdown(
                f"""<div class='request-id'>{request_id}</div>""",
                unsafe_allow_html=True
            )
            # DATE
            col2.markdown(
                f"""<div class='request-text'> 📅 {date}</div>""",
                unsafe_allow_html=True
            )
            # ITEMS
            col3.markdown(
                f"""<div class='request-text'> 📦 {_format_items(items)}</div>
                """,
                unsafe_allow_html=True
            )
            # TOTAL
            col4.markdown(
                f"""<div class='request-total'>₱{float(total):,.2f}</div>""",
                unsafe_allow_html=True
            )
            # USER
            col5.markdown(
                f"""<div class='request-text'> 👤 {user_id}</div>""",
                unsafe_allow_html=True
            )

        approve_key = f"approve_{request_id}"
        decline_key = f"decline_{request_id}"
        
        if col6.button("Approve", key=approve_key):
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
                    # keep in 'to_pay' for 30s, then set to 'to_claim'
                    def _job_to_claim():
                        try:
                            order_client.update_order(request_id, {"status": "to_claim"})
                        except Exception:
                            traceback.print_exc()
                            return

                    t1 = threading.Timer(30, _job_to_claim)
                    t1.daemon = True
                    t1.start()

                    flash_set("success", f"Order {request_id} set to 'to_pay'. It will move to 'to_claim' after 30s.", details=resp)
                    _safe_rerun()
                    return
                else:
                    flash_set("error", f"Failed to approve order {request_id}.")
                    _safe_rerun()
                    return

        if col6.button("Reject", key=decline_key):
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
    st.button("Refresh", on_click=_safe_rerun)

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

    st.markdown(
    """
    <style>
    /* Tabs container */
      /* Each tab button */
    button[data-testid="stTab"] {
        flex: 1;                /* equal width for all tabs */
        text-align: center;     /* center the label */
        font-weight: 600;
        padding: 10px;
        border-radius: 6px;
    }
    button[data-testid="stTab"] {
        flex: 1;                  /* equal width */
        text-align: center;       /* center text */
        font-size: 25px;          /* bigger text */
        font-weight: 700;         /* bold text */
        letter-spacing: 1px;      /* spacing between letters */
        color: black;             /* inactive text color */
        border-radius: 6px;
        padding: 10px;
    }
    /* Active tab */
    button[data-testid="stTab"][aria-selected="true"] {
      
        color: #1e3a8a;              /* text color when active */
    }
    </style>
    """,
    unsafe_allow_html=True
)
    tab1, tab2 = st.tabs(["Requests","Claiming"],)
    
    with tab1: 
        requests()

    with tab2:
        claiming_page()