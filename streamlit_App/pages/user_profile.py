# pages/user_profile.py

import streamlit as st
import pandas as pd
from pathlib import Path


from recommender import (
    products,
    recommend_hybrid
)


from user_recommender import (
    build_user_profile,
    recommend_for_user
)


from utils.ui_components import product_card


from cold_start import (
    load_user_preferences,
    cold_start_recommend
)



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Beauty Profile",
    page_icon="💄",
    layout="wide"
)



# ============================================================
# LOAD REVIEWS SAFELY
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
# LOGIN CHECK
# ============================================================


if (
    "logged_in" not in st.session_state
    or not st.session_state.logged_in
):

    st.warning(
        "Please login first"
    )

    st.stop()



# ============================================================
# USER
# ============================================================


user_id = st.session_state.get(
    "user"
)



if user_id is None:

    st.error(
        "User not found"
    )

    st.stop()



# ============================================================
# PRODUCT SAFETY
# ============================================================


products = products.copy()



required_defaults = {

    "primary_category":"Unknown",

    "brand_name":"Unknown",

    "price_usd":0,

    "image_url":
        "https://via.placeholder.com/300"

}



for col,value in required_defaults.items():

    if col not in products.columns:

        products[col] = value



# ============================================================
# BUILD PROFILE
# ============================================================


profile = build_user_profile(

    user_id,

    reviews,

    products

)



# ============================================================
# HEADER
# ============================================================


st.title(
    "💄 My Beauty Profile"
)


st.write(
    f"Welcome back **{user_id}**"
)



# ============================================================
# PROFILE METRICS
# ============================================================


col1,col2,col3 = st.columns(3)



with col1:

    st.metric(
        "Total Reviews",
        profile.get(
            "total_reviews",
            0
        )
    )


with col2:

    st.metric(
        "Average Spend",
        f"${profile.get('avg_price',0):.2f}"
    )


with col3:

    st.metric(
        "Average Rating",
        f"{profile.get('avg_rating',0):.1f} ⭐"
    )



# ============================================================
# PREFERENCES
# ============================================================


st.divider()


left,right = st.columns(2)



with left:

    st.subheader(
        "Favourite Categories"
    )


    categories = profile.get(
        "favorite_categories",
        []
    )


    if categories:

        for c in categories:

            st.write(
                "🧴",
                c
            )

    else:

        st.info(
            "No category data yet"
        )



with right:

    st.subheader(
        "Favourite Brands"
    )


    brands = profile.get(
        "favorite_brands",
        []
    )


    if brands:

        for b in brands:

            st.write(
                "✨",
                b
            )

    else:

        st.info(
            "No brand data yet"
        )



# ============================================================
# HISTORY
# ============================================================


st.divider()


st.subheader(
    "Recently Interacted Products"
)



liked = profile.get(
    "liked_products",
    []
)



if liked:


    st.dataframe(

        pd.DataFrame(liked),

        use_container_width=True

    )


else:

    st.info(
        "No previous products found"
    )



# ============================================================
# RECOMMENDATIONS
# ============================================================


st.divider()


st.header(
    "✨ Recommended For You"
)



if st.button(
    "Generate Recommendations"
):


    if profile.get(
        "total_reviews",
        0
    ) > 0:



        recommendations = recommend_for_user(

            user_id,

            reviews,

            products,

            recommend_hybrid,

            top_n=20

        )


    else:


        preferences = load_user_preferences(

            user_id

        )


        recommendations = cold_start_recommend(

            products,

            preferences,

            top_n=20

        )



    st.session_state.profile_results = recommendations



# ============================================================
# DISPLAY
# ============================================================


if "profile_results" in st.session_state:


    results = (

        st.session_state.profile_results.copy()

    )


    st.subheader(
        "AI Picks"
    )



    sort = st.selectbox(

        "Sort By",

        [

            "AI Ranking",

            "Price Low → High",

            "Price High → Low"

        ],

        key="profile_sort"

    )



    if sort=="Price Low → High":


        results = results.sort_values(

            "price_usd",

            ascending=True

        )



    elif sort=="Price High → Low":


        results = results.sort_values(

            "price_usd",

            ascending=False

        )


    else:


        for col in [

            "final_score",

            "content_score",

            "collab_score",

            "popularity_norm"

        ]:


            if col in results.columns:


                results = results.sort_values(

                    col,

                    ascending=False

                )

                break



    for _,row in results.iterrows():

        product_card(row)