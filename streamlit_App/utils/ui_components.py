import streamlit as st



def product_card(row):


    # ==============================
    # SAFE VALUES
    # ==============================


    product_id = row.get(
        "product_id",
        ""
    )


    product_name = row.get(
        "product_name",
        "Unknown Product"
    )


    brand = row.get(
        "brand_name",
        "Unknown Brand"
    )


    category = row.get(
        "primary_category",
        "Beauty"
    )


    price = row.get(
        "price_usd",
        0
    )


    image = row.get(
        "image_url",
        "https://via.placeholder.com/300"
    )



    # ==============================
    # CARD
    # ==============================


    col1, col2 = st.columns(
        [1,2]
    )



    with col1:


        st.image(
            image,
            width=180
        )



    with col2:


        st.subheader(
            product_name
        )


        st.caption(
            brand
        )


        st.write(
            f"🧴 {category}"
        )


        st.write(
            f"💵 ${float(price):.2f}"
        )



        # ==========================
        # AI SCORE
        # ==========================


        score = None


        for col in [

            "final_score",
            "content_score",
            "collab_score",
            "personal_score",
            "cold_start_score"

        ]:


            if col in row.index:


                score = row[col]

                break



        if score is not None:


            score = float(score)


            score = max(
                0,
                min(
                    score,
                    1
                )
            )


            st.progress(
                score
            )


            st.write(

                f"🤖 AI Match: {score*100:.1f}%"

            )



        # ==========================
        # EXPLANATION
        # ==========================


        if "reason" in row.index:


            st.info(

                f"✨ {row['reason']}"

            )


        else:


            st.info(
                """
✨ Why recommended:

• Similar beauty preferences
• Similar products liked by users
• Matches your category interest
"""
            )



        # ==========================
        # PRODUCT DETAIL BUTTON
        # ==========================


        if st.button(

            "View Details",

            key=f"detail_{product_id}"

        ):


            st.session_state.selected_product = product_id


            st.switch_page(

                "pages/product_detail.py"

            )



    st.divider()