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

