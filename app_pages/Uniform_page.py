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

    # =========================
    # CART MODE - Size Selection
    # =========================
    if st.session_state.get("uniform_cart_mode") and st.session_state.get("selected_uniform"):
        uniform = st.session_state["selected_uniform"]
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
            else:
                st.button(f"{size_label} (Out of stock)", key=size_key, disabled=True, use_container_width=True)

        if selected_size:
            st.info(f"Selected size: **{selected_size}**")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back", key="back_from_cart"):
                st.session_state["uniform_cart_mode"] = False
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
        with col2:
            if st.button("🛒 Add to Cart", key=f"confirm_cart_{uniform.get('product_id', 0)}", disabled=not selected_size):
                if "cart" not in st.session_state:
                    st.session_state["cart"] = []
                item = uniform.copy()
                item["selected_size"] = selected_size
                st.session_state["cart"].append(item)
                st.success(f"Added {uniform.get('product_name')} ({selected_size}) to cart!")
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
                st.session_state["uniform_cart_mode"] = False
        return

    # =========================
    # DETAIL VIEW
    # =========================
    if st.session_state.get("selected_uniform"):
        uniform = st.session_state["selected_uniform"]
        total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])

        st.markdown(f"<div class='uniform-title'>{uniform.get('product_name', 'Unknown')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='detail-box'>
                <b>Type:</b> {uniform.get('uniform_type', '')} <br>
                <b>Price:</b> ₱{uniform.get('price', '0')} <br>
                <b>Total Stock:</b> {total_stock}
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back to List", key="back_to_list"):
                st.session_state["selected_uniform"] = None
                st.session_state["selected_uniform_size"] = None
                st.session_state["uniform_cart_mode"] = False
        with col2:
            if total_stock > 0:
                if st.button("🛒 Add to Cart", key=f"detail_cart_{uniform.get('product_id', 0)}"):
                    st.session_state["uniform_cart_mode"] = True
                    st.session_state["selected_uniform_size"] = None
        return

    # =========================
    # SEARCH BAR (no filter column)
    # =========================
    search_query = st.text_input("🔍 Search uniforms...", key="uniform_search")

    # Apply search filter only
    filtered = [u for u in uniforms if not search_query or search_query.lower() in u.get("product_name", "").lower()]

    if not filtered:
        st.warning("No uniforms match your search.")
        return

    # =========================
    # LIST VIEW - 2 columns, buttons side by side
    # =========================
    cols = st.columns(2)
    for i, uniform in enumerate(filtered):
        with cols[i % 2]:
            icon = icons.get(uniform.get("uniform_type", ""), "👕")
            total_stock = sum([s.get("product_stock", 0) for s in uniform.get("sizes", [])])
            product_id = uniform.get("product_id", i)

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

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("🔎 View Details", key=f"view_{product_id}"):
                    st.session_state["selected_uniform"] = uniform
                    st.session_state["selected_uniform_size"] = None
                    st.session_state["uniform_cart_mode"] = False
            with btn_col2:
                if total_stock > 0:
                    if st.button("🛒 Add to Cart", key=f"cart_{product_id}"):
                        st.session_state["selected_uniform"] = uniform
                        st.session_state["selected_uniform_size"] = None
                        st.session_state["uniform_cart_mode"] = True

if __name__ == "__main__":
    show()