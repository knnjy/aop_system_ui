# components/navbar.py
import streamlit as st
from streamlit_option_menu import option_menu


hide_default_menu = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Make navbar stretch full width */
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Navbar Styling */
    .nav-container {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 12px 0;
        border-radius: 0px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
        margin-left: -1000px !important;
        margin-right: -1000px !important;
        padding-left: 1000px !important;
        padding-right: 1000px !important;
    }
    
    /* Active menu item styling */
    .nav-item-active {
        background-color: #fbbf24 !important;
        color: #1e3a8a !important;
        font-weight: 700 !important;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(251, 191, 36, 0.3);
    }
    
    /* Menu options styling */
    [data-testid="stHorizontalBlock"] > [data-testid="element-container"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """

def navbar():
    # Hide default sidebar menu
   
    st.markdown(hide_default_menu, unsafe_allow_html=True)

    menu_options = [
        "Home", "Books", "Uniforms",
        "Checkout Page", "Order Status",
        "Order History", "Account"
    ]
    
    menu_icons = [
        "house", "book", "person-badge",
        "bag-check", "list", "clock-history", "person"
    ]
    
    # Get current page from session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    
    # Determine default_index based on current page
    try:
        default_index = menu_options.index(st.session_state.current_page)
    except ValueError:
        default_index = 0

    col1, col2 = st.columns([8, 1])
    with col1:
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=menu_icons,
            orientation="horizontal",
            default_index=default_index,
            key="navbar_menu",
            styles={
            "container": {
                "background-color": "#1e3a8a",
                "padding": "8px 0",
                "border-radius": "10px",
            },
            "icon": {
                "color": "white",
                "font-size": "18px",
            },
            "nav-link": {
                "color": "white",
                "font-size": "14px",
                "text-align": "center",
                "margin": "0 4px",
                "padding": "10px 16px",
                "border-radius": "8px",
                "font-weight": "500",
            },
            "nav-link-selected": {
                "background-color": "#fbbf24",
                "color": "#1e3a8a",
                "font-weight": "700",
                "box-shadow": "0 4px 8px rgba(251, 191, 36, 0.3)",
            },
        }
        )
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_page = "Home"
            st.rerun()
        
        # If the selected page is different from current page, update and rerun
        if selected != st.session_state.current_page:
            st.session_state.current_page = selected
            st.rerun()
        
        return selected


def admin_navbar():
    st.markdown(hide_default_menu, unsafe_allow_html=True)
    menu_options = [
        "Home", "Books", "Uniforms", "Order Request", "Order History", "Account"
    ]
    menu_icons = [
        "house", "book", "person-badge",
        "bag-check", "list", "clock-history", "person"
    ]

    try:
        default_index = menu_options.index(st.session_state.current_page)
    except ValueError:
        default_index = 0
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        menu_icon="list",
        default_index=default_index,
        orientation="horizontal",
        key="navbar_menu",
        styles={
            "container": {
                "background-color": "#1e3a8a",
                "padding": "8px 0",
                "border-radius": "10px",
            },
            "icon": {
                "color": "white",
                "font-size": "18px",
            },
            "nav-link": {
                "color": "white",
                "font-size": "14px",
                "text-align": "center",
                "margin": "0 4px",
                "padding": "10px 16px",
                "border-radius": "8px",
                "font-weight": "500",
            },
            "nav-link-selected": {
                "background-color": "#fbbf24",
                "color": "#1e3a8a",
                "font-weight": "700",
                "box-shadow": "0 4px 8px rgba(251, 191, 36, 0.3)",
            },
        }
    )

    return selected