import streamlit as st
import pandas as pd
from typing import List, Dict

def display_book_catalog(books: List[Dict]) -> None:
    """
    Display a book catalog with filtering and search capabilities.
    
    Args:
        books: List of book dictionaries containing book details
    """
    
    st.subheader("📚 Book Catalog")
    
    # Convert to DataFrame for easier filtering
    df = pd.DataFrame(books)
    
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_title = st.text_input("🔍 Search by Title")
    
    with col2:
        program_filter = st.multiselect(
            "Program",
            options=df["program_related"].unique().tolist(),
            default=df["program_related"].unique().tolist()
        )
    
    with col3:
        availability_filter = st.multiselect(
            "Availability",
            options=["available", "unavailable"],
            default=["available"]
        )
    
    with col4:
        price_range = st.slider(
            "Price Range",
            min_value=int(df["price"].min()),
            max_value=int(df["price"].max()),
            value=(int(df["price"].min()), int(df["price"].max())),
            step=50
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_title:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(search_title, case=False, na=False)
        ]
    
    filtered_df = filtered_df[
        (filtered_df["program_related"].isin(program_filter)) &
        (filtered_df["availability"].isin(availability_filter)) &
        (filtered_df["price"] >= price_range[0]) &
        (filtered_df["price"] <= price_range[1])
    ]
    
    # Display results count
    st.write(f"**Found {len(filtered_df)} book(s)**")
    
    # Display books in a grid layout
    cols = st.columns(3)
    
    for idx, (_, book) in enumerate(filtered_df.iterrows()):
        col = cols[idx % 3]
        
        with col:
            # Determine availability color
            availability_color = "🟢" if book["availability"] == "available" else "🔴"
            
            # Create card
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: #f9f9f9;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{book['title']}</h4>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <b>Book ID:</b> {book['book_id']}<br>
                    <b>Subject:</b> {book['subject_code']}<br>
                    <b>Program:</b> {book['program_related']}<br>
                    <b>Semester:</b> {book['semester_available']}
                </p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 14px;">
                    <b>₱{book['price']:.2f}</b>
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    Stock: <b>{book['stock_quantity']}</b> units
                </p>
                <p style="margin: 5px 0; font-size: 12px;">
                    {availability_color} <b>{book['availability'].upper()}</b>
                </p>
                <p style="margin: 5px 0; font-size: 11px; color: #999;">
                    Updated: {book['date_updated']}
                </p>
            </div>
            """, unsafe_allow_html=True)


def display_book_table(books: List[Dict]) -> None:
    """
    Display books in a table format.
    
    Args:
        books: List of book dictionaries
    """
    
    st.subheader("📋 Book Catalog (Table View)")
    
    df = pd.DataFrame(books)
    
    # Format columns for display
    display_df = df[
        ["book_id", "title", "price", "stock_quantity", "program_related", "availability"]
    ].copy()
    
    display_df.columns = ["ID", "Title", "Price (₱)", "Stock", "Program", "Status"]
    
    # Color availability column
    def color_availability(val):
        color = 'green' if val == 'available' else 'red'
        return f'color: {color}'
    
    styled_df = display_df.style.applymap(
        color_availability,
        subset=['Status']
    )
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def display_book_sidebar_filter(books: List[Dict]) -> Dict:
    """
    Display book filters in sidebar and return filtered results.
    
    Args:
        books: List of book dictionaries
        
    Returns:
        Dictionary with filter values
    """
    
    df = pd.DataFrame(books)
    
    with st.sidebar:
        st.header("🔧 Filters")
        
        filters = {}
        
        filters["title"] = st.text_input("Search Title")
        filters["program"] = st.multiselect(
            "Select Program(s)",
            options=df["program_related"].unique().tolist()
        )
        filters["semester"] = st.multiselect(
            "Select Semester(s)",
            options=sorted(df["semester_available"].unique().tolist())
        )
        filters["availability"] = st.radio(
            "Availability",
            options=["All", "Available", "Unavailable"]
        )
        
        return filters
    
    st.set_page_config(page_title="Book Catalog", layout="wide")
    st.title("Book Catalog Widget Demo")
    
    # Display card view
    display_book_catalog(sample_books)
    
    st.divider()
    
    # Display table view
    display_book_table(sample_books)
