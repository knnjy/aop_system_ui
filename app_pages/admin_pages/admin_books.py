import time

import streamlit as st
from components.add_book import add_book_form
from components.update_book import update_book_form
from services.book_client import BookClient

def btn():
        # Inject CSS for round icon button
    st.markdown(
        """
        <style>
        .round-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;   /* fixed width */
            height: 50px;  /* fixed height */
            border-radius: 50%;
            border: none;
            background-color: #1e3a8a;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;    /* prevent extra spacing */
        }
        .round-button:hover {
            background-color: #3b82f6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Render as HTML so global button styles don't interfere
    st.markdown("<button class='round-button'>➕</button>", unsafe_allow_html=True)




def show():
    book_client = BookClient()

    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .page-title {
            font-size:32px;
            font-weight:800;
            color:#1e3a8a;
            margin-bottom:10px;
            text-align:left;   /* ✅ align to left */
        }
        .filter-box {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .filter-title { font-size:18px; font-weight:700; color:#1e3a8a; margin-bottom:10px; }
        .book-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 10px;
        }
        .book-img-placeholder {
            background-color: #e2e8f0;
            width: 100%;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }
        .book-name { font-size:16px; font-weight:700; color:#1e3a8a; }
        .book-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .book-type { font-size:12px; color:#64748b; margin-top:2px; }
        .detail-box {
            background-color: #fefce8;
            border: 1px solid #facc15;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- EDIT VIEW (MUST BE HERE FIRST) ---
    if "selected_book" in st.session_state and st.session_state.get("edit_mode", False):
        update_book_form(st.session_state["selected_book"])
        st.stop()

    # --- Page Title ---
    st.markdown("<div class='page-title'>RTU Book Page</div>", unsafe_allow_html=True)
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        search_query = st.text_input(
            "Search uniforms...",
            key="admin_uniform_search",
            label_visibility="collapsed",
            placeholder="Search uniforms..."
        )

    with top_col2:
        # Only render the button here
        if st.button("➕ Add Book", key="add_uniform_btn", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.get("show_add_form", False)

    # --- New line after the columns ---
    if st.session_state.get("show_add_form", False):
        add_book_form()

    # --- Back to List button (top left, only in detail view) ---
    if "selected_book" in st.session_state and st.session_state["selected_book"]:
        col_back, _ = st.columns([1,3])
        with col_back:
            if st.button("⬅️ Back to List", key="back_btn_top"):
                st.session_state["selected_book"] = None
                st.rerun()

    # --- Fetch Books ---
    try:
        books = book_client.list_books() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    if not books:
        st.warning("No books found.")
        return

    # --- DETAIL VIEW ---
    if "selected_book" in st.session_state and st.session_state["selected_book"]:
        book = st.session_state["selected_book"]

        # 2-column layout: Left = Image, Right = Title + Info + Controls
        col_img, col_info = st.columns([1.2, 1.8])

        with col_img:
            path = book.get("subject_code", None)
            if path:
                st.image(f"http://localhost:9000/static/images/books/{path}.jpg", use_container_width=True)  # ✅ fixed
            else:
                st.markdown("<div class='book-img-placeholder'>📚</div>", unsafe_allow_html=True)

        with col_info:
            # Title moved here
            st.markdown(f"<div class='page-title'>{book.get('title','Unknown')}</div>", unsafe_allow_html=True)

            # Info box
            st.markdown(f"""
                <div class='detail-box'>
                    <b>Price:</b> ₱{book.get('price','0')} <br>
                    <b>Stock:</b> {book.get('stock_quantity','0')} <br>
                    <b>Program:</b> {book.get('program_related','')}
                </div>
            """, unsafe_allow_html=True)

            # Horizontal controls
            col1, col2 = st.columns([1,2], gap="medium")
            with col1:
                qty = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1,
                                      key=f"detail_qty_{book.get('book_id','0')}")
            with col2:
                if st.button("🛒 Add to Cart", key=f"cart_{book.get('book_id','0')}"):
                    st.session_state.setdefault("cart_items", []).append({
                        "id": book.get('book_id'),
                        "product_id": book.get('book_id'),
                        "unit_price": float(book.get('price', 0) or 0),
                        "quantity": 1,
                        "subtotal": float(book.get('price', 0) or 0),
                        "title": book.get('title'),
                        "info": book.get('program_related')
                    })
                    st.success(f"Added {book.get('title','Unknown')} to cart!")
        return
    # --- LIST VIEW ---
    if st.session_state.get("update_success"):
        st.toast(st.session_state["update_success"])
        st.session_state["update_success"] = None
    if st.session_state.get("archive_success"):
        st.toast(st.session_state["archive_success"])
        st.session_state["archive_success"] = None
    # --- LIST VIEW (Filters + Grid) ---
    filter_col, book_col = st.columns([1,3])
    with filter_col:
        st.markdown("<div class='filter-box'><div class='filter-title'>📑 Filters</div>", unsafe_allow_html=True)
        search_query = st.text_input("🔎 Search books...", key="book_search")
        category = st.selectbox("📂 Category", ["All", "ICS", "CEA", "CAS", "CBEA"], key="book_category")
        price_range = st.selectbox("💰 Price Range", ["All", "₱0-₱300", "₱301-₆00", "₱601+"], key="book_price_range")
        st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered_books = []
    for book in books:
        try:
            title = str(book.get("title", ""))
            program = str(book.get("program_related", ""))
            price_val = float(book.get("price", 0) or 0)

            title_match = search_query.lower() in title.lower() if search_query else True
            category_match = (category == "All" or program == category)

            if price_range == "₱0-₱300":
                price_match = price_val <= 300
            elif price_range == "₱301-₆00":
                price_match = 301 <= price_val <= 600
            elif price_range == "₱601+":
                price_match = price_val >= 601
            else:
                price_match = True

            if title_match and category_match and price_match:
                filtered_books.append(book)
        except Exception as e:
            st.warning(f"Skipped a book due to invalid data: {e}")
            continue

    if not filtered_books:
        st.warning("No books match your filters.")
        return

    # --- Grid Layout ---
    icons = {"ICS": "💻", "CEA": "📐", "CAS": "📖", "CBEA": "📊"}
    for i in range(0, len(filtered_books), 3):
        row_books = filtered_books[i:i+3]
        cols = book_col.columns(3)

        for j, book in enumerate(row_books):
            with cols[j]:
                icon = icons.get(book.get("program_related", ""), "📚")
                path = book.get("subject_code", None)
                book_index = i + j

                if path:
                    st.image(f"http://localhost:9000/static/images/books/{path}.jpg", width=150)
                else:
                    st.markdown(f"<div class='book-img-placeholder'>{icon}</div>", unsafe_allow_html=True)

                st.markdown(f"""
                    <div class='book-card'>
                        <div class='book-name'>{book.get('title','Unknown')}</div>
                        <div class='book-type'>{book.get('program_related','')} | Stock: {book.get('stock_quantity',0)}</div>
                        <div class='book-price'>₱{book.get('price','0')}</div>
                    </div>
                """, unsafe_allow_html=True)

                # row1, row2 = st.columns([3,1])   # wider column for View Details, narrower for ⋮
                # with row1:
                #     if st.button("🔎 View Details", key=f"view_{book_index}"):
                #         st.session_state["selected_book"] = book
                #         st.rerun()
                # with row2:
                #     if st.button("⋮", key=f"menu_btn_{book_index}", help="More options"):
                #         if st.session_state.get("open_menu") == book_index:
                #             st.session_state["open_menu"] = None
                #         else:
                #             st.session_state["open_menu"] = book_index
                if st.button("🔎 View Details", key=f"view_{book_index}"):
                    st.session_state["selected_book"] = book
                    st.rerun()
                
                if st.button("⋮", key=f"menu_btn_{book_index}", help="More options"):
                    if st.session_state.get("open_menu") == book_index:
                        st.session_state["open_menu"] = None
                    else:
                        st.session_state["open_menu"] = book_index

                # --- Show menu actions when open ---
                if st.session_state.get("open_menu") == book_index:
                    with st.container():
                        st.markdown("<div class='menu-box'>", unsafe_allow_html=True)
                        if st.button("✏️ Edit", key=f"edit_{book_index}"):
                            st.session_state["selected_book"] = book
                            st.session_state["edit_mode"] = True
                            st.session_state["open_menu"] = None
                            st.rerun()
                            
                        if st.button("🗑️ Archive", key=f"delete_{book_index}"):
                            success = book_client.delete_book(book.get("book_id"))
                            if success:
                                # Save toast message in session state
                                st.session_state["open_menu"] = None
                                st.session_state["archive_success"] = f"Archived '{book.get('title','Unknown')}' successfully!"
                                st.rerun()
                            else:
                                st.session_state["archive_error"] = "❌ Failed to archive book."
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- Show menu actions ---
                if st.session_state.get("open_menu") == book_index:
                    with st.container():
                        st.markdown("<div class='menu-box'>", unsafe_allow_html=True)
