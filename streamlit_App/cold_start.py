import json
from pathlib import Path
import pandas as pd



# ============================================================
# PATHS
# ============================================================


DATA_DIR = Path(__file__).resolve().parent / "data"


DATA_DIR.mkdir(
    exist_ok=True
)


PREF_FILE = DATA_DIR / "user_preferences.json"



# Create file if missing

if not PREF_FILE.exists():

    with open(PREF_FILE,"w") as f:

        json.dump({},f)




# ============================================================
# SAVE USER PREFERENCES
# ============================================================


def save_user_preferences(
        user_id,
        preferences
):


    with open(
        PREF_FILE,
        "r"
    ) as f:

        users=json.load(f)



    users[str(user_id)] = preferences



    with open(
        PREF_FILE,
        "w"
    ) as f:

        json.dump(
            users,
            f,
            indent=4
        )





# ============================================================
# LOAD USER PREFERENCES
# ============================================================


def load_user_preferences(
        user_id
):


    with open(
        PREF_FILE,
        "r"
    ) as f:

        users=json.load(f)



    return users.get(

        str(user_id),

        {}

    )





# ============================================================
# COLD START ENGINE
# ============================================================


def cold_start_recommend(

        products,

        preferences,

        top_n=10

):


    df = products.copy()



    # safety columns


    if "primary_category" not in df.columns:

        df["primary_category"]=""



    if "brand_name" not in df.columns:

        df["brand_name"]=""



    if "price_usd" not in df.columns:

        df["price_usd"]=0



    if "popularity_norm" not in df.columns:

        df["popularity_norm"]=0



    df["cold_score"]=0





    # ----------------------------------
    # Category
    # ----------------------------------


    if preferences.get("category"):


        df.loc[

            df["primary_category"]

            .astype(str)

            .str.contains(

                preferences["category"],

                case=False,

                na=False

            ),

            "cold_score"

        ] += 5





    # ----------------------------------
    # Brand
    # ----------------------------------


    if preferences.get("brand"):


        df.loc[

            df["brand_name"]

            .astype(str)

            .str.contains(

                preferences["brand"],

                case=False,

                na=False

            ),

            "cold_score"

        ] += 3





    # ----------------------------------
    # Budget
    # ----------------------------------


    budget = preferences.get(
        "budget"
    )


    if budget=="Low":


        df.loc[

            df["price_usd"]<=30,

            "cold_score"

        ] += 3



    elif budget=="Medium":


        df.loc[

            (df["price_usd"]>30)

            &

            (df["price_usd"]<=80),

            "cold_score"

        ] += 3



    elif budget=="High":


        df.loc[

            df["price_usd"]>80,

            "cold_score"

        ] +=3





    # ----------------------------------
    # Popular fallback
    # ----------------------------------


    df["cold_score"] += (

        df["popularity_norm"]

        *2

    )





    return (

        df

        .sort_values(

            "cold_score",

            ascending=False

        )

        .head(top_n)

    )