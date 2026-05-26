import streamlit as st
from services.book_client import BookClient

book_client = BookClient()

def update_book_form(existing_book):
    st.markdown("### Update Book")

    with st.form("update_book_form"):
        subject_code = st.text_input("Subject Code", value=existing_book["subject_code"])
        title = st.text_input("Title", value=existing_book["title"])
        price = st.number_input("Price", min_value=0.0, format="%.2f", value=existing_book["price"])
        stock_quantity = st.number_input("Stock Quantity", min_value=0, value=existing_book["stock_quantity"])
        semester_available = st.number_input("Semester Available", min_value=1, max_value=2, value=existing_book["semester_available"])
        program_related = st.selectbox("Program Related", ["All", "ICS", "CEA", "CAS", "CBEA"], index=["All", "ICS", "CEA", "CAS", "CBEA"].index(existing_book["program_related"]))
        availability = st.selectbox("Availability", ["available", "unavailable"], index=["available", "unavailable"].index(existing_book["availability"]))

        col1, col2 = st.columns([1,1])
        with col1:
            submitted = st.form_submit_button("Update Book")
        with col2:
            cancel = st.form_submit_button("Cancel")

        if submitted:
            updated_book = {
                "subject_code": subject_code,
                "title": title,
                "price": price,
                "stock_quantity": stock_quantity,
                "semester_available": semester_available,
                "program_related": program_related,
                "availability": availability
            }
                       # Validation
            errors = []
            if not updated_book["subject_code"]:
                errors.append("Subject Code is required.")
            if not updated_book["title"]:
                errors.append("Title is required.")
            if updated_book["price"] <= 0:
                errors.append("Price must be greater than 0.")
            if updated_book["stock_quantity"] <= 0:
                errors.append("Stock Quantity must be greater than 0.")

            if errors:
                st.error("⚠️ Please fix the following:\n- " + "\n- ".join(errors))
            else:
                st.json(updated_book)
                success = book_client.update_book(
                    book_id=existing_book.get("book_id"),
                    updated_data=updated_book
                )
                if success:
                    st.success("Book updated!")
                    st.session_state["update_success"] = f"Success, '{updated_book['subject_code']}' has been updated successfully!"
                    st.session_state["edit_mode"] = False
                    st.session_state["selected_book"] = None
                    st.rerun()
                else:
                    st.error("Failed to update book")
        if cancel:
            # Just exit edit mode without saving
            st.session_state["edit_mode"] = False
            st.session_state["selected_book"] = None
            st.rerun()
