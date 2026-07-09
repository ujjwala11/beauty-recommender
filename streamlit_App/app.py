# ============================================================
# app.py
# Beauty AI Store
# ============================================================


import streamlit as st
import pandas as pd


from recommender import (
    products,
    recommend_content,
    recommend_collaborative,
    recommend_hybrid,
    popularity_fallback,
)


from utils.ui_components import product_card
from utils.auth import logout



# ============================================================
# CONFIG
# ============================================================


st.set_page_config(

    page_title="Beauty AI Store",

    page_icon="💄",

    layout="wide"

)



# ============================================================
# LOGIN CHECK
# ============================================================


if "logged_in" not in st.session_state:

    st.session_state.logged_in = False



if not st.session_state.logged_in:


    st.warning(
        "🔒 Please login first"
    )

    st.stop()





# ============================================================
# SESSION STATE
# ============================================================


if "results" not in st.session_state:

    st.session_state.results = pd.DataFrame()



if "selected_product" not in st.session_state:

    st.session_state.selected_product = None






# ============================================================
# DATA SAFETY
# ============================================================


products = products.copy()



def ensure_column(
        df,
        col,
        default
):

    if col not in df.columns:

        df[col] = default




ensure_column(
    products,
    "product_name",
    "Unknown Product"
)


ensure_column(
    products,
    "brand_name",
    "Unknown Brand"
)


ensure_column(
    products,
    "primary_category",
    "Beauty"
)


ensure_column(
    products,
    "price_usd",
    0
)


ensure_column(
    products,
    "image_url",
    "https://via.placeholder.com/300"
)





# ============================================================
# SIDEBAR
# ============================================================


st.sidebar.title(
    "💄 Beauty AI Store"
)


st.sidebar.write(

    f"Welcome {st.session_state.get('user','User')}"

)



if st.sidebar.button(
    "Logout"
):

    logout()

    st.rerun()



page = st.sidebar.radio(

    "Navigate",

    [

        "🛍 Shop",

        "✨ AI Recommendations"

    ]

)





# ============================================================
# SHOP PAGE
# ============================================================


if page=="🛍 Shop":


    st.title(
        "💄 Beauty Marketplace"
    )


    st.write(

        "Discover skincare and beauty products powered by AI"

    )



    # filters


    st.sidebar.subheader(
        "Filters"
    )


    brand_options=[

        "All"

    ] + sorted(

        products["brand_name"]

        .dropna()

        .unique()

        .tolist()

    )



    category_options=[

        "All"

    ] + sorted(

        products["primary_category"]

        .dropna()

        .unique()

        .tolist()

    )



    brand=st.sidebar.selectbox(

        "Brand",

        brand_options

    )


    category=st.sidebar.selectbox(

        "Category",

        category_options

    )



    data=products.copy()



    if brand!="All":

        data=data[

            data["brand_name"]

            ==
            brand

        ]



    if category!="All":

        data=data[

            data["primary_category"]

            ==
            category

        ]




    search=st.text_input(

        "🔍 Search"

    )



    if search:


        data=data[

            data["product_name"]

            .str.contains(

                search,

                case=False,

                na=False

            )

        ]



    st.subheader(
        "Products"
    )



    cols=st.columns(4)



    for i,(_,row) in enumerate(

        data.head(40).iterrows()

    ):


        with cols[i%4]:


            product_card(row)







# ============================================================
# RECOMMENDATION PAGE
# ============================================================


else:


    st.title(
        "✨ AI Recommendation Engine"
    )


    product_names = (
    products["product_name"]
    .dropna()
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)



    selected_name = st.selectbox(

        "Choose product",

        product_names

    )



    selected_id = products.loc[
    products["product_name"] == selected_name,
    "product_id",
    ].iat[0]



    model=st.radio(

        "Recommendation Model",

        [

            "Hybrid",

            "Content Based",

            "Collaborative Filtering"

        ],

        horizontal=True

    )



    top_n=st.slider(

        "Recommendations",

        5,

        20,

        10

    )

    if st.button("🚀 Generate"):


     with st.spinner("AI is finding recommendations..."):


        try:


            if model == "Hybrid":

                results = recommend_hybrid(
                    selected_id,
                    top_n
                )


            elif model == "Content Based":

                results = recommend_content(
                    selected_id,
                    top_n
                )


            else:

                results = recommend_collaborative(
                    selected_id,
                    top_n
                )


            st.write("DEBUG OUTPUT")
            st.write(results.head())


            if results.empty:

                st.warning(
                    "No AI recommendations found"
                )

            else:

                st.success(
                    f"{len(results)} recommendations generated"
                )


            st.session_state.results = results


        except Exception as e:

            st.exception(e)
    





# ============================================================
# DISPLAY
# ============================================================


if not st.session_state.results.empty:


    st.subheader(

        "Recommended Products"

    )



    results=st.session_state.results.copy()



    sort=st.selectbox(

        "Sort by",

        [

            "AI Score",

            "Price Low → High",

            "Price High → Low"

        ]

    )




    if sort=="AI Score":


        possible=[

            "final_score",

            "content_score",

            "collab_score"

        ]


        for col in possible:


            if col in results.columns:


                results=results.sort_values(

                    col,

                    ascending=False

                )

                break



    elif sort=="Price Low → High":


        results["price_usd"]=pd.to_numeric(

            results["price_usd"],

            errors="coerce"

        ).fillna(0)



        results=results.sort_values(

            "price_usd"

        )



    else:


        results["price_usd"]=pd.to_numeric(

            results["price_usd"],

            errors="coerce"

        ).fillna(0)



        results=results.sort_values(

            "price_usd",

            ascending=False

        )




    cols=st.columns(4)



    for i,(_,row) in enumerate(

        results.iterrows()

    ):


        with cols[i%4]:


            product_card(row)