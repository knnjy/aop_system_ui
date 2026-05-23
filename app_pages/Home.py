import streamlit as st
from services.auth_client import AuthClient
from services.book_client import BookClient


def _format_price(value):
    try:
        amount = float(value)
        return f"₱{amount:,.2f}"
    except (TypeError, ValueError):
        return f"₱{value}"


def _get_book_key(book: dict):
    return str(book.get("book_id") or book.get("id") or book.get("isbn") or book.get("title") or "unknown")


def _is_book_ordered(book: dict) -> bool:
    ordered_flags = [
        book.get("already_ordered"),
        book.get("is_ordered"),
        book.get("ordered"),
        book.get("status") in ["ordered", "purchased", "completed"],
    ]
    return any(bool(flag) for flag in ordered_flags)


def _is_out_of_stock(book: dict) -> bool:
    stock = book.get("stock")
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
        # Extract digits from strings like "2nd year" or "Semester 1"
        digits = ''.join(ch for ch in str(year_value) if ch.isdigit())
        return int(digits) if digits else None
    except (ValueError, TypeError):
        return None



def show():

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

    auth_client = AuthClient()
    student_data = st.session_state.get("user_data") or {}
    if not student_data:
        student_data = auth_client.get_profile() or {}
        if student_data:
            st.session_state["user_data"] = student_data

    student_name = student_data.get("name") or student_data.get("student_name") or student_data.get("full_name") or st.session_state.get("username", "Student")
    year_level = student_data.get("year_level") or student_data.get("year") or student_data.get("grade_level") or student_data.get("semester")
    program = student_data.get("program")
    normalized_year = _normalize_year(year_level)

    st.markdown(
        f"""
        <div class='home-header'>
            <h1>Welcome {student_name}</h1>
            <p>Year level: {normalized_year}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "cart_items" not in st.session_state:
        st.session_state["cart_items"] = []

    book_client = BookClient()
    if isinstance(normalized_year, int):
        books = book_client.filter_books(semester_available=normalized_year, program_related=program) or []
    else:
        books = []

    required_books = [book for book in books if not _is_book_ordered(book)]
    total_required_count = len(required_books)
    total_required_price = sum(float(book.get("price", 0) or 0) for book in required_books)

    page_col1, page_col2 = st.columns([3, 2], gap="large")

    with page_col1:
        st.markdown(
            """
            <div class='summary-card'>
                <h3 style='margin-top:0; color:#1e3a8a;'>Required books for this semester</h3>
                <p style='margin:0; color:#475569;'>Select required titles and add them to your cart.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if books:
            for book in books:
                book_id = _get_book_key(book)
                title = book.get("title", "Untitled")
                price_text = _format_price(book.get("price", 0))
                already_ordered = _is_book_ordered(book)
                out_of_stock = _is_out_of_stock(book)
                in_cart = any(item["id"] == book_id for item in st.session_state["cart_items"])

                status_text = None
                status_class = "status-pill"
                if already_ordered:
                    status_text = "Already ordered"
                elif out_of_stock:
                    status_text = "Out of stock"
                elif in_cart:
                    status_text = "Added to cart"
                    status_class = "status-pill active"

                st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='book-card-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='book-card-price'>{price_text}</div>", unsafe_allow_html=True)

                if status_text:
                    st.markdown(f"<div class='{status_class}'>{status_text}</div>", unsafe_allow_html=True)
                else:
                    if st.button("Add to Cart", key=f"add_{book_id}"):
                        if not in_cart:
                            st.session_state["cart_items"].append({
                                "id": book_id,
                                "title": title,
                                "info": book.get("subject_code", ""),
                                "price": float(book.get("price", 0)),
                                "quantity": 1
                            })
                        st.success(f"Added {title} to cart")

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No required books found for your current semester.")

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
        cart_total = sum(float(item.get("price", 0) or 0) * item.get("quantity", 1) for item in cart_items)

        st.markdown(f"<div class='summary-row'><strong>Required books:</strong><span>{total_required_count}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Required total:</strong><span>{_format_price(total_required_price)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Selected books:</strong><span>{cart_count}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-row'><strong>Cart subtotal:</strong><span>{_format_price(cart_total)}</span></div>", unsafe_allow_html=True)

        if cart_count == 0:
            st.info("Your cart is empty. Add required books from the left panel.")
        else:
            st.success("Your cart has been updated.")

        st.markdown("</div>", unsafe_allow_html=True)
