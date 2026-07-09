import streamlit as st
import pandas as pd
from pathlib import Path


from recommender import (
    products,
    recommend_hybrid
)

from utils.tracking import add_event
from utils.ui_components import product_card



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Product Details",
    page_icon="💄",
    layout="wide"
)



# ============================================================
# OPTIONAL REVIEWS LOADER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


REVIEWS_PATH = (
    PROJECT_ROOT
    /
    "data"
    /
    "processed"
    /
    "recommendation"
    /
    "reviews_summary.csv"
)


@st.cache_data
def load_reviews():

    if REVIEWS_PATH.exists():

        return pd.read_csv(
            REVIEWS_PATH,
            low_memory=False
        )

    return pd.DataFrame()



reviews = load_reviews()



# ============================================================
# CHECK PRODUCT
# ============================================================

if "selected_product" not in st.session_state:

    st.warning(
        "No product selected"
    )

    st.stop()



product_id = st.session_state.selected_product



if "user" in st.session_state:

    add_event(
        st.session_state.user,
        product_id,
        "view"
    )



# ============================================================
# GET PRODUCT
# ============================================================


product_data = products[
    products["product_id"] == product_id
]


if product_data.empty:

    st.error(
        "Product not found"
    )

    st.stop()



product = product_data.iloc[0]



# ============================================================
# PRODUCT HEADER
# ============================================================


col1, col2 = st.columns(
    [1,2]
)



with col1:


    image = product.get(
        "image_url",
        ""
    )


    if not image:

        image = (
            "https://via.placeholder.com/300"
        )


    st.image(
        image,
        width=300
    )



with col2:


    st.title(
        product.get(
            "product_name",
            "Unknown Product"
        )
    )


    st.subheader(

        product.get(
            "brand_name",
            "Unknown Brand"
        )

    )


    st.write(
        f"🧴 Category: {product.get('primary_category','Beauty')}"
    )


    price = product.get(
        "price_usd",
        0
    )


    st.write(
        f"💵 Price: ${float(price):.2f}"
    )



# ============================================================
# DESCRIPTION
# ============================================================


st.divider()


st.subheader(
    "About this product"
)


description = product.get(
    "description",
    "Premium beauty product designed for everyday care."
)


if pd.isna(description):

    description = (
        "Premium beauty product designed for everyday care."
    )


st.write(description)



# ============================================================
# INGREDIENTS
# ============================================================


st.subheader(
    "🧪 Ingredients"
)


ingredients = product.get(
    "ingredients",
    None
)



if ingredients is None or pd.isna(ingredients):

    st.write(
        "Ingredients information unavailable"
    )


else:

    for ing in str(ingredients).split(",")[:10]:

        st.write(
            f"🟢 {ing.strip()}"
        )



# ============================================================
# AI EXPLANATION
# ============================================================


st.divider()


st.subheader(
    "🤖 AI Recommendation Explanation"
)


st.info(
"""
This product recommendation uses:

✓ Content similarity  
✓ Collaborative filtering  
✓ Popularity signals  

The AI considers:
- Product characteristics
- Customer behaviour
- Similar product interactions
"""
)



# ============================================================
# SIMILAR PRODUCTS
# ============================================================


st.divider()


st.subheader(
    "✨ Similar Products"
)



try:

    similar = recommend_hybrid(
        product_id,
        top_n=6
    )


    if similar.empty:

        st.write(
            "No similar products found"
        )


    else:

        for _, row in similar.iterrows():

            product_card(row)



except Exception as e:

    st.error(
        f"Recommendation error: {e}"
    )



# ============================================================
# REVIEWS
# ============================================================


st.divider()


st.subheader(
    "💬 Customer Reviews"
)



if reviews.empty:


    st.write(
        "Reviews unavailable"
    )


else:


    product_reviews = reviews[
        reviews["product_id"]
        ==
        product_id
    ]



    if product_reviews.empty:


        st.write(
            "No reviews available"
        )


    else:


        for _,review in product_reviews.head(5).iterrows():


            st.write(
                f"⭐ {review.get('rating','')}/5"
            )


            st.write(
                review.get(
                    "review_text",
                    ""
                )
            )


            st.divider()



# ============================================================
# BACK
# ============================================================


if st.button(
    "⬅ Back to Store"
):

    st.switch_page(
        "app.py"
    )