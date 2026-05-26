import streamlit as st
from services.uniform_client import UniformClient


def show():
    uniform_client = UniformClient()

    st.markdown("""
        <style>
        .stApp { background-color: white; }
        .uniform-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .uniform-card { background-color: #f8fafc; border-radius: 0 0 12px 12px; border: 1px solid #e2e8f0; margin-bottom: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 10px; }
        .uniform-info { padding: 8px 0px; }
        .uniform-name { font-size:15px; font-weight:700; color:#1e3a8a; }
        .uniform-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .uniform-type { font-size:12px; color:#64748b; margin-top:2px; }
        .detail-box { background-color: #fefce8; border: 1px solid #facc15; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
        .admin-action-note { margin-top: 12px; font-size: 13px; color: #475569; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='uniform-title'>Admin Uniform Management</div>", unsafe_allow_html=True)

    try:
        uniforms = uniform_client.list_uniforms() or []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return

    st.session_state.setdefault("admin_selected_uniform_id", None)
    st.session_state.setdefault("admin_edit_mode", False)
    st.session_state.setdefault("admin_hidden_uniform_ids", [])
    st.session_state.setdefault("admin_uniform_action_product", None)

    def select_uniform(product_id, edit_mode=False):
        st.session_state["admin_selected_uniform_id"] = product_id
        st.session_state["admin_edit_mode"] = edit_mode
        st.session_state["admin_uniform_action_product"] = None

    def hide_uniform(product_id):
        hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])
        hidden_ids.add(str(product_id))
        st.session_state["admin_hidden_uniform_ids"] = list(hidden_ids)
        st.success("Product hidden from user view.")

    def restore_uniform(product_id):
        hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])
        hidden_ids.discard(str(product_id))
        st.session_state["admin_hidden_uniform_ids"] = list(hidden_ids)
        st.success("Product restored to visible list.")

    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        search_query = st.text_input("Search uniforms...", key="admin_uniform_search", label_visibility="collapsed", placeholder="Search uniforms...")
    with top_col2:
        st.write("")

    try:
        categories = sorted({u.get("uniform_type", "Other") or "Other" for u in uniforms})
    except Exception:
        categories = ["Other"]

    price_ranges = [
        ("All Prices", None),
        ("Under 500", (0, 499.99)),
        ("500 - 999", (500, 999.99)),
        ("1000+", (1000, None)),
    ]

    fcol1, fcol2, fcol3, fcol4 = st.columns([1, 1, 1, 1])
    with fcol1:
        availability_filter = st.selectbox("Availability", ["All", "In Stock", "Out of Stock"], key="admin_availability_filter", label_visibility="collapsed")
    with fcol2:
        hidden_filter = st.selectbox("Show", ["All", "Visible only", "Hidden only"], key="admin_hidden_filter", label_visibility="collapsed")
    with fcol3:
        category_filter = st.selectbox("Category", ["All"] + categories, key="admin_category_filter", label_visibility="collapsed")
    with fcol4:
        price_filter = st.selectbox("Price range", [p[0] for p in price_ranges], key="admin_price_filter", label_visibility="collapsed")

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

    hidden_ids = set(str(pid) for pid in st.session_state["admin_hidden_uniform_ids"])
    selected_price_range = dict(price_ranges)[price_filter]

    def _matches_filters(u):
        name = str(u.get("product_name", "") or "")
        if search_query and search_query.lower() not in name.lower():
            return False
        if category_filter != "All" and u.get("uniform_type", "") != category_filter:
            return False
        total_stock = sum(int(s.get("product_stock", 0)) for s in u.get("sizes", []))
        if availability_filter == "In Stock" and total_stock <= 0:
            return False
        if availability_filter == "Out of Stock" and total_stock > 0:
            return False
        price = parse_price(u.get("price", 0))
        if not in_price_range(price, selected_price_range):
            return False
        return True

    visible_uniforms = [u for u in uniforms if str(u.get("product_id", "")) not in hidden_ids and _matches_filters(u)]
    hidden_uniforms = [u for u in uniforms if str(u.get("product_id", "")) in hidden_ids and _matches_filters(u)]

    selected_uniform_id = st.session_state["admin_selected_uniform_id"]
    selected_uniform = None
    if selected_uniform_id is not None:
        for uniform in uniforms:
            if str(uniform.get("product_id", "")) == str(selected_uniform_id):
                selected_uniform = uniform
                break

    # =========================
    # EDIT MODE
    # =========================
    if selected_uniform and st.session_state["admin_edit_mode"]:
        st.markdown(f"<div class='uniform-title'>Edit {selected_uniform.get('product_name', 'Uniform')}</div>", unsafe_allow_html=True)

        img_url = f"http://localhost:9000/static/images/uniforms/{selected_uniform.get('product_id', '')}.jpg"
        st.markdown(f"""
            <div style='width:100%;height:300px;display:flex;align-items:center;justify-content:center;background:#f8fafc;border-radius:12px;overflow:hidden;margin-bottom:15px;'>
                <img src='{img_url}' style='max-width:100%;max-height:300px;object-fit:contain;' onerror="this.parentElement.innerHTML='<div style=\\'font-size:64px;\\'>👕</div>';">
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='detail-box'>
                <b>Product Name:</b> {selected_uniform.get('product_name', '')} <br>
                <b>Type:</b> {selected_uniform.get('uniform_type', '')} <br>
            </div>
        """, unsafe_allow_html=True)

        with st.form("admin_uniform_edit_form"):
            price = st.number_input("Price", min_value=0.0, value=float(selected_uniform.get("price", 0)), format="%.2f")
            st.markdown("<div class='detail-box'><strong>Size stock details</strong></div>", unsafe_allow_html=True)
            updated_sizes = []
            for idx, size_info in enumerate(selected_uniform.get("sizes", [])):
                size_label = size_info.get("size", "N/A")
                stock_value = int(size_info.get("product_stock", 0))
                new_stock = st.number_input(f"Stock for {size_label}", min_value=0, value=stock_value, step=1, key=f"admin_stock_{selected_uniform_id}_{idx}")
                updated_sizes.append({"size": size_label, "product_stock": new_stock})

            save_changes = st.form_submit_button("Save Changes")
            cancel_edit = st.form_submit_button("Cancel")

            if save_changes:
                update_data = {"price": price, "sizes": updated_sizes}
                success = uniform_client.update_uniform(str(selected_uniform.get("product_id", "")), update_data)
                if success:
                    st.success("Uniform updated successfully.")
                else:
                    st.error("Failed to update uniform.")
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_uniform_id"] = None
                st.rerun()

            if cancel_edit:
                st.session_state["admin_edit_mode"] = False
                st.session_state["admin_selected_uniform_id"] = None
                st.rerun()

        st.button("Hide Product", key="admin_hide_in_edit", on_click=hide_uniform, args=(selected_uniform.get("product_id", ""),))
        return

    # =========================
    # DETAIL VIEW
    # =========================
    if selected_uniform and not st.session_state.get("admin_edit_mode", False):
        st.markdown(f"<div class='uniform-title'>{selected_uniform.get('product_name', 'Uniform')}</div>", unsafe_allow_html=True)
        total_stock = sum(int(s.get("product_stock", 0)) for s in selected_uniform.get("sizes", []))

        img_url = f"http://localhost:9000/static/images/uniforms/{selected_uniform.get('product_id', '')}.jpg"
        st.markdown(f"""
            <div style='width:100%;height:350px;display:flex;align-items:center;justify-content:center;background:#f8fafc;border-radius:12px;overflow:hidden;margin-bottom:15px;'>
                <img src='{img_url}' style='max-width:100%;max-height:350px;object-fit:contain;' onerror="this.parentElement.innerHTML='<div style=\\'font-size:64px;\\'>👕</div>';">
            </div>
        """, unsafe_allow_html=True)

        size_lines = []
        for size in selected_uniform.get("sizes", []):
            size_label = size.get("size", "N/A")
            stock = int(size.get("product_stock", 0))
            detail_parts = [f"Stock: {stock}"]
            for key, value in size.items():
                if key in ("size", "product_stock"):
                    continue
                detail_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            size_lines.append(f"<strong>{size_label}</strong> — {' | '.join(detail_parts)}")

        sizes_html = "<br>".join(size_lines) or "No size data available"

        st.markdown(f"""
            <div class='detail-box'>
                <b>Type:</b> {selected_uniform.get('uniform_type', '')} <br>
                <b>Price:</b> ₱{selected_uniform.get('price', '0')} <br>
                <b>Total Stock:</b> {total_stock} <br>
                <b>Sizes:</b> <br>
                <span style='font-size:13px;color:#475569;'>{sizes_html}</span>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("Back to List", key="admin_back_to_uniform_list"):
                select_uniform(None, False)
                st.rerun()
        with col2:
            if st.button("Edit", key="admin_detail_edit"):
                select_uniform(selected_uniform_id, True)
                st.rerun()
        with col3:
            if st.button("Delete", key="admin_detail_delete"):
                hide_uniform(selected_uniform.get("product_id", ""))
                st.session_state["admin_selected_uniform_id"] = None
                st.rerun()
        return

    # =========================
    # LIST VIEW
    # =========================
    if hidden_filter == "All":
        rows = visible_uniforms + hidden_uniforms
    elif hidden_filter == "Visible only":
        rows = visible_uniforms
    else:
        rows = hidden_uniforms

    if not rows:
        st.warning("No uniforms found for the selected filters.")
        return

    # Use rows of 2 to allow st.columns inside without 3-level nesting
    for row_start in range(0, len(rows), 2):
        row_items = rows[row_start:row_start + 2]
        card_cols = st.columns(len(row_items))

        for col_idx, uniform in enumerate(row_items):
            with card_cols[col_idx]:
                total_stock = sum(int(s.get("product_stock", 0)) for s in uniform.get("sizes", []))
                product_id = uniform.get("product_id", "")
                is_hidden = str(product_id) in hidden_ids
                img_url = f"http://localhost:9000/static/images/uniforms/{product_id}.jpg"
                opacity = "opacity:0.55;" if is_hidden else ""

                st.markdown(f"""
                    <div style='width:100%;height:250px;display:flex;align-items:center;justify-content:center;background:#f8fafc;border-radius:12px 12px 0 0;overflow:hidden;{opacity}'>
                        <img src='{img_url}' style='max-width:100%;max-height:250px;object-fit:contain;' onerror="this.parentElement.innerHTML='<div style=\\'font-size:48px;\\'>👕</div>';">
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class='uniform-card' style='{opacity}'>
                        <div class='uniform-info'>
                            <div class='uniform-name'>{uniform.get('product_name', 'Unknown')}</div>
                            <div class='uniform-type'>{uniform.get('uniform_type', '')} | Stock: {total_stock}</div>
                            <div class='uniform-price'>₱{uniform.get('price', '0')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_hidden:
                    st.markdown("<span style='background:#64748b;color:white;border-radius:10px;padding:4px 10px;font-size:12px;'>Hidden</span>", unsafe_allow_html=True)

                # View Details + ⋮ side by side (level 2 columns)
                btn_col1, btn_col2 = st.columns([5, 1])
                with btn_col1:
                    if st.button("View Details", key=f"admin_view_{product_id}", use_container_width=True):
                        select_uniform(product_id, False)
                        st.rerun()
                with btn_col2:
                    with st.popover(""):
                        if st.button("✏️ Edit", key=f"admin_edit_{product_id}", use_container_width=True):
                            select_uniform(product_id, True)
                            st.rerun()
                        if is_hidden:
                            if st.button("🔁 Restore", key=f"admin_restore_{product_id}", use_container_width=True):
                                restore_uniform(product_id)
                                st.rerun()
                        else:
                            if st.button("🗑️ Delete", key=f"admin_delete_{product_id}", use_container_width=True):
                                hide_uniform(product_id)
                                st.rerun()

    if hidden_uniforms:
        st.markdown("<p class='admin-action-note'>Hidden uniforms are shown at the bottom and remain available for admin review.</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    show()