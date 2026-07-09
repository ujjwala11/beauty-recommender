# ============================================================
# recommender.py
# Beauty AI Recommendation Engine
# ============================================================

import streamlit as st
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "processed" / "recommendation"

MODEL_DIR = PROJECT_ROOT / "models" / "recommendation"



# ============================================================
# LOAD HELPERS
# ============================================================


def load_csv(path):

    if not path.exists():
        raise FileNotFoundError(path)

    return pd.read_csv(
        path,
        low_memory=False
    )



def load_model(path):

    if not path.exists():
        raise FileNotFoundError(path)

    return joblib.load(path)



def ensure_column(df,col,value):

    if col not in df.columns:
        df[col]=value



# ============================================================
# LOAD ENGINE
# ============================================================


@st.cache_resource(
    show_spinner="Loading AI recommendation engine..."
)
def load_recommender():


    products = load_csv(
        DATA_DIR /
        "products_processed_popularity.csv"
    )


    # safety

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
        ""
    )



    if "popularity_norm" not in products:


        if "popularity_score" in products:

            mx = products["popularity_score"].max()

            products["popularity_norm"] = (
                products["popularity_score"]/mx
                if mx>0 else 0
            )

        else:

            products["popularity_norm"]=0




    # CONTENT MODEL


    tfidf_matrix = load_model(

        MODEL_DIR /
        "content_based/tfidf_matrix.pkl"

    )


    product_indices = load_model(

        MODEL_DIR /
        "content_based/product_indices.pkl"

    )



    # COLLAB MODEL


    item_knn = load_model(

        MODEL_DIR /
        "collab/item_knn.pkl"

    )


    item_user_matrix = load_model(

        MODEL_DIR /
        "collab/item_user_matrix.pkl"

    )


    product_map = load_csv(

        MODEL_DIR /
        "collab/product_map.csv"

    )



    product_map = product_map.merge(

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



    product_to_idx = dict(

        zip(
            product_map.product_id,
            product_map.product_idx
        )

    )


    return (

        products,
        tfidf_matrix,
        product_indices,
        item_knn,
        item_user_matrix,
        product_map,
        product_to_idx

    )



(
products,
tfidf_matrix,
product_indices,
item_knn,
item_user_matrix,
product_map,
product_to_idx

)=load_recommender()



# ============================================================
# HELPERS
# ============================================================


def popularity_fallback(top_n):

    return (

        products
        .sort_values(
            "popularity_norm",
            ascending=False
        )
        .head(top_n)
        .copy()

    )




def attach_details(df):


    if df.empty:
        return df


    cols=[
        "product_id",
        "product_name",
        "brand_name",
        "primary_category",
        "price_usd",
        "image_url"
    ]


    missing=[
        c for c in cols
        if c not in df.columns
    ]


    if missing:

        df=df.merge(

            products[cols],

            on="product_id",

            how="left"

        )


    return df

# ============================================================
# CONTENT BASED RECOMMENDATION
# ============================================================


def recommend_content(product_id, top_n=10):


    if product_id not in product_indices["product_id"].values:

        return pd.DataFrame(
            columns=[
                "product_id",
                "content_score"
            ]
        )



    idx = int(

        product_indices.loc[
            product_indices["product_id"] == product_id,
            "product_idx"
        ].iloc[0]

    )



    if idx >= tfidf_matrix.shape[0]:

        return pd.DataFrame(
            columns=[
                "product_id",
                "content_score"
            ]
        )



    similarity = cosine_similarity(

        tfidf_matrix[idx],

        tfidf_matrix

    )[0]



    ranked = np.argsort(
        similarity
    )[::-1]



    recommendations=[]


    for i in ranked:


        # remove same product

        if i == idx:
            continue



        recommendations.append(

            {
                "product_id":
                    product_indices.iloc[i]["product_id"],

                "content_score":
                    float(similarity[i])

            }

        )


        if len(recommendations)>=top_n:

            break



    result=pd.DataFrame(
        recommendations
    )


    return attach_details(result)





# ============================================================
# COLLABORATIVE FILTERING
# ============================================================



def recommend_collaborative(product_id, top_n=10):


    if product_id not in product_to_idx:


        return pd.DataFrame(
            columns=[
                "product_id",
                "collab_score"
            ]
        )



    idx = product_to_idx[product_id]



    if idx >= item_user_matrix.shape[0]:


        return pd.DataFrame(
            columns=[
                "product_id",
                "collab_score"
            ]
        )



    neighbors = min(

        top_n + 1,

        item_user_matrix.shape[0]

    )



    distances,indices = item_knn.kneighbors(

        item_user_matrix[idx],

        n_neighbors=neighbors

    )



    output=[]



    for distance,neighbor in zip(

        distances[0][1:],

        indices[0][1:]

    ):


        match = product_map[

            product_map["product_idx"]

            ==

            neighbor

        ]



        if match.empty:

            continue



        output.append(

            {

                "product_id":
                    match.iloc[0]["product_id"],


                "collab_score":
                    float(1-distance)

            }

        )



    result=pd.DataFrame(output)



    return attach_details(result)





# ============================================================
# HYBRID ENGINE
# ============================================================


def recommend_hybrid(

        product_id,

        top_n=10,

        content_weight=0.5,

        collab_weight=0.3,

        popularity_weight=0.2

):


    content = recommend_content(

        product_id,

        top_n*3

    )


    collab = recommend_collaborative(

        product_id,

        top_n*3

    )



    # ensure columns exist


    if content.empty:

        content = pd.DataFrame(

            columns=[
                "product_id",
                "content_score"
            ]

        )



    if collab.empty:

        collab = pd.DataFrame(

            columns=[
                "product_id",
                "collab_score"
            ]

        )




    hybrid = content.merge(

        collab,

        on="product_id",

        how="outer"

    )



    if hybrid.empty:


        fallback = popularity_fallback(top_n)


        fallback["final_score"]=(
            fallback["popularity_norm"]
        )


        fallback["reason"]="Popular products"


        return fallback




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




    hybrid["content_score"] = (

        pd.to_numeric(

            hybrid["content_score"],

            errors="coerce"

        )

        .fillna(0)

    )



    hybrid["collab_score"]=(

        pd.to_numeric(

            hybrid["collab_score"],

            errors="coerce"

        )

        .fillna(0)

    )



    hybrid["popularity_norm"]=(

        pd.to_numeric(

            hybrid["popularity_norm"],

            errors="coerce"

        )

        .fillna(0)

    )



    # normalize


    for col in [

        "content_score",

        "collab_score",

        "popularity_norm"

    ]:


        maximum=hybrid[col].max()


        if maximum>0:

            hybrid[col]=hybrid[col]/maximum




    hybrid["final_score"]=(


        content_weight *
        hybrid["content_score"]


        +

        collab_weight *
        hybrid["collab_score"]


        +

        popularity_weight *
        hybrid["popularity_norm"]

    )



    hybrid["reason"]=np.where(

        hybrid["content_score"]

        >=

        hybrid["collab_score"],


        "Similar products",


        "Users also liked"

    )



    hybrid = attach_details(hybrid)



    return (

        hybrid

        .sort_values(

            "final_score",

            ascending=False

        )

        .drop_duplicates(

            "product_id"

        )

        .head(top_n)

        .reset_index(drop=True)

    )





# backward compatibility

hybrid_recommend = recommend_hybrid