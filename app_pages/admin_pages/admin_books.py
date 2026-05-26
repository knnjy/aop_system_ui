import streamlit as st
from services import book_client
from services.book_client import BookClient

def show_add_book(book_client):

    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

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

            image_file = st.file_uploader(
                "Upload Book Image",
                type=["jpg"]
            )

            submitted = st.form_submit_button("Add Book")

            if submitted:

                if not subject_code or not title or price <= 0 or stock_quantity <= 0:
                    st.error("Please complete all required fields.")
                    return

                if image_file:
                    filename_no_ext = image_file.name.split(".")[0]

                    if filename_no_ext != subject_code:
                        st.error(
                            f"Image filename must match subject code ({subject_code})"
                        )
                        return

                    uploaded = book_client.book_upload_image(image_file)

                    if not uploaded:
                        st.error("Image upload failed")
                        return

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
                    st.session_state.show_add_form = False
                    st.rerun()
                else:
                    st.error("Failed to add book.")

def show():
    book_client = BookClient()

    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .book-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }

        .book-card-wrapper {
            display: flex;
            flex-direction: column;
            border-radius: 0 0 12px 12px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 5px;
            background: #f8fafc;
        }
        .book-card-img {
            width: 100%;
            height: 220px;
            overflow: hidden;
            flex-shrink: 0;
            background: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 72px;
        }
        .book-card-img img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }
        .book-card-body {
            padding: 10px 12px 12px 12px;
            background: #f8fafc;
            display: flex;
            flex-direction: column;
        }
        .book-name  { font-size:15px; font-weight:700; color:#1e3a8a; }
        .book-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .book-type  { font-size:12px; color:#64748b; margin-top:2px; }

        .detail-box {
            background-color: #fefce8;
            border: 1px solid #facc15;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .admin-action-note { margin-top:12px; font-size:13px; color:#475569; }
        .deleted-section-title { font-size:20px; font-weight:700; color:#dc2626; margin-top:32px; margin-bottom:12px; }
        .deleted-row {
            display: flex;
            align-items: center;
            background: #fff1f2;
            border: 1px solid #fecaca;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }
        .deleted-book-name { font-size:14px; font-weight:700; color:#991b1b; }
        .deleted-book-meta { font-size:12px; color:#64748b; margin-top:2px; }

        div[data-testid="stPopover"] > div > button {
            background: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            font-size: 20px !important;
            width: 36px !important;
            min-width: 36px !important;
            height: 36px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #475569 !important;
        }
        div[data-testid="stPopover"] > div > button:hover { background: #e2e8f0 !important; }
        div[data-testid="stPopover"] > div > button svg { display: none !important; }
        div[data-testid="stPopover"] > div > button::after { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    try:
        books = book_client.list_books() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    # --- Session State ---
    st.session_state.setdefault("admin_selected_book_id", None)
    st.session_state.setdefault("admin_edit_mode", False)
    st.session_state.setdefault("admin_hidden_book_ids", [])
    st.session_state.setdefault("admin_deleted_book_ids", [])
    st.session_state.setdefault("show_add_form", False)

    ICONS = {"ICS": "💻", "CEA": "📐", "CAS": "📖", "CBEA": "📊"}
    BASE_IMG = "http://localhost:9000/static/images/books"

    def select_book(book_id, edit_mode=False):
        st.session_state["admin_selected_book_id"] = book_id
        st.session_state["admin_edit_mode"] = edit_mode

    def hide_book(book_id):
        ids = set(str(b) for b in st.session_state["admin_hidden_book_ids"])
        ids.add(str(book_id))
        st.session_state["admin_hidden_book_ids"] = list(ids)

    def restore_book(book_id):
        ids = set(str(b) for b in st.session_state["admin_hidden_book_ids"])
        ids.discard(str(book_id))
        st.session_state["admin_hidden_book_ids"] = list(ids)

    def soft_delete_book(book_id):
        ids = set(str(b) for b in st.session_state["admin_deleted_book_ids"])
        ids.add(str(book_id))
        st.session_state["admin_deleted_book_ids"] = list(ids)
        hide_book(book_id)

    def restore_deleted_book(book_id):
        ids = set(str(b) for b in st.session_state["admin_deleted_book_ids"])
        ids.discard(str(book_id))
        st.session_state["admin_deleted_book_ids"] = list(ids)
        restore_book(book_id)

    # =========================
    # PAGE TITLE + SEARCH + ADD
    # =========================
    st.markdown(
        "<h1 style='color:#1e3a8a; margin-bottom:16px;'>Admin Book Management</h1>",
        unsafe_allow_html=True
    )

    search_col, add_col = st.columns([5, 1])
    with search_col:
        search_query = st.text_input(
            "Search books...",
            key="admin_book_search",
            label_visibility="collapsed",
            placeholder="Search books...",
        )
    with add_col:
        if st.button("➕ Add Book", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form

    show_add_book(book_client)

    # --- Derived sets ---
    hidden_ids  = set(str(b) for b in st.session_state["admin_hidden_book_ids"])
    deleted_ids = set(str(b) for b in st.session_state["admin_deleted_book_ids"])

    active_books  = [b for b in books if str(b.get("book_id", "")) not in deleted_ids]
    deleted_books = [b for b in books if str(b.get("book_id", "")) in deleted_ids]

    def _matches(b):
        return not search_query or search_query.lower() in str(b.get("title", "")).lower()

    visible_books     = [b for b in active_books if str(b.get("book_id", "")) not in hidden_ids and _matches(b)]
    hidden_books_list = [b for b in active_books if str(b.get("book_id", "")) in hidden_ids and _matches(b)]

    selected_book_id = st.session_state["admin_selected_book_id"]
    selected_book = next(
        (b for b in books if str(b.get("book_id", "")) == str(selected_book_id)),
        None
    ) if selected_book_id is not None else None

    # =========================
    # EDIT MODE
    # =========================
    if selected_book and st.session_state["admin_edit_mode"]:
        st.markdown(f"<div class='book-title'>Edit: {selected_book.get('title', 'Book')}</div>", unsafe_allow_html=True)

        subject_code = selected_book.get("subject_code", "")
        icon = ICONS.get(selected_book.get("program_related", ""), "📚")
        img_url = f"{BASE_IMG}/{subject_code}.jpg"

        st.markdown(f"""
            <div style='width:100%;height:280px;display:flex;align-items:center;justify-content:center;
                        background:#f8fafc;border-radius:12px;overflow:hidden;margin-bottom:15px;'>
                <img src='{img_url}' style='max-width:100%;max-height:280px;object-fit:contain;'
                    onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                <div style='display:none;font-size:72px;align-items:center;justify-content:center;
                            width:100%;height:100%;'>{icon}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='detail-box'>
                <b>Book Title:</b> {selected_book.get('title', '')} <br>
                <b>Subject Code:</b> {subject_code} <br>
                <b>Program:</b> {selected_book.get('program_related', '')} <br>
            </div>
        """, unsafe_allow_html=True)

        with st.form("admin_book_edit_form"):
            price = st.number_input(
                "Price", min_value=0.0,
                value=float(selected_book.get("price", 0) or 0), format="%.2f"
            )
            stock_quantity = st.number_input(
                "Stock Quantity", min_value=0,
                value=int(selected_book.get("stock_quantity", 0) or 0), step=1
            )
            semester_available = st.number_input(
                "Semester Available", min_value=1, max_value=4, step=1,
                value=int(selected_book.get("semester_available", 1) or 1)
            )
            save_col, cancel_col = st.columns(2)
            with save_col:
                save_changes = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with cancel_col:
                cancel_edit = st.form_submit_button("✖ Cancel", use_container_width=True)

            if save_changes:
                success = book_client.update_book(
                    str(selected_book.get("book_id", "")),
                    {"price": price, "stock_quantity": stock_quantity, "semester_available": semester_available}
                )
                st.success("Book updated successfully.") if success else st.error("Failed to update book.")
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_book_id"] = None
                st.rerun()

            if cancel_edit:
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_book_id"] = None
                st.rerun()

        st.button("Hide Book", key="admin_hide_in_edit",
                on_click=hide_book, args=(selected_book.get("book_id", ""),))
        return

    # =========================
    # DETAIL VIEW
    # =========================
    if selected_book and not st.session_state.get("admin_edit_mode", False):
        st.markdown(f"<div class='book-title'>{selected_book.get('title', 'Book')}</div>", unsafe_allow_html=True)

        subject_code = selected_book.get("subject_code", "")
        icon = ICONS.get(selected_book.get("program_related", ""), "📚")
        img_url = f"{BASE_IMG}/{subject_code}.jpg"

        detail_img_col, detail_info_col = st.columns([1, 2])
        with detail_img_col:
            st.markdown(f"""
                <div style='width:100%;height:320px;display:flex;align-items:center;justify-content:center;
                            background:#f8fafc;border-radius:12px;overflow:hidden;'>
                    <img src='{img_url}' style='max-width:100%;max-height:480px;object-fit:contain;'
                        onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                    <div style='display:none;font-size:72px;align-items:center;justify-content:center;
                                width:100%;height:100%;'>{icon}</div>
                </div>
            """, unsafe_allow_html=True)

        with detail_info_col:
            st.markdown(f"""
                <div class='detail-box' style='height:320px;box-sizing:border-box;'>
                    <b>Subject Code:</b> {subject_code} <br><br>
                    <b>Program:</b> {selected_book.get('program_related', '')} <br><br>
                    <b>Price:</b> ₱{selected_book.get('price', '0')} <br><br>
                    <b>Stock:</b> {selected_book.get('stock_quantity', '0')} <br><br>
                    <b>Semester Available:</b> {selected_book.get('semester_available', '')}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("← Back to List", key="admin_back_to_book_list", use_container_width=True):
                select_book(None, False)
                st.rerun()
        with col2:
            if st.button("✏️ Edit", key="admin_book_detail_edit", use_container_width=True):
                select_book(selected_book_id, True)
                st.rerun()
        with col3:
            if st.button("🗑️ Delete", key="admin_book_detail_delete", use_container_width=True):
                soft_delete_book(selected_book.get("book_id", ""))
                st.session_state["admin_selected_book_id"] = None
                st.rerun()
        return

    # =========================
    # LIST VIEW
    # =========================
    rows = visible_books + hidden_books_list

    if not rows:
        st.warning("No books found.")
    else:
        for row_start in range(0, len(rows), 2):
            row_items = rows[row_start:row_start + 2]
            card_cols = st.columns(2)

            for col_idx, book in enumerate(row_items):
                with card_cols[col_idx]:
                    book_id      = book.get("book_id", "")
                    is_hidden    = str(book_id) in hidden_ids
                    subject_code = book.get("subject_code", "")
                    icon         = ICONS.get(book.get("program_related", ""), "📚")
                    opacity      = "opacity:0.55;" if is_hidden else ""
                    stock        = int(book.get("stock_quantity", 0) or 0)
                    img_url      = f"{BASE_IMG}/{subject_code}.jpg"

                    hidden_badge = (
                        "<span style='background:#64748b;color:white;border-radius:10px;"
                        "padding:3px 9px;font-size:11px;margin-left:6px;'>Hidden</span>"
                    ) if is_hidden else ""

                    st.markdown(f"""
                        <div class='book-card-wrapper' style='{opacity}'>
                            <div class='book-card-img'>
                                <img src='{img_url}'
                                    onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                                <div style='display:none;width:100%;height:100%;font-size:72px;
                                            align-items:center;justify-content:center;background:#e2e8f0;'>{icon}</div>
                            </div>
                            <div class='book-card-body'>
                                <div class='book-name'>{book.get('title', 'Unknown')}{hidden_badge}</div>
                                <div class='book-type'>{book.get('program_related', '')} | Stock: {stock}</div>
                                <div class='book-price'>₱{book.get('price', '0')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns([10, 1])
                    with btn_col1:
                        if st.button("View Details", key=f"admin_book_view_{book_id}", use_container_width=True):
                            select_book(book_id, False)
                            st.rerun()
                    with btn_col2:
                        with st.popover(""):
                            if st.button("✏️ Edit", key=f"admin_book_edit_{book_id}", use_container_width=True):
                                select_book(book_id, True)
                                st.rerun()
                            if is_hidden:
                                if st.button("🔁 Restore", key=f"admin_book_restore_{book_id}", use_container_width=True):
                                    restore_book(book_id)
                                    st.rerun()
                            else:
                                if st.button("🗑️ Delete", key=f"admin_book_delete_{book_id}", use_container_width=True):
                                    soft_delete_book(book_id)
                                    st.rerun()

        if hidden_books_list:
            st.markdown(
                "<p class='admin-action-note'>Hidden books are shown above and remain available for admin review.</p>",
                unsafe_allow_html=True
            )

    # =========================
    # DELETED BOOKS SECTION
    # =========================
    if deleted_books:
        st.markdown("<div class='deleted-section-title'>🗑️ Deleted Books</div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:13px;color:#64748b;margin-bottom:12px;'>"
            "These books have been deleted and are hidden from all views. You can restore them at any time.</p>",
            unsafe_allow_html=True
        )

        for book in deleted_books:
            book_id = book.get("book_id", "")
            icon    = ICONS.get(book.get("program_related", ""), "📚")
            stock   = int(book.get("stock_quantity", 0) or 0)

            dcol1, dcol2 = st.columns([6, 1])
            with dcol1:
                st.markdown(f"""
                    <div class='deleted-row'>
                        <span style='font-size:28px;margin-right:12px;'>{icon}</span>
                        <div>
                            <div class='deleted-book-name'>{book.get('title', 'Unknown')}</div>
                            <div class='deleted-book-meta'>
                                {book.get('program_related', '')} &nbsp;|&nbsp;
                                Stock: {stock} &nbsp;|&nbsp;
                                ₱{book.get('price', '0')} &nbsp;|&nbsp;
                                Sem {book.get('semester_available', '')}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with dcol2:
                st.write("")
                if st.button("🔁 Restore", key=f"admin_book_undelete_{book_id}", use_container_width=True):
                    restore_deleted_book(book_id)
                    st.rerun()


if __name__ == "__main__":
    show()