# ============================================================
# recommender.py
# Beauty AI Recommendation Engine
# ============================================================

import pandas as pd
import numpy as np
import joblib

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "recommendation"
)


DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "recommendation"
)



# ============================================================
# LOAD DATA
# ============================================================


products = pd.read_csv(
    DATA_DIR / "products_processed_popularity.csv",
    low_memory=False
)



# ============================================================
# LOAD REVIEWS SAFELY
# ============================================================


reviews_files = list(
    DATA_DIR.glob("*reviews*csv")
)


if len(reviews_files) > 0:


    reviews = pd.read_csv(

        reviews_files[0],

        low_memory=False

    )


else:


    raise FileNotFoundError(

        "No reviews csv found inside recommendation folder"

    )



# ============================================================
# PRODUCT COLUMN NORMALIZATION
# ============================================================


def add_column(
        df,
        column,
        default
):

    if column not in df.columns:

        df[column] = default



add_column(
    products,
    "product_name",
    "Unknown Product"
)


add_column(
    products,
    "brand_name",
    "Unknown Brand"
)


add_column(
    products,
    "primary_category",
    "Beauty"
)


add_column(
    products,
    "price_usd",
    0
)


add_column(
    products,
    "image_url",
    "https://via.placeholder.com/300"
)



# popularity


if "popularity_norm" not in products.columns:


    if "popularity_score" in products.columns:


        max_value = (
            products["popularity_score"]
            .max()
        )


        products["popularity_norm"] = (

            products["popularity_score"]

            /

            max_value

        )


    else:

        products["popularity_norm"] = 0





# ============================================================
# LOAD CONTENT MODEL
# ============================================================


content_similarity = joblib.load(

    MODEL_DIR /
    "content_based/cosine_similarity.pkl"

)



content_products = joblib.load(

    MODEL_DIR /
    "content_based/product_indices.pkl"

)




# ============================================================
# LOAD COLLAB MODEL
# ============================================================


item_knn = joblib.load(

    MODEL_DIR /
    "collab/item_knn.pkl"

)



item_user_matrix = joblib.load(

    MODEL_DIR /
    "collab/item_user_matrix.pkl"

)



cf_products = pd.read_csv(

    MODEL_DIR /
    "collab/product_map.csv"

)



# attach missing metadata

cf_products = cf_products.merge(

    products[
        [
            "product_id",
            "price_usd",
            "image_url",
            "primary_category",
            "brand_name"
        ]
    ],

    on="product_id",

    how="left"

)



cf_product_to_idx = dict(

    zip(

        cf_products["product_id"],

        cf_products["product_idx"]

    )

)





# ============================================================
# HELPER
# ============================================================


def attach_product_details(df):


    if df.empty:

        return df



    result = df.merge(

        products[
            [
                "product_id",
                "product_name",
                "brand_name",
                "primary_category",
                "price_usd",
                "image_url"
            ]
        ],

        on="product_id",

        how="left"

    )


    return result





# ============================================================
# CONTENT BASED
# ============================================================


def recommend_content(
        product_id,
        top_n=10
):


    match = content_products[

        content_products["product_id"]
        ==
        product_id

    ]



    if match.empty:


        return popularity_fallback(
            top_n
        )



    product_idx = int(

        match.iloc[0]["product_idx"]

    )



    scores = content_similarity[

        product_idx

    ]



    indexes = np.argsort(

        scores

    )[::-1]



    output=[]



    for idx in indexes:


        if idx == product_idx:

            continue



        output.append(

            {

                "product_id":

                content_products.iloc[idx]["product_id"],


                "content_score":

                float(
                    scores[idx]
                )

            }

        )


        if len(output)==top_n:

            break



    result = pd.DataFrame(
        output
    )


    return attach_product_details(
        result
    )





# ============================================================
# COLLABORATIVE FILTERING
# ============================================================


def recommend_collaborative(
        product_id,
        top_n=10
):


    if product_id not in cf_product_to_idx:


        return popularity_fallback(
            top_n
        )



    idx = cf_product_to_idx[product_id]



    distances, indices = item_knn.kneighbors(

        item_user_matrix[idx],

        n_neighbors=top_n+1

    )



    output=[]



    for distance, neighbour in zip(

        distances[0][1:],

        indices[0][1:]

    ):


        output.append(

            {

                "product_idx":

                neighbour,


                "collab_score":

                float(
                    1-distance
                )

            }

        )



    result = pd.DataFrame(
        output
    )



    result = result.merge(

        cf_products,

        on="product_idx",

        how="left"

    )



    return result.sort_values(

        "collab_score",

        ascending=False

    ).head(top_n)







# ============================================================
# HYBRID
# ============================================================


def recommend_hybrid(
        product_id,
        top_n=10
):


    content = recommend_content(
        product_id,
        top_n * 3
    )


    collab = recommend_collaborative(
        product_id,
        top_n * 3
    )


    # -----------------------------
    # Extract scores safely
    # -----------------------------

    if not content.empty and "content_score" in content.columns:

        content_scores = content[
            [
                "product_id",
                "content_score"
            ]
        ]

    else:

        content_scores = pd.DataFrame(
            columns=[
                "product_id",
                "content_score"
            ]
        )



    if not collab.empty and "collab_score" in collab.columns:

        collab_scores = collab[
            [
                "product_id",
                "collab_score"
            ]
        ]

    else:

        collab_scores = pd.DataFrame(
            columns=[
                "product_id",
                "collab_score"
            ]
        )



    # -----------------------------
    # Merge
    # -----------------------------


    hybrid = content_scores.merge(

        collab_scores,

        on="product_id",

        how="outer"

    )



    # -----------------------------
    # Ensure columns exist
    # -----------------------------


    if "content_score" not in hybrid.columns:

        hybrid["content_score"] = 0



    if "collab_score" not in hybrid.columns:

        hybrid["collab_score"] = 0



    hybrid["content_score"] = (

        pd.to_numeric(

            hybrid["content_score"],

            errors="coerce"

        )

        .fillna(0)

    )



    hybrid["collab_score"] = (

        pd.to_numeric(

            hybrid["collab_score"],

            errors="coerce"

        )

        .fillna(0)

    )



    # -----------------------------
    # Add popularity
    # -----------------------------


    hybrid = hybrid.merge(

        products[
            [
                "product_id",
                "popularity_norm"
            ]
        ],

        on="product_id",

        how="left"

    )



    hybrid["popularity_norm"] = (

        pd.to_numeric(

            hybrid["popularity_norm"],

            errors="coerce"

        )

        .fillna(0)

    )



    # -----------------------------
    # Final score
    # -----------------------------


    hybrid["final_score"] = (

        0.5 *
        hybrid["content_score"]

        +

        0.3 *
        hybrid["collab_score"]

        +

        0.2 *
        hybrid["popularity_norm"]

    )



    # -----------------------------
    # Product details
    # -----------------------------


    hybrid = hybrid.merge(

        products[
            [
                "product_id",
                "product_name",
                "brand_name",
                "primary_category",
                "price_usd",
                "image_url"
            ]
        ],

        on="product_id",

        how="left"

    )



    hybrid["reason"] = np.where(

        hybrid["content_score"] >

        hybrid["collab_score"],


        "Similar beauty profile",

        "Loved by similar users"

    )



    return hybrid.sort_values(

        "final_score",

        ascending=False

    ).head(top_n)



# ============================================================
# COLD START
# ============================================================


def popularity_fallback(
        top_n=10
):


    return products.sort_values(

        "popularity_norm",

        ascending=False

    ).head(top_n)





# backwards compatibility

hybrid_recommend = recommend_hybrid