import uuid
import streamlit as st
from services.order_client import OrderClient

def _get_session_account_id():
    candidates = [
        "account_id",
        "user_id",
        "user",
        "user_info",
        "profile",
    ]
    for k in candidates:
        if k in st.session_state:
            val = st.session_state[k]
            if isinstance(val, dict):
                for nested in ("account_id", "user_id", "id"):
                    if nested in val:
                        return str(val[nested])
            else:
                return str(val)
    return None

def safe_rerun():
    """Try the standard rerun; if unavailable, change query params to force a rerun."""
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
            return
    except Exception:
        pass
    try:
        st.query_params(_refresh=str(uuid.uuid4()))
        return
    except Exception:
        pass
    st.session_state["_refresh"] = not st.session_state.get("_refresh", False)

def _show_confirmation_inline(order_id: str):
    """Fallback inline confirmation UI (Yes / No). Returns True if user confirmed."""
    key_yes = f"confirm_yes_{order_id}"
    key_no = f"confirm_no_{order_id}"
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Yes, cancel", key=key_yes):
            return True
    with col2:
        if st.button("No, keep", key=key_no):
            return False
    return None

def show(debug: bool = False):
    order_client = OrderClient()

    st.markdown("<h1 style='color:#1e3a8a;'>Order Status</h1>", unsafe_allow_html=True)

    orders = order_client.list_orders()
    if orders is None:
        st.error("Failed to fetch orders from API.")
        st.stop()

    raw_account = _get_session_account_id()
    if raw_account is None:
        if debug:
            st.warning("No account id found in session_state. Keys available:")
            st.write(list(st.session_state.keys()))
        st.info("You are not logged in or account id is missing.")
        st.stop()

    account_id = raw_account.strip().lower()

    if debug:
        st.write("session account_id (normalized):", account_id)
        st.write("raw orders user_id values:", [o.get("user_id") for o in orders if isinstance(o, dict)])

    # status normalization map
    status_map = {
        "to pay": "to_pay",
        "to_pay": "to_pay",
        "to pay ": "to_pay",
        "to claim": "to_claim",
        "to_claim": "to_claim",
        "item received": "item_received",
        "item_received": "item_received",
        "received": "received",
        "claimed": "claimed",
        "cancelled": "cancelled",
        "cancel": "cancelled",
        "approved": "to_claim",
        "pending": "pending",
    }

    status_colors = {
        "pending": "#fb923c",
        "to_pay": "#facc15",
        "to_claim": "#60a5fa",
        "item_received": "#4ade80",
        "received": "#4ade80",
        "claimed": "#ef4444",
        "cancelled": "#ef4444",
    }

    timeline_statuses = ["pending", "to_pay", "to_claim", "item_received"]

    # Only show these canonical statuses
    allowed_display = {"pending", "to_pay", "to_claim"}

    # filter orders for this account (normalize user_id)
    user_orders = []
    for o in orders:
        if not isinstance(o, dict):
            continue
        uid = str(o.get("user_id", "")).strip().lower()
        if uid == account_id:
            user_orders.append(o)
        elif debug:
            st.write(f"skipping order {o.get('request_id')} (user_id={o.get('user_id')})")

    # If there are no orders for this account at all, show message
    if not user_orders:
        st.info("You have no active orders")
        st.stop()

    # NEW: determine which of the user_orders will actually be displayed
    # (i.e., those that have a canonical status in allowed_display and are not hidden)
    displayable_orders = []
    for order in user_orders:
        raw_status = str(order.get("status", "unknown")).strip().lower()
        mapped_status = status_map.get(raw_status, raw_status.replace(" ", "_"))
        # Skip orders that won't be displayed due to status
        if mapped_status not in allowed_display:
            if debug:
                st.write(f"Not displayable (status) {order.get('request_id')} -> {mapped_status}")
            continue
        # Skip orders hidden by session flag
        hidden_key = f"hidden_{order.get('request_id')}"
        if st.session_state.get(hidden_key):
            if debug:
                st.write(f"Not displayable (hidden) {order.get('request_id')}")
            continue
        # If we reach here, this order will be shown
        displayable_orders.append(order)

    # If nothing will be shown in the order list, show the "no active orders" message
    if not displayable_orders:
        st.info("You have no active orders")
        st.stop()

    # display each order (only iterate displayable_orders now)
    for order in displayable_orders:
        raw_status = str(order.get("status", "unknown")).strip().lower()
        mapped_status = status_map.get(raw_status, raw_status.replace(" ", "_"))
        status = mapped_status

        # Skip if user previously confirmed cancellation (persisted in session_state)
        hidden_key = f"hidden_{order.get('request_id')}"
        if st.session_state.get(hidden_key):
            if debug:
                st.write(f"Order {order.get('request_id')} hidden by session flag.")
            continue

        current_index = timeline_statuses.index(status) if status in timeline_statuses else 0

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                    <h3 style='color:#1e3a8a;'>{order.get("request_id", "No ID")}</h3>
                    <p style='color:#64748b;'>Ordered on {order.get("date_created", "Unknown")}</p>
                """, unsafe_allow_html=True)

            with col2:
                badge_color = status_colors.get(status, "#94a3b8")
                st.markdown(f"""
                    <div style="
                        background-color:{badge_color};
                        color:white;
                        padding:10px;
                        border-radius:20px;
                        text-align:center;
                        font-weight:bold;
                    ">
                        {status.replace('_', ' ').title()}
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            timeline_cols = st.columns(len(timeline_statuses))
            for i, s in enumerate(timeline_statuses):
                with timeline_cols[i]:
                    label = s.replace("_", " ").title()
                    if i < current_index:
                        st.markdown(f"""
                            <div style="
                                background-color:#1e3a8a;
                                color:white;
                                padding:12px;
                                border-radius:10px;
                                text-align:center;
                                font-weight:bold;
                                box-shadow:0 2px 6px rgba(0,0,0,0.15);
                            ">
                                ✓ {label}
                            </div>
                        """, unsafe_allow_html=True)
                    elif i == current_index:
                        st.markdown(f"""
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
                                ● {label}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="
                                background-color:#e2e8f0;
                                color:#475569;
                                padding:12px;
                                border-radius:10px;
                                text-align:center;
                                border:1px solid #cbd5e1;
                            ">
                                ○ {label}
                            </div>
                        """, unsafe_allow_html=True)

            st.write("")
            st.markdown("<h4 style='color:#1e3a8a;'>Items</h4>", unsafe_allow_html=True)
            for item in order.get("order_item_ids", []):
                st.write(f"• {item}")

            st.markdown(f"<h3 style='color:#1e3a8a;'>Total: {order.get('total_amount')}</h3>", unsafe_allow_html=True)

            # Cancel button: visible only for pending / to_pay
            if status in ("pending", "to_pay"):
                confirm_key = f"confirm_cancel_{order.get('request_id')}"
                # If user clicked initial Cancel, set a session flag to show confirmation UI
                if st.button("Cancel Order", key=f"cancel_{order.get('request_id')}"):
                    st.session_state[confirm_key] = True

                # Show confirmation modal if available
                if st.session_state.get(confirm_key):
                    confirmed = None
                    # prefer modal if Streamlit supports it
                    if hasattr(st, "modal"):
                        with st.modal(f"Confirm cancel {order.get('request_id')}"):
                            st.markdown(f"Are you sure you want to cancel **{order.get('request_id')}**? This action cannot be undone.")
                            col_yes, col_no = st.columns([1, 1])
                            with col_yes:
                                if st.button("Yes, cancel", key=f"modal_yes_{order.get('request_id')}"):
                                    confirmed = True
                            with col_no:
                                if st.button("No, keep", key=f"modal_no_{order.get('request_id')}"):
                                    confirmed = False
                    else:
                        st.warning(f"Are you sure you want to cancel {order.get('request_id')}?")
                        confirmed = _show_confirmation_inline(order.get('request_id'))

                    # Handle confirmation result
                    if confirmed is True:
                        success = order_client.cancel_order(order.get("request_id"))
                        if success:
                            st.success("Order cancelled successfully.")
                            # mark hidden so it won't show again in this session
                            st.session_state[hidden_key] = True
                            # clear confirmation flag
                            st.session_state[confirm_key] = False
                            safe_rerun()
                        else:
                            st.error("Failed to cancel order.")
                            st.session_state[confirm_key] = False
                    elif confirmed is False:
                        # user declined; hide confirmation UI
                        st.session_state[confirm_key] = False