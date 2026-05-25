import streamlit as st
from services.order_client import OrderClient

def show():
    st.markdown("<h1 style='color:#1e3a8a;'>🛒 Check Out</h1>", unsafe_allow_html=True)
    order_client = OrderClient()

    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []

    if st.session_state.cart_items:
        # Header row using columns
        header_cols = st.columns([3, 2, 1, 2, 1, 1])
        headers = ["Product", "Info", "Price", "Quantity", "Subtotal", "Action"]
        for col, text in zip(header_cols, headers):
            col.markdown(f"<strong style='color:#1e3a8a;'>{text}</strong>", unsafe_allow_html=True)

        # Cart items
        for item in st.session_state.cart_items:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 2, 1, 1])
            col1.markdown(f"**{item['title']}**")
            col2.markdown(f"<span style='   color:#6b7280;'>{item['info']}</span>", unsafe_allow_html=True)
            col3.markdown(f"₱{item['unit_price']:.2f}")
            new_qty = col4.number_input("", min_value=1, value=item['quantity'], key=f"qty_{item['product_id']}", label_visibility="collapsed")
            item['quantity'] = new_qty
            col5.markdown(f"**₱{item['unit_price'] * item['quantity']:.2f}**")
            if col6.button("🗑️", key=f"remove_{item['product_id']}"):
                st.session_state.cart_items = [i for i in st.session_state.cart_items if i['product_id'] != item['product_id']]
                st.rerun()

        # Total section
        total = sum(item['unit_price'] * item['quantity'] for item in st.session_state.cart_items)
        st.markdown(f"<hr><h3 style='text-align:right;color:#1e3a8a;'>Total: ₱{total:.2f}</h3>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("💳 Proceed to Check out", use_container_width=True, type="primary"):
                # Create order from cart items
                cart = st.session_state.cart_items
                order_data = {
                    "user_id": st.session_state.user_id,
                    "total_amount": total,
                    "order_items": [
                        {
                            "product_id": item['product_id'],
                            "unit_price": item['unit_price'],
                            "quantity": item['quantity'],
                            "subtotal": item['unit_price'] * item['quantity']
                        }
                        for item in cart
                    ]
                }

                try:
                    result = order_client.add_order(order_data)
                    # Check if successful (200 status or result is truthy)
                    if result is not None:
                        st.success("Order placed successfully!")
                        st.session_state.cart_items = []
                        st.session_state.current_page = 'Order Status'
                        st.rerun()
                    else:
                        st.error("Failed to place order. Please try again.")
                except Exception as e:
                    st.error(f"Error placing order: {str(e)}")
    else:
        st.info("Your cart is empty")
        col1, col2 = st.columns(2)
        if col1.button("Browse Books"):
            st.session_state.current_page = 'Books'
            st.rerun()
        if col2.button("Browse Uniforms"):
            st.session_state.current_page = 'Uniforms'
            st.rerun()
