import streamlit as st
from services.book_client import BookClient

def show():
    book_client = BookClient()

    # Inject CSS (copied/adapted from Uniform Page)
    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .book-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .filter-box {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .filter-title { font-size:18px; font-weight:700; color:#1e3a8a; margin-bottom:15px; }
        .book-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 0;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            cursor: pointer;
        }
        .book-img-placeholder {
            background-color: #e2e8f0;
            width: 100%;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        .book-info { padding: 12px; }
        .book-name { font-size:15px; font-weight:700; color:#1e3a8a; }
        .book-price { font-size:14px; color:#1e3a8a; font-weight:600; margin-top:4px; }
        .book-type { font-size:12px; color:#64748b; margin-top:2px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='book-title'>Book Page</div>", unsafe_allow_html=True)

    # Fetch books
    try:
        books = book_client.list_books() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    if not books:
        st.warning("No books found.")
        return

    # Layout: filters left, products right
    col_filter, col_products = st.columns([1, 3])

    with col_filter:
        st.markdown("""
            <div class='filter-box'>
                <div class='filter-title'>Filters</div>
            </div>
        """, unsafe_allow_html=True)

        search_query = st.text_input("Search", placeholder="Search books...", key="book_search")
        category = st.selectbox("Category", ["All", "ICS", "CEA", "CAS", "CBEA"], key="book_category")
        price_range = st.selectbox("Price Range", ["All", "₱0-₱300", "₱301-₱600", "₱601+"], key="book_price")
        availability = st.selectbox("Availability", ["All", "Available", "Unavailable"], key="book_availability")

    # Apply filters
    filtered = []
    for b in books:
        if str(b.get("is_deleted", "False")).lower() == "true":
            continue
        if search_query and search_query.lower() not in b.get("title", "").lower():
            continue
        if category != "All" and category.lower() not in b.get("program_related", "").lower():
            continue
        if availability != "All" and availability.lower() != b.get("availability", "").lower():
            continue
        if price_range != "All":
            price = float(b.get("price", 0))
            if price_range == "₱0-₱300" and price > 300:
                continue
            elif price_range == "₱301-₱600" and not (301 <= price <= 600):
                continue
            elif price_range == "₱601+" and price < 601:
                continue
        filtered.append(b)

    with col_products:
        if not filtered:
            st.warning("No books match your filters.")
            return

        # Book icons per category
        icons = {
            "ICS": "💻",
            "CEA": "📐",
            "CAS": "📖",
            "CBEA": "📊",
        }

        cols = st.columns(2)
        for i, book in enumerate(filtered):
            with cols[i % 2]:
                icon = icons.get(book.get("program_related", ""), "📚")

                st.markdown(f"""
                    <div class='book-card'>
                        <div class='book-img-placeholder'>{icon}</div>
                        <div class='book-info'>
                            <div class='book-name'>{book.get('title', 'Unknown')}</div>
                            <div class='book-type'>{book.get('program_related', '')} | Stock: {book.get('stock_quantity', 0)}</div>
                            <div class='book-price'>₱{book.get('price', '0')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if book.get("availability", "").lower() == "available":
                    if st.button("Add to Cart", key=f"book_{book.get('book_id', i)}"):
                        if "cart" not in st.session_state:
                            st.session_state["cart"] = []
                        st.session_state["cart"].append(book)
                        st.success(f"Added {book.get('title')} to cart!")

if __name__ == "__main__":
    show()
