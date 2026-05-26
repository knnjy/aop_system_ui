import streamlit as st
from services.book_client import BookClient

book_client = BookClient()
def add_book_form():
    with st.form("add_book_form"):

        subject_code = st.text_input("Subject Code", key="subject_code")
        title = st.text_input("Book Title", key="title")
        price = st.number_input("Price", min_value=0.0, key="price")
        stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1, key="stock_quantity")
        program_related = st.text_input("Program Related", key="program_related")
        semester_available = st.number_input(
            "Semester Available",
            min_value=1,
            max_value=4,
            step=1,
            key="semester_available"
        )
        image_file = st.file_uploader("Upload Book Image", type=["jpg"])

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
                st.rerun()
            else:
                st.error("Failed to add book.")
