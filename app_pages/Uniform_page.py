import streamlit as st
from services.uniform_client import UniformClient

def show():
    uniform_client = UniformClient()

    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .uniform-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .filter-box {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .filter-title { font-size:18px; font-weight:700; color:#1e3a8a; margin-bottom:15px; }
        .uniform-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 0;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            cursor: pointer;
        }
        .uniform-img-placeholder {
            background-color: #e2e8f0;
            width: 100%;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
        }
        .uniform-info { padding: 12px; }
        .uniform-name { font-size:15px; font-weight:700; color:#1e3a8a; }
        .uniform-price { font-size:14px; color:#1e3a8a; font-weight:600; margin-top:4px; }
        .uniform-type { font-size:12px; color:#64748b; margin-top:2px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='uniform-title'>Uniform Page</div>", unsafe_allow_html=True)

    # Fetch uniforms
    try:
        uniforms = uniform_client.list_uniforms() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    if not uniforms:
        st.warning("No uniforms found.")
        return

    # Layout: filters left, products right
    col_filter, col_products = st.columns([1, 3])

    with col_filter:
        st.markdown("""
            <div class='filter-box'>
                <div class='filter-title'>Filters</div>
            </div>
        """, unsafe_allow_html=True)

        search_query = st.text_input("Search", placeholder="Search uniforms...", key="uniform_search")

        types = ["All"] + sorted(list(set([u.get("uniform_type", "") for u in uniforms if u.get("uniform_type")])))
        all_sizes = []
        for u in uniforms:
            for s in u.get("sizes", []):
                if s.get("size") and s.get("size") not in all_sizes:
                    all_sizes.append(s.get("size"))
        sizes = ["All"] + sorted(all_sizes)

        category = st.selectbox("Category", types, key="uniform_category")
        size = st.selectbox("Size", sizes, key="uniform_size")
        price_range = st.selectbox("Price Range", ["All", "₱0-₱300", "₱301-₱600", "₱601+"], key="uniform_price")
        availability = st.selectbox("Availability", ["All", "Available", "Unavailable"], key="uniform_availability")

    # Apply filters
    filtered = []
    for u in uniforms:
        if search_query and search_query.lower() not in u.get("product_name", "").lower():
            continue
        if category != "All" and u.get("uniform_type", "") != category:
            continue
        if size != "All":
            sizes_list = [s.get("size") for s in u.get("sizes", [])]
            if size not in sizes_list:
                continue
        if price_range != "All":
            price = float(u.get("price", 0))
            if price_range == "₱0-₱300" and price > 300:
                continue
            elif price_range == "₱301-₱600" and not (301 <= price <= 600):
                continue
            elif price_range == "₱601+" and price < 601:
                continue
        if availability != "All":
            total_stock = sum([s.get("product_stock", 0) for s in u.get("sizes", [])])
            if availability == "Available" and total_stock <= 0:
                continue
            if availability == "Unavailable" and total_stock > 0:
                continue
        filtered.append(u)

    with col_products:
        if not filtered:
            st.warning("No uniforms match your filters.")
            return

        # Uniform icons per type
        icons = {
            "Essentials": "👔",
            "PE": "🏃",
        }

        cols = st.columns(2)
        for i, uniform in enumerate(filtered):
            with cols[i % 2]:
                icon = icons.get(uniform.get("uniform_type", ""), "👕")
                total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])

                st.markdown(f"""
                    <div class='uniform-card'>
                        <div class='uniform-img-placeholder'>{icon}</div>
                        <div class='uniform-info'>
                            <div class='uniform-name'>{uniform.get('product_name', 'Unknown')}</div>
                            <div class='uniform-type'>{uniform.get('uniform_type', '')} | Stock: {total_stock}</div>
                            <div class='uniform-price'>₱{uniform.get('price', '0')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if total_stock > 0:
                    if st.button("Add to Cart", key=f"uniform_{uniform.get('product_id', i)}"):
                        if "cart" not in st.session_state:
                            st.session_state["cart"] = []
                        st.session_state["cart"].append(uniform)
                        st.success(f"Added {uniform.get('product_name')} to cart!")


if __name__ == "__main__":
    show()