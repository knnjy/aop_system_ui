import streamlit as st
from services.book_client import BookClient

# Main function for RTU Books page
def show():
    # Page title
    st.title("RTU Books")

    # Connect to backend service
    book_client = BookClient()

    # Sidebar filters
    search_query = st.sidebar.text_input("Search books...")
    category = st.sidebar.selectbox("Category", ["All", "ICS", "CEA", "CAS", "CBEA"])
    price_range = st.sidebar.selectbox("Price Range", ["All", "₱0-₱300", "₱301-₱600", "₱601+"])
    availability_filter = st.sidebar.selectbox("Availability", ["All", "Available", "Unavailable"])

    # Get books from backend
    books = book_client.list_books() or []

    # Apply filters
    filtered_books = []
    for book in books:
        # Only active books
        if str(book.get("is_deleted", "False")).lower() == "false":
            # Search filter
            if search_query and search_query.lower() not in book["title"].lower():
                continue
            # Category filter
            if category != "All" and category.lower() not in book["program_related"].lower():
                continue
            # Availability filter
            if availability_filter != "All" and availability_filter.lower() != book["availability"].lower():
                continue
            # Price filter
            if price_range != "All":
                price = float(book["price"])
                if price_range == "₱0-₱300" and price > 300:
                    continue
                elif price_range == "₱301-₱600" and not (301 <= price <= 600):
                    continue
                elif price_range == "₱601+" and price < 601:
                    continue
            # Add book if it passed all filters
            filtered_books.append(book)

    # Display books
    if filtered_books:
        for book in filtered_books:
            st.markdown(f"""
            ### {book['subject_code']}  
            {book['title']}  
            Edition: {book.get('semester_available','N/A')}  
            Price: ₱{book['price']}  
            {book['availability']} | Stocks: {book['stock_quantity']}
            """)
            st.button("Add to Cart", key=book["book_id"])
    else:
        st.warning("No books found.")


show()