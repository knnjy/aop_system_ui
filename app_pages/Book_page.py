import streamlit as st
from services.book_client import BookClient

def show():
    book_client = BookClient()

    # --- Inject CSS (Blue, White, Gold Theme) ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .book-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .filter-box {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .filter-title {
            font-size:18px; font-weight:700; color:#1e3a8a; margin-bottom:10px;
        }
        .book-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            cursor: pointer;
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
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='book-title'>RTU Book Page</div>", unsafe_allow_html=True)

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

        st.markdown(f"<div class='book-title'>{book.get('title','Unknown')}</div>", unsafe_allow_html=True)

        # --- Image ---
        path = book.get("subject_code", None)
        if path:
            st.image(f"http://localhost:9000/static/images/books/{path}.jpg", width=500)
        else:
            st.markdown("<div class='book-img-placeholder'>📚</div>", unsafe_allow_html=True)

        # --- Info Box ---
        st.markdown(f"""
            <div class='detail-box'>
                <b>Price:</b> ₱{book.get('price','0')} <br>
                <b>Stock:</b> {book.get('stock_quantity','0')} <br>
                <b>Program:</b> {book.get('program_related','')}
            </div>
        """, unsafe_allow_html=True)

        # --- Horizontal Controls ---
        def clear_selected_book():
            st.session_state["selected_book"] = None
            st.rerun()

        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            st.button("⬅️ Back to List", on_click=clear_selected_book)
        with col2:
            qty = st.number_input("", min_value=1, max_value=10, value=1, step=1,
                                  label_visibility="collapsed",
                                  key=f"detail_qty_{book.get('book_id','0')}")
        with col3:
            if st.button("🛒 Add to Cart", key=f"detail_cart_{book.get('book_id','0')}"):
                st.session_state.setdefault("cart_items", []).append({
                    "product_id": book.get('book_id'),
                    "unit_price": float(book.get('price', 0) or 0),
                    "quantity": qty,
                    "subtotal": float(book.get('price', 0) or 0) * qty,
                    "title": book.get('title'),
                    "info": book.get('program_related')
                })
                st.success(f"Added {qty} x {book.get('title','Unknown')} to cart!")
        return

    # --- LIST VIEW (Filters + Grid) ---
    filter_col, book_col = st.columns([1,3])

    with filter_col:
        st.markdown("<div class='filter-box'><div class='filter-title'>📑 Filters</div>", unsafe_allow_html=True)
        search_query = st.text_input("🔎 Search books...", key="book_search")
        category = st.selectbox("📂 Category", ["All", "ICS", "CEA", "CAS", "CBEA"], key="book_category")
        price_range = st.selectbox("💰 Price Range", ["All", "₱0-₱300", "₱301-₱600", "₱601+"], key="book_price_range")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Apply Filters ---
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
            elif price_range == "₱301-₱600":
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

    # --- No Match ---
    if not filtered_books:
        st.warning("No books found for the selected filter.")
        return

    # --- Grid Layout (2 cards per row) ---
    icons = {"ICS": "💻", "CEA": "📐", "CAS": "📖", "CBEA": "📊"}
    with book_col:
        for i in range(0, len(filtered_books), 2):
            row_books = filtered_books[i:i+2]
            cols = st.columns(2)
        
            for j, book in enumerate(row_books):
                with cols[j]:
                    try:
                        icon = icons.get(book.get("program_related", ""), "📚")
                        path = book.get("subject_code", None)

                        # --- Image ---
                        if path:
                            try:
                                st.image(f"http://localhost:9000/static/images/books/{path}.jpg", width=150)
                            except:
                                st.markdown(f"<div class='book-img-placeholder'>{icon}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='book-img-placeholder'>{icon}</div>", unsafe_allow_html=True)

                        # --- Card Info ---
                        st.markdown(f"""
                            <div class='book-card'>
                                <div class='book-name'>{book.get('title','Unknown')}</div>
                                <div class='book-type'>{book.get('program_related','')} | Stock: {book.get('stock_quantity',0)}</div>
                                <div class='book-price'>₱{book.get('price','0')}</div>
                            </div>
                        """, unsafe_allow_html=True)

                        # --- Buttons ---
                        if st.button("🔎 View Details", key=f"view_{book.get('book_id',i+j)}"):
                            st.session_state["selected_book"] = book
                            st.rerun()
                        if str(book.get("availability","")).lower() == "available":
                            if st.button("🛒 Add to Cart", key=f"cart_{book.get('book_id',i+j)}"):
                                st.session_state.setdefault("cart_items", []).append({
                                "product_id": book.get('book_id'),
                                "unit_price": float(book.get('price', 0) or 0),
                                "quantity": qty,
                                "subtotal": float(book.get('price', 0) or 0) * qty,
                                "title": book.get('title'),
                                "info": book.get('program_related')
                            })
                            st.success(f"Added {qty} x {book.get('title','Unknown')} to cart!")

                    except Exception as e:
                        st.warning(f"Skipped rendering a book card due to error: {e}")
                        continue
