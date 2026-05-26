import streamlit as st

from services.uniform_client import UniformClient

uniform_client = UniformClient()


def add_uniform_form():
    st.markdown("### Add New Uniform")

    # --- Uniform type selector OUTSIDE the form ---
    uniform_category = st.selectbox("Uniform Type", ["Top", "Bottom", "Skirt"], key="uniform_type_selector")

    with st.form("add_uniform_form"):
        # --- Product-level fields ---
        st.markdown("#### Details")
        product_name = st.text_input("Product Name")
        top_col1, top_col2 = st.columns([3, 1])
        with top_col1:
            uniform_type = st.selectbox("Uniform Type", ["Essentials", "NSTP", "PE", "Others"])
        with top_col2:
            price = st.number_input("Price", min_value=0.0, format="%.2f")

        # --- Size entries ---
        st.markdown("#### Sizes")

        sizes = []
        size_options = ["Small", "Medium", "Large", "XL", "2XL", "3XL"]

        for size in size_options:
            st.markdown(f"**{size}**")

            if uniform_category == "Top":
                col1, col2, col3, col4 = st.columns(4)
                length = col1.number_input(f"{size} Length", min_value=0, key=f"{size}_length")
                bust_chest = col2.number_input(f"{size} Bust/Chest", min_value=0, key=f"{size}_bust")
                shoulder = col3.number_input(f"{size} Shoulder", min_value=0, key=f"{size}_shoulder")
                stock = col4.number_input(f"{size} Stock", min_value=0, key=f"{size}_stock")

                sizes.append({
                    "size": size,
                    "length": length,
                    "bust_chest": bust_chest,
                    "shoulder": shoulder,
                    "product_stock": stock
                })

            elif uniform_category == "Bottom":
                col1, col2, col3 = st.columns(3)
                length = col1.number_input(f"{size} Length", min_value=0, key=f"{size}_length")
                waistline = col2.number_input(f"{size} Waistline", min_value=0, key=f"{size}_waist")
                stock = col3.number_input(f"{size} Stock", min_value=0, key=f"{size}_stock")

                sizes.append({
                    "size": size,
                    "length": length,
                    "waistline": waistline,
                    "product_stock": stock
                })

            elif uniform_category == "Skirt":
                col1, col2, col3 = st.columns(3)
                length = col1.number_input(f"{size} Length", min_value=0, key=f"{size}_length")
                waistline = col2.number_input(f"{size} Waistline", min_value=0, key=f"{size}_waist")
                stock = col3.number_input(f"{size} Stock", min_value=0, key=f"{size}_stock")

                sizes.append({
                    "size": size,
                    "length": length,
                    "waistline": waistline,
                    "product_stock": stock
                })

        image_file = st.file_uploader("Upload Uniform Image", type=["jpg"])

        submitted = st.form_submit_button("Save Uniform")

        if submitted:
            # --- Validation ---
            errors = []
            if not product_name.strip():
                errors.append("Product Name is required.")
            if not uniform_type.strip():
                errors.append("Uniform Type is required.")
            if price <= 0:
                errors.append("Price must be greater than 0.")

            for s in sizes:
                for k, v in s.items():
                    if k != "size" and (v is None or v == 0):
                        errors.append(f"{s['size']} {k.replace('_',' ').title()} must not be empty or zero.")

            if errors:
                st.error("⚠️ Please fix the following:\n- " + "\n- ".join(errors))
            else:
                # STEP 1: Create the uniform first
                uniform_data = {
                    "product_name": product_name,
                    "price": price,
                    "uniform_type": uniform_type,
                    "uniform_category": uniform_category,
                    "sizes": sizes
                }
                
                response = uniform_client.add_uniform(uniform_data=uniform_data)
                if response:
                    # STEP 2: Get the product_id from the response
                    product_id = response.get("product_id")  # Backend must return this
                    
                    # STEP 3: Now validate and upload image with the product_id
                    if image_file and product_id:
                        # Rename to match product_id
                        image_file.name = f"{product_id}.jpg"
                        uploaded = uniform_client.uniform_upload_image(image_file)
                        if uploaded:
                            st.success("Uniform and image uploaded successfully!")
                        else:
                            st.error("Uniform created but image upload failed")
                    else:
                        st.success("Uniform added successfully!")
                else:
                    st.error("Failed to create uniform.")
