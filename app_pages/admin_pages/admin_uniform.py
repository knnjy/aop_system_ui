import streamlit as st
from services.uniform_client import UniformClient


def show():
    uniform_client = UniformClient()

    st.markdown(
        """
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
        .hidden-card { opacity: 0.55; }
        .hidden-badge { display: inline-block; background: #64748b; color: white; border-radius: 10px; padding: 4px 10px; font-size: 12px; margin-top: 8px; }
        .admin-action-note { margin-top: 12px; font-size: 13px; color: #475569; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='uniform-title'>Admin Uniform Management</div>", unsafe_allow_html=True)

    try:
        uniforms = uniform_client.list_uniforms() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    st.session_state.setdefault("admin_selected_uniform_id", None)
    st.session_state.setdefault("admin_edit_mode", False)
    st.session_state.setdefault("admin_hidden_uniform_ids", [])

    def enter_edit_mode():
        st.session_state["admin_edit_mode"] = True

    def exit_edit_mode():
        st.session_state["admin_edit_mode"] = False
        st.session_state["admin_selected_uniform_id"] = None

    def select_uniform(product_id, edit_mode=False):
        st.session_state["admin_selected_uniform_id"] = product_id
        st.session_state["admin_edit_mode"] = edit_mode

    def hide_uniform(product_id):
        hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])
        hidden_ids.add(str(product_id))
        st.session_state["admin_hidden_uniform_ids"] = list(hidden_ids)
        try:
            uniform_client.delete_uniform(str(product_id))
            st.success("Product hidden from user view.")
        except Exception:
            st.warning("Product marked hidden in admin view.")

    def restore_uniform(product_id):
        hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])
        hidden_ids.discard(str(product_id))
        st.session_state["admin_hidden_uniform_ids"] = list(hidden_ids)
        st.success("Product restored to visible list.")

    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        search_query = st.text_input("🔍 Search uniforms...", key="admin_uniform_search")
    with top_col2:
        if st.session_state["admin_edit_mode"]:
            st.button("✅ Exit Edit Mode", key="admin_exit_edit_mode", on_click=exit_edit_mode)
        else:
            st.button("✏️ Enter Edit Mode", key="admin_enter_edit_mode", on_click=enter_edit_mode)

    hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])

    visible_uniforms = []
    hidden_uniforms = []
    for uniform in uniforms:
        if str(uniform.get("product_id", "")) in hidden_ids:
            hidden_uniforms.append(uniform)
        else:
            visible_uniforms.append(uniform)

    if search_query:
        search_query_lower = search_query.lower()
        visible_uniforms = [
            u for u in visible_uniforms
            if search_query_lower in u.get("product_name", "").lower() or search_query_lower in u.get("uniform_type", "").lower()
        ]
        hidden_uniforms = [
            u for u in hidden_uniforms
            if search_query_lower in u.get("product_name", "").lower() or search_query_lower in u.get("uniform_type", "").lower()
        ]

    selected_uniform_id = st.session_state["admin_selected_uniform_id"]
    selected_uniform = None
    if selected_uniform_id is not None:
        for uniform in uniforms:
            if str(uniform.get("product_id", "")) == str(selected_uniform_id):
                selected_uniform = uniform
                break

    if selected_uniform and st.session_state["admin_edit_mode"]:
        st.markdown(f"<div class='uniform-title'>Edit {selected_uniform.get('product_name', 'Uniform')}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class='detail-box'>
                <b>Product Name:</b> {selected_uniform.get('product_name', '')} <br>
                <b>Type:</b> {selected_uniform.get('uniform_type', '')} <br>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("admin_uniform_edit_form"):
            price = st.number_input("Price", min_value=0.0, value=float(selected_uniform.get("price", 0)), format="%.2f")
            st.markdown("<div class='detail-box'><strong>Size stock details</strong></div>", unsafe_allow_html=True)
            updated_sizes = []
            for idx, size_info in enumerate(selected_uniform.get("sizes", [])):
                size_label = size_info.get("size", "N/A")
                stock_value = int(size_info.get("product_stock", 0))
                new_stock = st.number_input(
                    f"Stock for {size_label}", min_value=0, value=stock_value, step=1,
                    key=f"admin_stock_{selected_uniform_id}_{idx}"
                )
                updated_sizes.append({"size": size_label, "product_stock": new_stock})

            save_changes = st.form_submit_button("Save Changes")
            cancel_edit = st.form_submit_button("Cancel")

            if save_changes:
                update_data = {
                    "price": price,
                    "sizes": updated_sizes,
                }
                success = uniform_client.update_uniform(str(selected_uniform.get("product_id", "")), update_data)
                if success:
                    st.success("Uniform updated successfully.")
                else:
                    st.error("Failed to update uniform.")
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_uniform_id"] = None
                st.experimental_rerun()

            if cancel_edit:
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_uniform_id"] = None
                st.experimental_rerun()

        st.button("🗑️ Hide Product", key="admin_hide_in_edit", on_click=hide_uniform, args=(selected_uniform.get("product_id", ""),), help="Hide this uniform from the user catalog.")
        return

    if selected_uniform and not st.session_state["admin_edit_mode"]:
        st.markdown(f"<div class='uniform-title'>{selected_uniform.get('product_name', 'Uniform')}</div>", unsafe_allow_html=True)
        total_stock = sum(int(s.get("product_stock", 0)) for s in selected_uniform.get("sizes", []))
        st.markdown(
            f"""
            <div class='detail-box'>
                <b>Type:</b> {selected_uniform.get('uniform_type', '')} <br>
                <b>Price:</b> ₱{selected_uniform.get('price', '0')} <br>
                <b>Total Stock:</b> {total_stock}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button("⬅️ Back to Uniform List", key="admin_back_to_uniform_list", on_click=lambda: select_uniform(None, False))
        return

    if not visible_uniforms and not hidden_uniforms:
        st.warning("No uniforms found.")
        return

    def render_uniform_tile(uniform, hidden=False):
        total_stock = sum(int(s.get("product_stock", 0)) for s in uniform.get("sizes", []))
        product_id = uniform.get("product_id", "")
        product_name = uniform.get("product_name", "Unknown")
        product_type = uniform.get("uniform_type", "")
        price = uniform.get("price", "0")
        badge_html = "<div class='hidden-badge'>Hidden</div>" if hidden else ""
        card_class = "uniform-card hidden-card" if hidden else "uniform-card"

        st.markdown(
            f"""
            <div class='{card_class}'>
                <div class='uniform-img-placeholder'>👕</div>
                <div class='uniform-info'>
                    <div class='uniform-name'>{product_name}</div>
                    <div class='uniform-type'>{product_type} | Stock: {total_stock}</div>
                    <div class='uniform-price'>₱{price}</div>
                    {badge_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.button("🔎 View Details", key=f"admin_view_{product_id}", on_click=select_uniform, args=(product_id, False))

        if st.session_state["admin_edit_mode"]:
            with col2:
                st.button("🗑️ Hide", key=f"admin_hide_{product_id}", on_click=hide_uniform, args=(product_id,))
            with col3:
                if hidden:
                    st.button("Restore", key=f"admin_restore_{product_id}", on_click=restore_uniform, args=(product_id,))

    rows = visible_uniforms + hidden_uniforms
    cols = st.columns(2)
    for index, uniform in enumerate(rows):
        with cols[index % 2]:
            render_uniform_tile(uniform, hidden=str(uniform.get("product_id", "")) in hidden_ids)

    if hidden_uniforms:
        st.markdown("<p class='admin-action-note'>Hidden uniforms are shown at the bottom and remain available for admin review.</p>", unsafe_allow_html=True)
