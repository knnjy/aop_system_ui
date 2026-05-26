import streamlit as st
from services import book_client
from services.book_client import BookClient


def show():

    st.markdown(
        """
        <h1 style='color:#1e3a8a;'>
            Admin Book Management
        </h1>
        """,
        unsafe_allow_html=True
    )

    book_client = BookClient()

    # =========================
    # ADD NEW BOOK FORM
    # =========================
    # Initialize toggle state
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

    # Button to toggle form visibility
    if st.button("➕ Add Book"):
        st.session_state.show_add_form = not st.session_state.show_add_form

    # Conditionally show the form
    if st.session_state.show_add_form:
        st.markdown("### Add New Book")

        with st.form("add_book_form"):

            subject_code = st.text_input("Subject Code")
            title = st.text_input("Book Title")
            price = st.number_input("Price", min_value=0.0)
            stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
            program_related = st.text_input("Program Related")
            semester_available = st.number_input(
                "Semester Available",
                min_value=1,
                max_value=4,
                step=1
            )

            submitted = st.form_submit_button("Add Book")

            if submitted:

                book_data = {
                    "subject_code": subject_code,
                    "title": title,
                    "price": price,
                    "stock_quantity": stock_quantity,
                    "semester_available": semester_available,
                    "program_related": program_related
                }

                success = book_client.add_book(book_data)

                if success:
                    st.success("Book added successfully!")
                else:
                    st.error("Failed to add book.")

def show():
    book_client = BookClient()

    # --- CSS Styling ---
    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .book-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .book-card {
            background-color:#f8fafc;
            border-radius:12px;
            border:1px solid #e2e8f0;
            margin-bottom:15px;
            overflow:hidden;
            box-shadow:0 2px 8px rgba(0,0,0,0.05);
            position:relative;
        }
        .book-img-placeholder {
            background-color:#e2e8f0;
            width:100%;
            height:200px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:48px;
        }
        .book-info { padding:12px; }
        .book-name { font-size:15px; font-weight:700; color:#1e3a8a; }
        .book-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .book-type { font-size:12px; color:#64748b; margin-top:2px; }

        /* 3-dot menu */
        .menu-container { position:absolute; top:10px; right:10px; }
        .menu-button {
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:8px;
            font-size:18px;
            width:32px;
            height:32px;
            display:flex;
            align-items:center;
            justify-content:center;
            cursor:pointer;
            box-shadow:0 1px 3px rgba(0,0,0,0.1);
        }
        .menu-box {
            position:absolute;
            top:40px;
            right:0;
            background:#fff;
            border:1px solid #e2e8f0;
            border-radius:8px;
            box-shadow:0 4px 10px rgba(0,0,0,0.15);
            padding:6px;
            width:120px;
            z-index:100;
        }
        .menu-box button {
            display:block;
            width:100%;
            padding:8px 10px;
            font-size:14px;
            border:none;
            background:none;
            text-align:left;
            cursor:pointer;
            border-radius:6px;
        }
        .menu-box button:hover { background:#f1f5f9; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='book-title'>Admin Book Management</div>", unsafe_allow_html=True)

    # --- Fetch Books ---
    try:
        books = book_client.list_books() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    if not books:
        st.warning("No books found.")
        return

    # --- Session State ---
    if "selected_book" not in st.session_state:
        st.session_state["selected_book"] = None
    if "open_menu" not in st.session_state:
        st.session_state["open_menu"] = None

    selected_book = st.session_state.get("selected_book")

    # --- DETAIL VIEW ---
    if selected_book:
        book = selected_book
        st.markdown(f"<div class='book-title'>{book.get('title','Unknown')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='detail-box'>
                <b>Author:</b> {book.get('author','')} <br>
                <b>Program:</b> {book.get('program_related','')} <br>
                <b>Price:</b> ₱{book.get('price','0')} <br>
                <b>Stock:</b> {book.get('stock_quantity','0')} <br>
                <b>Semester Available:</b> {book.get('semester_available','')}
            </div>
        """, unsafe_allow_html=True)

        if st.button("⬅️ Back to List", key="back_to_list"):
            st.session_state["selected_book"] = None
            st.rerun()
        return

    # --- LIST VIEW (Pop-out 3-dot menu) ---
    cols = st.columns(2)
    icons = {"ICS":"💻","CEA":"📐","CAS":"📖","CBEA":"📊"}
    for i, book in enumerate(books):
        with cols[i % 2]:
            icon = icons.get(book.get("program_related",""),"📚")

            # Card layout
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

            # --- Streamlit-native 3-dot menu button ---
            menu_cols = st.columns([20, 1])
            with menu_cols[1]:
                if st.button("⋮", key=f"menu_btn_{i}", help="More options"):
                    # toggle menu open state for this item
                    if st.session_state.get("open_menu") == i:
                        st.session_state["open_menu"] = None
                    else:
                        st.session_state["open_menu"] = i

            # --- Show menu actions when open ---
            if st.session_state.get("open_menu") == i:
                # small container for actions
                with st.container():
                    st.markdown("<div class='menu-box'>", unsafe_allow_html=True)
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state["selected_book"] = book
                        st.session_state["open_menu"] = None
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        success = book_client.delete_book(book.get("book_id"))
                        if success:
                            st.success(f"Deleted {book.get('title','Unknown')}")
                            st.session_state["open_menu"] = None
                            st.rerun()
                        else:
                            st.subheader("History")
                            st.error("Failed to delete book.")
                    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    show()
