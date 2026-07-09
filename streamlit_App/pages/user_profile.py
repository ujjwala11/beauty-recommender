# pages/user_profile.py

import streamlit as st
import pandas as pd


from recommender import (
    products,
    reviews,
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
# LOGIN CHECK
# ============================================================

if "logged_in" not in st.session_state or not st.session_state.logged_in:

    st.warning(
        "Please login first"
    )

    st.stop()



# ============================================================
# USER ID
# ============================================================


user_id = st.session_state.get(

    "user",

    None

)



if user_id is None:

    st.error(
        "User not found"
    )

    st.stop()





# ============================================================
# COLUMN SAFETY
# ============================================================


products = products.copy()

reviews = reviews.copy()



if "primary_category" not in products.columns:

    products["primary_category"] = "Unknown"



if "brand_name" not in products.columns:

    products["brand_name"] = "Unknown"



if "price_usd" not in products.columns:

    products["price_usd"] = 0



if "image_url" not in products.columns:

    products["image_url"] = (

        "https://via.placeholder.com/300"

    )





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
# PROFILE CARDS
# ============================================================


col1,col2,col3 = st.columns(3)



with col1:

    st.metric(

        "Total Reviews",

        profile["total_reviews"]

    )



with col2:

    st.metric(

        "Average Spend",

        f"${profile['avg_price']:.2f}"

    )



with col3:

    st.metric(

        "Average Rating",

        f"{profile['avg_rating']:.1f} ⭐"

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


    if profile["favorite_categories"]:


        for c in profile["favorite_categories"]:

            st.write(

                "🧴",

                c

            )

    else:

        st.write(

            "No category data yet"

        )




with right:


    st.subheader(

        "Favourite Brands"

    )


    if profile["favorite_brands"]:


        for b in profile["favorite_brands"]:

            st.write(

                "✨",

                b

            )

    else:

        st.write(

            "No brand data yet"

        )





# ============================================================
# USER HISTORY
# ============================================================


st.divider()



st.subheader(

    "Recently Interacted Products"

)



if profile["liked_products"]:


    history_df = pd.DataFrame(

        profile["liked_products"]

    )


    st.dataframe(

        history_df,

        use_container_width=True

    )


else:


    st.info(

        "No previous products found"

    )





# ============================================================
# PERSONALIZED RECOMMENDATIONS
# ============================================================


st.divider()


st.header(
    "✨ Recommended For You"
)



if st.button(
    "Generate Recommendations"
):


    if profile["total_reviews"] > 0:


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





if "profile_results" in st.session_state:


    results = st.session_state.profile_results.copy()



    sort = st.selectbox(

        "Sort",

        [

            "AI Ranking",

            "Price Low → High",

            "Price High → Low"

        ]

    )



    if sort=="Price Low → High":

        results = results.sort_values(

            "price_usd"

        )



    elif sort=="Price High → Low":

        results = results.sort_values(

            "price_usd",

            ascending=False

        )




    for _,row in results.iterrows():

        product_card(row)




# ============================================================
# DISPLAY RESULTS
# ============================================================



if (

    "profile_recommendations"

    in st.session_state

):


    results = st.session_state.profile_recommendations.copy()



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