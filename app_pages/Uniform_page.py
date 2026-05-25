
import streamlit as st
from services.uniform_client import UniformClient

def show():
    uniform_client = UniformClient()

    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .uniform-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .uniform-card { background-color: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 15px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .uniform-img-placeholder { background-color: #e2e8f0; width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; font-size: 48px; }
        .uniform-info { padding: 12px; }
        .uniform-name { font-size:15px; font-weight:700; color:#1e3a8a; }
        .uniform-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .uniform-type { font-size:12px; color:#64748b; margin-top:2px; }
        .detail-box { background-color: #fefce8; border: 1px solid #facc15; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='uniform-title'>Uniform Page</div>", unsafe_allow_html=True)

    try:
        uniforms = uniform_client.list_uniforms() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    if not uniforms:
        st.warning("No uniforms found.")
        return

    if "selected_uniform" not in st.session_state:
        st.session_state["selected_uniform"] = None
    if "selected_uniform_size" not in st.session_state:
        st.session_state["selected_uniform_size"] = None
    if "uniform_cart_mode" not in st.session_state:
        st.session_state["uniform_cart_mode"] = False

    icons = {"Essentials": "👔", "PE": "🏃"}

    def parse_price(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    def in_price_range(price_value, price_range):
        if price_range is None:
            return True
        low, high = price_range
        if low is not None and price_value < low:
            return False
        if high is not None and price_value > high:
            return False
        return True

    selected_uniform = st.session_state.get("selected_uniform")

    if st.session_state.get("uniform_cart_mode") and selected_uniform:
        uniform = selected_uniform
        total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])
        key_base = f"detail_{uniform.get('product_id', 0)}"
        selected_size = st.session_state.get("selected_uniform_size", None)

        st.markdown(f"<div class='uniform-title'>{uniform.get('product_name', 'Unknown')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='detail-box'>
                <b>Type:</b> {uniform.get('uniform_type', '')} <br>
                <b>Price:</b> ₱{uniform.get('price', '0')} <br>
                <b>Total Stock:</b> {total_stock}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='color:#1e3a8a;font-weight:600;'>Choose size:</p>", unsafe_allow_html=True)
        for size_info in uniform.get("sizes", []):
            size_label = size_info.get("size", "N/A")
            stock = int(size_info.get("product_stock", 0))
            size_key = f"{key_base}_size_{size_label}"
            if stock > 0:
                is_selected = selected_size == size_label
                btn_label = f"✓ {size_label} (Stock: {stock})" if is_selected else f"{size_label} (Stock: {stock})"
                if st.button(btn_label, key=size_key, use_container_width=True):
                    st.session_state["selected_uniform_size"] = size_label
                    st.rerun()
            else:
                st.button(f"{size_label} (Out of stock)", key=size_key, disabled=True, use_container_width=True)

        if selected_size:
            st.info(f"Selected size: **{selected_size}**")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back", key="back_from_cart"):
                st.session_state["uniform_cart_mode"] = False
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
                st.rerun()
        with col2:
            if st.button("Add to Cart", key=f"confirm_cart_{uniform.get('product_id', 0)}", disabled=not selected_size):
                if "cart_items" not in st.session_state:
                    st.session_state["cart_items"] = []
                cart_item = {
                    "id": uniform.get("product_id"),
                    "title": uniform.get("product_name"),
                    "price": float(uniform.get("price", 0) or 0),
                    "info": f"{uniform.get('uniform_type', '')} - Size: {selected_size}",
                    "quantity": 1
                }
                st.session_state["cart_items"].append(cart_item)
                st.success(f"Added {uniform.get('product_name')} ({selected_size}) to cart!")
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
                st.session_state["uniform_cart_mode"] = False
                st.rerun()
        return

    if selected_uniform:
        uniform = selected_uniform
        total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])

        size_lines = []
        for size in uniform.get('sizes', []):
            size_label = size.get('size', 'N/A')
            stock = int(size.get('product_stock', 0))
            detail_parts = [f"Stock: {stock}"]
            for key, value in size.items():
                if key in ('size', 'product_stock'):
                    continue
                detail_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            size_lines.append(f"<strong>{size_label}</strong> — {' | '.join(detail_parts)}")

        sizes_html = "<br>".join(size_lines) or "No size data available"

        st.markdown(f"<div class='uniform-title'>{uniform.get('product_name', 'Unknown')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='detail-box'>
                <b>Type:</b> {uniform.get('uniform_type', '')} <br>
                <b>Price:</b> ₱{uniform.get('price', '0')} <br>
                <b>Total Stock:</b> {total_stock} <br>
                <b>Sizes:</b> <br>
                <span style='font-size:13px;color:#475569;'>{sizes_html}</span>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back to List", key="back_to_list"):
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
                st.session_state["uniform_cart_mode"] = False
                st.rerun()
        with col2:
            if total_stock > 0:
                if st.button("Add to Cart", key=f"detail_cart_{uniform.get('product_id', 0)}"):
                    st.session_state["uniform_cart_mode"] = True
                    st.session_state["selected_uniform_size"] = None
                    st.rerun()
        return

    categories = sorted({u.get("uniform_type", "Other") or "Other" for u in uniforms})
    price_ranges = [
        ("All Prices", None),
        ("Under 500", (0, 499.99)),
        ("500 - 999", (500, 999.99)),
        ("1000+", (1000, None)),
    ]

    filter_col, list_col = st.columns([1, 3])
    with filter_col:
        st.markdown("<h4 style='margin-top:0;color:#1e3a8a;'>Filters</h4>", unsafe_allow_html=True)
        search_query = st.text_input("Search", key="uniform_search", placeholder="Search by name...", label_visibility="collapsed")
        availability_filter = st.selectbox("Availability", ["All", "In Stock", "Out of Stock"], key="availability_filter", label_visibility="collapsed")
        category_filter = st.selectbox("Category", ["All"] + categories, key="category_filter", label_visibility="collapsed")
        price_filter = st.selectbox("Price range", [p[0] for p in price_ranges], key="price_filter", label_visibility="collapsed")

    selected_price_range = dict(price_ranges)[price_filter]

    filtered = []
    for uniform in uniforms:
        name = str(uniform.get("product_name", "") or "")
        if search_query and search_query.lower() not in name.lower():
            continue
        if category_filter != "All" and uniform.get("uniform_type", "") != category_filter:
            continue
        total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])
        if availability_filter == "In Stock" and total_stock <= 0:
            continue
        if availability_filter == "Out of Stock" and total_stock > 0:
            continue
        price = parse_price(uniform.get("price", 0))
        if not in_price_range(price, selected_price_range):
            continue
        filtered.append(uniform)

    with list_col:
        if not filtered:
            st.warning("No uniforms match your search or filter settings.")
            return

        cols = st.columns(2)
        for i, uniform in enumerate(filtered):
            with cols[i % 2]:
                icon = icons.get(uniform.get("uniform_type", ""), "👕")
                total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])
                product_id = uniform.get("product_id", i)
                product_key = str(product_id)

                st.markdown(f"""
                    <div class='uniform-card'>
                        <div class='uniform-img-placeholder'>{icon}</div>
                        <div class='uniform-info'>
                            <div class='uniform-name'>{uniform.get('product_name', 'Unknown')}</div>
                            <div class='uniform-type'>{uniform.get('uniform_type', '')} | Stock: {total_stock}</div>
                            <div class='uniform-price'>{uniform.get('price', '0')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("View Details", key=f"view_{product_key}", use_container_width=True):
                    st.session_state["selected_uniform"] = uniform
                    st.session_state["selected_uniform_size"] = None
                    st.session_state["uniform_cart_mode"] = False
                    st.rerun()

                if total_stock > 0:
                    if st.button("Add to Cart", key=f"cart_{product_key}", use_container_width=True):
                        st.session_state["selected_uniform"] = uniform
                        st.session_state["selected_uniform_size"] = None
                        st.session_state["uniform_cart_mode"] = True
                        st.rerun()

if __name__ == "__main__":
    show()
