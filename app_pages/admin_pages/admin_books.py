import streamlit as st
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

    st.markdown("### Add New Book")

    with st.form("add_book_form"):

        book_id = st.text_input("Book ID")
        subject_code = st.text_input("Subject Code")
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        price = st.number_input("Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0, step=1)
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
                "book_id": book_id,
                "subject_code": subject_code,
                "title": title,
                "author": author,
                "price": price,
                "stock": stock,
                "program_related": program_related,
                "semester_available": semester_available
            }

            success = book_client.add_book(book_data)

            if success:
                st.success("Book added successfully!")
            else:
                st.error("Failed to add book.")