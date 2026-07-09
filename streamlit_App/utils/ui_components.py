import streamlit as st
import pandas as pd


# ============================================================
# PRODUCT CARD COMPONENT
# ============================================================


def safe_value(value, default):
    """
    Handle None, NaN, empty strings safely.
    """

    if value is None:
        return default

    if isinstance(value, float) and pd.isna(value):
        return default

    if str(value).strip() == "":
        return default

    if str(value).lower() == "nan":
        return default

    return value



def product_card(row):


    # ========================================================
    # SAFE VALUES
    # ========================================================


    product_id = safe_value(
        row.get("product_id"),
        "unknown"
    )


    product_name = safe_value(
        row.get("product_name"),
        "Unknown Product"
    )


    brand = safe_value(
        row.get("brand_name"),
        "Unknown Brand"
    )


    category = safe_value(
        row.get("primary_category"),
        "Beauty"
    )


    price = safe_value(
        row.get("price_usd"),
        0
    )


    image = safe_value(
        row.get("image_url"),
        "https://via.placeholder.com/300x300?text=No+Image"
    )



    # ========================================================
    # CARD LAYOUT
    # ========================================================


    col1, col2 = st.columns(
        [1, 2]
    )



    # ========================================================
    # IMAGE
    # ========================================================


    with col1:


        try:

            st.image(
                image,
                width=180
            )

        except Exception:

            st.image(
                "https://via.placeholder.com/300x300?text=No+Image",
                width=180
            )



    # ========================================================
    # DETAILS
    # ========================================================


    with col2:


        st.subheader(
            str(product_name)
        )


        st.caption(
            str(brand)
        )


        st.write(
            f"🧴 {category}"
        )


        try:

            price = float(price)

        except:

            price = 0.0


        st.write(
            f"💵 ${price:.2f}"
        )



        # ====================================================
        # AI SCORE
        # ====================================================


        score = None


        score_columns = [

            "final_score",

            "content_score",

            "collab_score",

            "personal_score",

            "cold_start_score"

        ]


        for col in score_columns:


            if col in row.index:


                try:

                    score = float(row[col])

                    break

                except:

                    pass



        if score is not None:


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



        # ====================================================
        # REASON
        # ====================================================


        reason = row.get(
            "reason",
            None
        )


        if reason and not pd.isna(reason):


            st.info(
                f"✨ {reason}"
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



        # ====================================================
        # PRODUCT DETAIL BUTTON
        # ====================================================


        if st.button(

            "View Details",

            key=f"detail_{product_id}"

        ):


            st.session_state.selected_product = product_id


            try:

                st.switch_page(
                    "pages/product_detail.py"
                )

            except Exception:


                st.warning(
                    "Product details page unavailable."
                )



    st.divider()