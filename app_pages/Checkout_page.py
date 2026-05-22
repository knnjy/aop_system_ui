import streamlit as st

def show():
    st.markdown("""
    <h1 style="color: #1e3a8a;">🛒 Check Out</h1>
    """, unsafe_allow_html=True)

    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []

    if st.session_state.cart_items:
        # Table header
        st.markdown("""
        <div class="card">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border); background-color: #f9fafb;">
                        <th style="padding: 1rem; text-align: left; color: #1e3a8a;">Product</th>
                        <th style="padding: 1rem; text-align: left; color: #1e3a8a;">Info</th>
                        <th style="padding: 1rem; text-align: left; color: #1e3a8a;">Price</th>
                        <th style="padding: 1rem; text-align: center; color: #1e3a8a;">Quantity</th>
                        <th style="padding: 1rem; text-align: right; color: #1e3a8a;">Subtotal</th>
                        <th style="padding: 1rem; text-align: center; color: #1e3a8a;">Action</th>
                    </tr>
                </thead>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Cart items
        for item in st.session_state.cart_items:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 2, 1, 1])

            with col1:
                st.markdown(f"""
                <div style="padding: 0.5rem;">
                    <strong>{item['title']}</strong>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="padding: 0.5rem; color: #6b7280;">
                    {item['info']}
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="padding: 0.5rem;">
                    ${item['price']:.2f}
                </div>
                """, unsafe_allow_html=True)

            with col4:
                new_qty = st.number_input("", min_value=1, value=item['quantity'], key=f"qty_{item['id']}", label_visibility="collapsed")
                item['quantity'] = new_qty

            with col5:
                st.markdown(f"""
                <div style="padding: 0.5rem; text-align: right; font-weight: 600;">
                    ${item['price'] * item['quantity']:.2f}
                </div>
                """, unsafe_allow_html=True)

            with col6:
                if st.button("🗑️", key=f"remove_{item['id']}"):
                    st.session_state.cart_items = [i for i in st.session_state.cart_items if i['id'] != item['id']]
                    st.rerun()

        # Total section
        total = sum(item['price'] * item['quantity'] for item in st.session_state.cart_items)

        st.markdown(f"""
        <div class="card" style="background-color: #f9fafb; margin-top: 2rem;">
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 2rem;">
                <span style="font-size: 1.5rem; color: #1e3a8a; font-weight: 600;">Total:</span>
                <span style="font-size: 2rem; font-weight: 700; color: #1e3a8a;">
                    ${total:.2f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("💳 Proceed to Check out", use_container_width=True, type="primary"):
                st.session_state.current_page = 'order_status'
                st.rerun()
    else:
        st.info("Your cart is empty")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Browse Books"):
                st.session_state.current_page = 'books'
                st.rerun()
        with col2:
            if st.button("Browse Uniforms"):
                st.session_state.current_page = 'uniforms'
                st.rerun()
