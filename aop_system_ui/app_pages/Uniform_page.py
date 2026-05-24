import streamlit as st
from services.uniform_client import UniformClient

def show():
    uniform_client = UniformClient()

    # --- Inject CSS (Blue, White, Gold Theme) ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .uniform-title { font-size:28px; font-weight:700; color:#1e3a8a; margin-bottom:20px; }
        .filter-box {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .filter-title {
            font-size:18px; font-weight:700; color:#1e3a8a; margin-bottom:10px;
        }
        .uniform-card {
            background-color: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            cursor: pointer;
        }
        .uniform-img-placeholder {
            background-color: #e2e8f0;
            width: 100%;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }
        .uniform-info { padding: 12px; }
        .uniform-name { font-size:16px; font-weight:700; color:#1e3a8a; }
        .uniform-price { font-size:14px; color:#d97706; font-weight:600; margin-top:4px; }
        .uniform-type { font-size:12px; color:#64748b; margin-top:2px; }
        .detail-box {
            background-color: #fefce8;
            border: 1px solid #facc15;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='uniform-title'>RTU Uniform Page</div>", unsafe_allow_html=True)

    # --- Layout: Filters (left) + Uniforms (right) ---
    filter_col, uniform_col = st.columns([1,3])

    with filter_col:
        st.markdown("<div class='filter-box'><div class='filter-title'>🧵 Filters</div>", unsafe_allow_html=True)
        search_query = st.text_input("🔎 Search uniforms...", key="uniform_search")

        # Fetch uniforms
        try:
            uniforms = uniform_client.list_uniforms() or []
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            return

        if not uniforms:
            st.warning("No uniforms found.")
            return

        types = ["All"] + sorted({u.get("uniform_type", "") for u in uniforms if u.get("uniform_type")})
        sizes = ["All"] + sorted({s.get("size") for u in uniforms for s in u.get("sizes", []) if s.get("size")})

        category = st.selectbox("📂 Category", types, key="uniform_category")
        size = st.selectbox("📏 Size", sizes, key="uniform_size")
        price_range = st.selectbox("💰 Price Range", ["All", "₱0-₱300", "₱301-₱600", "₱601+"], key="uniform_price")
        availability = st.selectbox("📦 Availability", ["All", "Available", "Unavailable"], key="uniform_availability")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Apply Filters ---
    filtered_uniforms = []
    for u in uniforms:
        try:
            name = str(u.get("product_name", ""))
            utype = str(u.get("uniform_type", ""))
            price_val = float(u.get("price", 0) or 0)
            total_stock = sum(s.get("product_stock", 0) for s in u.get("sizes", []))

            name_match = search_query.lower() in name.lower() if search_query else True
            category_match = (category == "All" or utype == category)
            size_match = (size == "All" or size in [s.get("size") for s in u.get("sizes", [])])

            if price_range == "₱0-₱300":
                price_match = price_val <= 300
            elif price_range == "₱301-₱600":
                price_match = 301 <= price_val <= 600
            elif price_range == "₱601+":
                price_match = price_val >= 601
            else:
                price_match = True

            if availability == "Available":
                avail_match = total_stock > 0
            elif availability == "Unavailable":
                avail_match = total_stock <= 0
            else:
                avail_match = True

            if name_match and category_match and size_match and price_match and avail_match:
                filtered_uniforms.append(u)

        except Exception as e:
            st.warning(f"Skipped a uniform due to invalid data: {e}")
            continue

    # --- LIST VIEW ---
    icons = {"Essentials": "👔", "PE": "🏃"}
    with uniform_col:
        if not filtered_uniforms:
            st.warning("No uniforms match your filters.")
        else:
            cols = st.columns(2)
            for i, uniform in enumerate(filtered_uniforms):
                try:
                    icon = icons.get(uniform.get("uniform_type", ""), "👕")
                    total_stock = sum(s.get("product_stock", 0) for s in uniform.get("sizes", []))

                    st.markdown(f"""
                        <div class='uniform-card'>
                            <div class='uniform-img-placeholder'>{icon}</div>
                            <div class='uniform-info'>
                                <div class='uniform-name'>{uniform.get('product_name','Unknown')}</div>
                                <div class='uniform-type'>{uniform.get('uniform_type','')} | Stock: {total_stock}</div>
                                <div class='uniform-price'>₱{uniform.get('price','0')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns([1,1])
                    with btn_col1:
                        if st.button("🔎 View Details", key=f"view_{uniform.get('product_id',i)}"):
                            st.session_state["selected_uniform"] = uniform
                    with btn_col2:
                        if total_stock > 0:
                            if st.button("🛒 Add to Cart", key=f"cart_{uniform.get('product_id',i)}"):
                                st.session_state.setdefault("cart", []).append(uniform)
                                st.success(f"Added {uniform.get('product_name')} to cart!")

                except Exception as e:
                    st.warning(f"Skipped rendering a uniform card due to error: {e}")
                    continue

if __name__ == "__main__":
    show()
