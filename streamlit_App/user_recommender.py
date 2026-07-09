# user_recommender.py

import pandas as pd
import numpy as np



# ============================================================
# BUILD USER PROFILE
# ============================================================


def build_user_profile(
        user_id,
        reviews,
        products
):


    empty_profile = {

        "user_id": user_id,

        "total_reviews": 0,

        "avg_price": 0,

        "avg_rating": 0,

        "favorite_categories": [],

        "favorite_brands": [],

        "liked_products": []

    }



    if reviews is None or reviews.empty:

        return empty_profile



    if "author_id" not in reviews.columns:

        return empty_profile



    # -----------------------------
    # User review history
    # -----------------------------


    user_history = reviews[

        reviews["author_id"]

        ==
        user_id

    ].copy()



    if user_history.empty:

        return empty_profile



    # -----------------------------
    # Merge product information
    # -----------------------------


    product_cols = [

        "product_id",

        "product_name",

        "brand_name",

        "primary_category",

        "price_usd"

    ]


    available_cols = [

        col

        for col in product_cols

        if col in products.columns

    ]



    history = user_history.merge(

        products[available_cols],

        on="product_id",

        how="left"

    )



    # -----------------------------
    # Average price
    # -----------------------------


    if "price_usd" in history.columns:


        avg_price = (

            pd.to_numeric(

                history["price_usd"],

                errors="coerce"

            )

            .mean()

        )

    else:

        avg_price = 0



    if pd.isna(avg_price):

        avg_price = 0




    # -----------------------------
    # Average rating
    # -----------------------------


    if "rating" in history.columns:


        avg_rating = (

            pd.to_numeric(

                history["rating"],

                errors="coerce"

            )

            .mean()

        )


    else:

        avg_rating = 0



    if pd.isna(avg_rating):

        avg_rating = 0





    # -----------------------------
    # Favorite categories
    # -----------------------------


    if "primary_category" in history.columns:


        favorite_categories = (

            history["primary_category"]

            .dropna()

            .value_counts()

            .head(5)

            .index

            .tolist()

        )


    else:

        favorite_categories = []





    # -----------------------------
    # Favorite brands
    # -----------------------------


    if "brand_name" in history.columns:


        favorite_brands = (

            history["brand_name"]

            .dropna()

            .value_counts()

            .head(5)

            .index

            .tolist()

        )


    else:

        favorite_brands = []






    # -----------------------------
    # Products user interacted with
    # -----------------------------


    liked_products = []



    required = [

        "product_id",

        "product_name"

    ]


    if all(

        col in history.columns

        for col in required

    ):


        liked_products = (

            history[required]

            .drop_duplicates()

            .head(10)

            .to_dict(

                "records"

            )

        )





    return {


        "user_id": user_id,


        "total_reviews": len(history),


        "avg_price": float(avg_price),


        "avg_rating": float(avg_rating),


        "favorite_categories":

        favorite_categories,


        "favorite_brands":

        favorite_brands,


        "liked_products":

        liked_products

    }






# ============================================================
# PERSONALIZED RECOMMENDATIONS
# ============================================================


def recommend_for_user(

        user_id,

        reviews,

        products,

        recommend_function,

        top_n=10

):



    profile = build_user_profile(

        user_id,

        reviews,

        products

    )



    # --------------------------------
    # Cold start user
    # --------------------------------


    if profile["total_reviews"] == 0:


        if "popularity_norm" in products.columns:


            return (

                products

                .sort_values(

                    "popularity_norm",

                    ascending=False

                )

                .head(top_n)

            )


        return products.head(top_n)





    # --------------------------------
    # Existing user
    # --------------------------------


    liked_products = (

        profile["liked_products"]

    )



    if len(liked_products)==0:


        return products.head(top_n)





    seed_products = [

        item["product_id"]

        for item in liked_products

    ]



    recommendations=[]



    for product_id in seed_products:


        try:


            result = recommend_function(

                product_id,

                top_n

            )


            if result is not None and not result.empty:


                recommendations.append(

                    result

                )


        except Exception:


            continue





    if len(recommendations)==0:


        return products.head(top_n)





    final = pd.concat(

        recommendations,

        ignore_index=True

    )





    # remove products already seen


    final = final[

        ~final["product_id"]

        .isin(seed_products)

    ]





    # remove duplicates


    final = final.drop_duplicates(

        "product_id"

    )





    # ranking


    score_columns = [

        "final_score",

        "content_score",

        "collab_score",

        "popularity_norm"

    ]



    for col in score_columns:


        if col in final.columns:


            final = final.sort_values(

                col,

                ascending=False

            )

            break





    return final.head(top_n)