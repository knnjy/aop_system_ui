import streamlit as st
from services.auth_client import AuthClient
from services.book_client import BookClient
from services.order_client import OrderClient


def _format_price(value):
    try:
        amount = float(value)
        return f"₱{amount:,.2f}"
    except (TypeError, ValueError):
        return f"₱{value}"


def _get_book_key(book: dict):
    return str(book.get("book_id") or book.get("id") or book.get("isbn") or book.get("title") or "unknown")


def _is_book_ordered(book: dict) -> bool:
    # Normalize status safely and check known ordered statuses
    status = None
    # try common status fields
    for key in ("status", "order_status", "order_state", "status_text"):
        if isinstance(book, dict) and key in book and book.get(key) is not None:
            status = book.get(key)
            break
    # handle nested order.status if present
    if status is None and isinstance(book.get("order"), dict):
        status = book["order"].get("status") or book["order"].get("status_text")

    if status is None:
        status_normalized = None
    else:
        try:
            status_normalized = str(status).strip().lower()
        except Exception:
            status_normalized = None

    ordered_statuses = {
        "ordered", "purchased", "completed",
        "pending", "to_pay", "to_claim", "claimed"
    }

    ordered_flags = [
        book.get("already_ordered"),
        book.get("is_ordered"),
        book.get("ordered"),
        status_normalized in ordered_statuses,
    ]

    # also consider orders placed in this session (cart -> checkout flow)
    try:
        ordered_items = st.session_state.get("ordered_items", [])
    except Exception:
        ordered_items = []

    book_key = _get_book_key(book)
    if book_key and book_key in ordered_items:
        return True

    return any(bool(flag) for flag in ordered_flags)


def _is_out_of_stock(book: dict) -> bool:
    stock = book.get("stock") or book.get("stock_quantity")
    if stock is None:
        return False
    try:
        return int(stock) <= 0
    except (TypeError, ValueError):
        return False


def _in_cart(book: dict, cart: list) -> bool:
    book_key = _get_book_key(book)
    return any(_get_book_key(item) == book_key for item in cart)


def _normalize_year(year_value):
    if year_value is None:
        return None
    try:
        digits = ''.join(ch for ch in str(year_value) if ch.isdigit())
        return int(digits) if digits else None
    except (ValueError, TypeError):
        return None


def show():
    auth_client = AuthClient()
    student_data = st.session_state.get("user_data") or {}
    if not student_data:
        student_data = auth_client.get_profile() or {}
        if student_data:
            st.session_state["user_data"] = student_data

    student_name = (
        student_data.get("name")
        or student_data.get("student_name")
        or student_data.get("full_name")
        or st.session_state.get("username", "Student")
    )

    # Extract enrolled subjects from session (e.g., "ITP220, ITP221, PE04")
    enrolled_subjects_str = student_data.get("current_enrolled_subjects", "") or ""
    enrolled_subjects = [s.strip() for s in enrolled_subjects_str.split(",") if s.strip()]

    # Extract year level string (no normalization, just display as-is)
    year_level_str = student_data.get("year_level") or student_data.get("year") or student_data.get("grade_level") or student_data.get("semester") or "N/A"

    st.markdown(
        """
        <style>
        .block-container {
        background-color: #ffffff !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        }
        .home-header {
            border: 1px solid #cbd5e1;
            background-color: #f8fafc;
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
        }
        .home-header h1 {
            margin: 0;
            color: #1e3a8a;
            font-size: 2.4rem;
        }
        .home-header p {
            margin: 6px 0 0;
            color: #475569;
            font-size: 1rem;
        }
        .book-card {
            border: 1px solid #e2e8f0;
            background-color: #ffffff;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .book-card-title {
            color: #1e40af;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .book-card-price {
            color: #065f46;
            font-size: 0.98rem;
            margin-bottom: 14px;
        }
        .status-pill {
            display: inline-block;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.92rem;
            color: #334155;
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
        }
        .status-pill.active {
            background: #dbeafe;
            color: #1d4ed8;
            border-color: #93c5fd;
        }
        .summary-card {
            border: 1px solid #e2e8f0;
            background-color: #ffffff;
            border-radius: 16px;
            padding: 22px;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 14px;
            font-size: 1rem;
            color: #334155;
        }
        .summary-row strong {
            color: #0f172a;
        }
        .stButton>button {
            background-color: #1d4ed8;
            color: white;
            border-radius: 999px;
            padding: 0.8rem 1.2rem;
            border: none;
        }
        .stButton>button:hover {
            background-color: #2563eb;
        }
        .stButton>button:disabled {
            background-color: #94a3b8;
            cursor: not-allowed;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='home-header'>
            <h1>Welcome {student_name}</h1>
            <p>Year level: {year_level_str}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "cart_items" not in st.session_state:
        st.session_state["cart_items"] = []

    book_client = BookClient()
    order_client = OrderClient()

    # Fetch all books (or narrow by program if your API supports it)
    all_books = book_client.filter_books() or []

    # -------------------------
    # Build maps for quick lookup
    # -------------------------
    book_id_map = {}
    book_title_map = {}
    for b in all_books:
        key = _get_book_key(b)
        bid = b.get("book_id") or b.get("id")
        if bid:
            book_id_map[str(bid)] = key
        title = b.get("title")
        if title:
            book_title_map[str(title).strip().lower()] = key

    # -------------------------
    # Fetch order history and resolve ordered book keys
    # -------------------------
    ordered_book_keys = set()
    user_id = student_data.get("user_id") or student_data.get("id") or student_data.get("uid")

    try:
        orders = order_client.list_orders() or []
    except Exception:
        orders = []

    if isinstance(orders, dict):
        orders = orders.get("data") or orders.get("orders") or []

    # For each order that belongs to the current user, collect ordered book keys
    for order in orders if isinstance(orders, list) else []:
        if not isinstance(order, dict):
            continue

        # If order has user_id and it doesn't match current user, skip
        if user_id and order.get("user_id") and str(order.get("user_id")) != str(user_id):
            continue

        # Skip cancelled orders entirely
        status = order.get("status")
        try:
            status_norm = str(status).strip().lower() if status is not None else ""
        except Exception:
            status_norm = ""
        if status_norm == "cancelled":
            continue

        # 1) If order already contains item objects with product/book ids, use them
        found_items_in_order = False
        for candidate_list_key in ("order_items", "order_items_detail", "items", "order_items_obj", "order_item_details"):
            items = order.get(candidate_list_key)
            if isinstance(items, list) and items:
                found_items_in_order = True
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    bid = it.get("book_id") or it.get("product_id") or it.get("product") or it.get("bookId")
                    if bid:
                        ordered_book_keys.add(_get_book_key({"book_id": bid}))
                        continue
                    if any(k in it for k in ("book_id", "title", "isbn", "id")):
                        ordered_book_keys.add(_get_book_key(it))
                # continue to next order after processing this key
                if found_items_in_order:
                    break

        if found_items_in_order:
            continue

        # 2) If order contains order_item_ids (like OB001), try to resolve via order detail endpoint
        order_item_ids = order.get("order_item_ids") or order.get("order_items") or []
        if isinstance(order_item_ids, list) and order_item_ids:
            req_id = order.get("request_id") or order.get("order_id") or order.get("id")
            detail = {}
            if req_id and hasattr(order_client, "get_order"):
                try:
                    detail = order_client.get_order(req_id) or {}
                except Exception:
                    detail = {}

            items = detail.get("order_items") or detail.get("items") or detail.get("order_item_details") or []
            if isinstance(items, list) and items:
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    bid = it.get("book_id") or it.get("product_id") or it.get("product")
                    if bid:
                        ordered_book_keys.add(_get_book_key({"book_id": bid}))
                        continue
                    if any(k in it for k in ("book_id", "title", "isbn", "id")):
                        ordered_book_keys.add(_get_book_key(it))
                # resolved via detail, move to next order
                if ordered_book_keys:
                    continue

            # 3) Fallback: try to match raw order_item_ids to book ids/titles (if backend used book ids directly)
            for raw in order_item_ids:
                try:
                    raw_s = str(raw).strip()
                except Exception:
                    raw_s = None
                if not raw_s:
                    continue
                if raw_s in book_id_map:
                    ordered_book_keys.add(book_id_map[raw_s])
                elif raw_s.lower() in book_title_map:
                    ordered_book_keys.add(book_title_map[raw_s.lower()])

            # 4) Last attempt: try resolving each order_item_id via BookClient if such method exists
            for oid in order_item_ids:
                try:
                    resolved = {}
                    if hasattr(book_client, "get_order_item"):
                        resolved = book_client.get_order_item(oid) or {}
                    elif hasattr(book_client, "fetch_order_item"):
                        resolved = book_client.fetch_order_item(oid) or {}
                    elif hasattr(book_client, "order_item_detail"):
                        resolved = book_client.order_item_detail(oid) or {}
                    else:
                        resolved = {}
                except Exception:
                    resolved = {}

                if isinstance(resolved, dict) and resolved:
                    bid = resolved.get("book_id") or resolved.get("product_id")
                    if bid:
                        ordered_book_keys.add(_get_book_key({"book_id": bid}))
                    elif isinstance(resolved.get("book"), dict):
                        ordered_book_keys.add(_get_book_key(resolved.get("book")))
                    elif resolved.get("title"):
                        ordered_book_keys.add(_get_book_key({"title": resolved.get("title")}))

    # -------------------------
    # End order-history cross-reference
    # -------------------------

    # Filter only those books whose subject_code matches enrolled subjects
    if enrolled_subjects:
        books = [book for book in all_books if (book.get("subject_code") or "").strip() in enrolled_subjects]
    else:
        books = []

    required_books = [book for book in books if not (_is_book_ordered(book) or (_get_book_key(book) in ordered_book_keys))]
    total_required_count = len(required_books)
    total_required_price = sum(float(book.get("price", 0) or 0) for book in required_books)

    page_col1, page_col2 = st.columns([3, 2], gap="large")

    with page_col1:
        st.markdown(
            """
            <div class='summary-card'>
                <h3 style='margin-top:0; color:#1e3a8a;'>Required books for your enrolled subjects</h3>
                <p style='margin:0; color:#475569;'>Select required titles and add them to your cart.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if books:
            for book in books:
                # st.write(book)  # Uncomment to inspect the book dict structure during debugging
                book_id = _get_book_key(book)
                title = book.get("title", "Untitled")
                price_text = _format_price(book.get("price", 0))
                # Determine already ordered by either book-level flags/status or cross-referenced order history
                already_ordered = _is_book_ordered(book) or (book_id in ordered_book_keys)
                out_of_stock = _is_out_of_stock(book)
                in_cart = _in_cart(book, st.session_state["cart_items"])

                status_text = None
                status_class = "status-pill"
                if already_ordered:
                    status_text = "Already ordered"
                elif out_of_stock:
                    status_text = "Out of stock"
                elif in_cart:
                    status_text = "Added to cart"
                    status_class = "status-pill active"

                st.markdown("<div style='border-bottom:1px solid #e2e8f0; margin:8px 0;'></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='book-card-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='book-card-price'>{price_text}</div>", unsafe_allow_html=True)

                if status_text:
                    st.markdown(f"<div class='{status_class}'>{status_text}</div>", unsafe_allow_html=True)
                else:
                    if st.button("Add to Cart", key=f"add_{book_id}"):
                        # re-check in_cart to avoid duplicates on rapid clicks
                        if not _in_cart(book, st.session_state.setdefault("cart_items", [])):
                            st.session_state.setdefault("cart_items", []).append({
                                "id": _get_book_key(book),
                                "product_id": book.get('book_id'),
                                "unit_price": float(book.get('price', 0) or 0),
                                "quantity": 1,
                                "subtotal": float(book.get('price', 0) or 0),
                                "title": book.get('title'),
                                "info": book.get('program_related')
                            })
                            st.success(f"Added {book.get('title','Unknown')} to cart!")

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No required books found for your current enrolled subjects.")

    with page_col2:
        st.markdown(
            """
            <div class='summary-card'>
                <h3 style='margin-top:0; color:#1e3a8a;'>Cart summary</h3>
            """,
            unsafe_allow_html=True,
        )

        cart_items = st.session_state["cart_items"]
        cart_count = len(cart_items)
        cart_total = sum(float(item.get("unit_price", 0) or 0) * item.get("quantity", 1) for item in cart_items)

        st.markdown(f"<div class='summary-row'><strong>Required books:</strong><span>{total_required_count}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Required total:</strong><span>{_format_price(total_required_price)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Selected books:</strong><span>{cart_count}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Cart subtotal:</strong><span>{_format_price(cart_total)}</span></div>", unsafe_allow_html=True)

        if cart_count == 0:
            st.info("Your cart is empty. Add required books from the left panel.")
        else:
            st.success("Your cart has been updated.")

        st.markdown("</div>", unsafe_allow_html=True)


    st.write("")
    st.write("")
    st.markdown(
        """
        <div style='color:#1e3a8a;'>
            <h1 style='color:#1e3a8a;'>About this app</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='color:#1e3a8a;'>
        <p>
        This web application is designed to help students easily find and request an order for their required books based on their current enrolled subjects. This app automatically identifies the student's enrolled subjects and displays the required books. 
        It automates the listing of required books, sum them app to compute the total price, and allows students and admins to manage their orders efficiently.
        </p>
        <p> </p>

        <p>1) For the user page, the app consists of multiple pages each with a specific function.</p>
        <p>2) The Home page displays the required books based on the student's enrolled subjects, allowing them to add books to their cart.</p> 
        <p>3) The Books page provides a comprehensive list of all available books, while the Uniforms page lists the RTU uniforms.</p>
        <p>4) The Checkout Page allows students to review their cart and place orders, while the Order Status page lets them track their order progress.</p> </p>
        <p>5) The Order Status page allows students to track the progress of their current orders.</p>
        <p>6) The Order History page shows past orders.</p>
        <p>7) The Account page allows users to view their profile.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
