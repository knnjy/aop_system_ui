import streamlit as st
from services.book_client import BookClient
from services.order_client import OrderClient


def show():

    st.set_page_config(page_title="AOP System - Home",page_icon="house.svg", layout="wide")
    # Inject custom CSS
    st.markdown(
        """
        <style>
        .stApp {
            background-color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='border:2px solid #6e6e6e; background-color:#f9f9f9; padding:20px; border-radius:8px'>
            <span style='color:#1e3a8a; font-weight:bold; font-size:35px'>
                Welcome back, Student! 
            </span>
            <span style='color:#676767; font-size:16px; display:block; margin-top:1px'>
                Required materials this semester.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

     # Initialize API clients
    book_client = BookClient()
    order_client = OrderClient()


    if "cart" not in st.session_state:
        st.session_state["cart"] = []


    # Outer layout: two main columns
    page_col1, page_col2 = st.columns([3,2])

    with page_col1:
        st.markdown(
            """
            <div style='border:1px solid #e2e8f0; background-color:white; padding:15px; border-radius:8px; margin-top:20px'>
                <h3 style='color:#1e3a8a; margin-bottom:10px'>Required Learning Materials</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        books = book_client.list_books()  # API call
        if books:
            for book in books:
                # Two columns: left for title+price, right for button
                book_col1, book_col2 = st.columns([4,2])

                with book_col1:
                    # Title
                    st.markdown(
                        f"<span style='color:#1e3a8a; font-weight:bold'>{book['Title']}</span>",
                        unsafe_allow_html=True
                    )
                    # Price below title
                    st.markdown(
                        f"<span style='color:#1e3a8a'>₱{book['Price']}</span>",
                        unsafe_allow_html=True
                    )

                with book_col2:
                    # Force button to the far right
                    st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
                    if st.button("Add to cart", icon=":material/add_shopping_cart:", key=f"add_{book['book_id']}"):
                        st.session_state["cart"].append(book)
                        st.success(f"Added {book['Title']} to cart")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Divider between items
                st.markdown(
                    "<hr style='border:1px solid #1e3a8a; margin:10px 0;'>",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No required books found.")





    with page_col2:
        st.markdown(
            """
            <div style='border:1px solid #e2e8f0; background-color:white; padding:15px; border-radius:8px; margin-top:20px'>
                <h3 style='color:#1e3a8a; margin-bottom:10px'>Summary</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
