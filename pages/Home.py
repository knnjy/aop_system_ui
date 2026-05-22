import streamlit as st
from services.book_client import BookClient
from services.order_client import OrderClient


def show():
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


    # Initialize cart once
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
                book_col1, book_col2 = st.columns([4,2])

                with book_col1:
                    st.markdown(
                        f"<span style='color:#1e3a8a; font-weight:bold'>{book['title']}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<span style='color:#1e3a8a'>₱{book['price']}</span>",
                        unsafe_allow_html=True
                    )

                with book_col2:
                    if st.button("Add to cart", icon=":material/add_shopping_cart:", key=f"add_{book['book_id']}"):
                        st.session_state["cart"].append(book)
                        st.success(f"Added {book['title']} to cart")

                st.markdown(
                    "<hr style='border:1px solid #1e3a8a; margin:10px 0;'>",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No required books found.")



    with page_col2:
        st.write(order_client, books)

        st.markdown(
            """
            <div style='border:1px solid #e2e8f0; background-color:white; padding:15px; border-radius:8px; margin-top:20px'>
                <h3 style='color:#1e3a8a; margin-bottom:10px'>Summary</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state["cart"]:
            total_items = len(st.session_state["cart"])
            total_price = sum(item["Price"] for item in st.session_state["cart"]) 

            st.write(f"Total items: {total_items}")
            st.write(f"Total price: ₱{total_price}")

            # Check if all books are bought
            if total_items == len(books):
                st.success("All books have been bought!")

            if st.button("Order All"):
                order_data = {"items": st.session_state["cart"]}
                result = order_client.add_order(order_data)
                if result:
                    st.success("Order placed successfully!")
                    st.session_state["cart"].clear()
                else:
                    st.error("Failed to place order.")
        else:
            st.info("Your cart is empty.")



