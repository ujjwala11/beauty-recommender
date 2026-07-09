import streamlit as st
import pandas as pd


from recommender import (
    products,
    reviews,
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
# CHECK SELECTED PRODUCT
# ============================================================


if "selected_product" not in st.session_state:


    st.warning(
        "No product selected"
    )


    st.stop()



product_id = st.session_state.selected_product


add_event(
    st.session_state.user,
    product_id,
    "view"
)

# ============================================================
# GET PRODUCT
# ============================================================


product_data = products[

    products["product_id"]

    ==

    product_id

]



if product_data.empty:


    st.error(
        "Product not found"
    )


    st.stop()



product = product_data.iloc[0]





# ============================================================
# PRODUCT DETAILS
# ============================================================


col1, col2 = st.columns(
    [1,2]
)



with col1:


    image = product.get(

        "image_url",

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

            "Unknown"

        )

    )


    st.subheader(

        product.get(

            "brand_name",

            ""

        )

    )


    st.write(

        f"🧴 Category: {product.get('primary_category','Beauty')}"

    )


    st.write(

        f"💵 Price: ${float(product.get('price_usd',0)):.2f}"

    )



    if "rating" in product.index:


        st.write(

            f"⭐ Rating: {product['rating']}"

        )





# ============================================================
# PRODUCT INFORMATION
# ============================================================


st.divider()



st.subheader(
    "About this product"
)



description = product.get(

    "description",

    "Premium beauty product designed for everyday care."

)



st.write(

    description

)





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



if pd.isna(ingredients) or ingredients is None:


    st.write(

        "Ingredients information unavailable"

    )


else:


    ingredient_list = str(

        ingredients

    ).split(",")



    for ing in ingredient_list[:10]:


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
This product was analyzed using:

✓ Content similarity  
✓ User preference patterns  
✓ Product popularity signals  

The recommendation engine considers:
- Product category
- Product characteristics
- User behaviour
- Similar customer interactions

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


        for _,row in similar.iterrows():


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


        rating = review.get(

            "rating",

            ""

        )


        text = review.get(

            "review_text",

            ""

        )


        st.write(

            f"⭐ {rating}/5"

        )


        st.write(

            text

        )


        st.divider()




# ============================================================
# BACK BUTTON
# ============================================================


if st.button(

    "⬅ Back to Store"

):


    st.switch_page(

        "app.py"

    )