import streamlit as st
from services.book_client import BookClient

def show():
    book_client = BookClient()

    # --- Inject CSS (Blue, White, Gold Theme) ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .book-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .book-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            cursor: pointer;
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
        .book-info { padding: 12px; }
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

    st.markdown("<div class='book-title'>NO TITLE Book Page</div>", unsafe_allow_html=True)

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
        st.markdown(f"""
            <div class='detail-box'>
                <b>Price:</b> ₱{book.get('price','0')} <br>
                <b>Stock:</b> {book.get('stock_quantity','0')} <br>
                <b>Program:</b> {book.get('program_related','')} <br>
                <b>Availability:</b> {book.get('availability','')}
            </div>
        """, unsafe_allow_html=True)

        # Buttons for Detail View
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("⬅️ Back to List"):
                st.session_state["selected_book"] = None
        with col2:
            if book.get("availability","").lower() == "available":
                if st.button("🛒 Add to Cart", key=f"detail_cart_{book.get('book_id','0')}"):
                    if "cart" not in st.session_state:
                        st.session_state["cart"] = []
                    st.session_state["cart"].append(book)
                    st.success(f"Added {book.get('title')} to cart!")
        return

    # --- LIST VIEW ---
    icons = {"ICS": "💻", "CEA": "📐", "CAS": "📖", "CBEA": "📊"}
    cols = st.columns(2)

    for i, book in enumerate(books):
        with cols[i % 2]:
            icon = icons.get(book.get("program_related", ""), "📚")

            st.markdown(f"""
                <div class='book-card'>
                    <div class='book-img-placeholder'>{icon}</div>
                    <div class='book-info'>
                        <div class='book-name'>{book.get('title','Unknown')}</div>
                        <div class='book-type'>{book.get('program_related','')} | Stock: {book.get('stock_quantity',0)}</div>
                        <div class='book-price'>₱{book.get('price','0')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Horizontal buttons
            btn_col1, btn_col2 = st.columns([1,1])
            with btn_col1:
                if st.button("🔎 View Details", key=f"view_{book.get('book_id',i)}"):
                    st.session_state["selected_book"] = book
            with btn_col2:
                if book.get("availability","").lower() == "available":
                    if st.button("🛒 Add to Cart", key=f"cart_{book.get('book_id',i)}"):
                        if "cart" not in st.session_state:
                            st.session_state["cart"] = []
                        st.session_state["cart"].append(book)
                        st.success(f"Added {book.get('title')} to cart!")

# if __name__ == "__main__":
#     show()
