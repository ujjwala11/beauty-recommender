import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import time



# ==========================================
# PATHS
# ==========================================


ROOT = Path(__file__).resolve().parent.parent


DATA_PATH = (
    ROOT
    /
    "data"
    /
    "processed"
    /
    "recommendation"
)


products = pd.read_csv(
    DATA_PATH /
    "products_processed_popularity.csv",
    low_memory=False
)



# ==========================================
# FIX COLUMNS
# ==========================================


if "brand_name" not in products.columns:

    products["brand_name"]=""



if "product_name" not in products.columns:

    raise Exception(
        "product_name missing"
    )



products = products[
    [
        "product_id",
        "product_name",
        "brand_name"
    ]
].drop_duplicates()



# ==========================================
# IMAGE SEARCH FUNCTION
# ==========================================


def get_image(product_name, brand):


    query = (
        f"{brand} {product_name}"
    )


    url = (
        "https://www.google.com/search?"
        f"tbm=isch&q={query}"
    )


    headers = {

        "User-Agent":
        "Mozilla/5.0"

    }



    try:


        response = requests.get(

            url,

            headers=headers,

            timeout=10

        )


        soup = BeautifulSoup(

            response.text,

            "html.parser"

        )


        images = soup.find_all(
            "img"
        )


        for img in images:


            src = img.get(
                "src"
            )


            if src and src.startswith(
                "http"
            ):


                return src



    except Exception:


        return None



    return None




# ==========================================
# SCRAPE
# ==========================================


results=[]


for _,row in tqdm(
    products.iterrows(),
    total=len(products)
):


    image = get_image(

        row["product_name"],

        row["brand_name"]

    )


    results.append(

        {

        "product_id":
        row["product_id"],


        "image_url":
        image

        }

    )


    time.sleep(
        1
    )




# ==========================================
# SAVE
# ==========================================


image_df = pd.DataFrame(
    results
)


image_df.to_csv(

    DATA_PATH /
    "product_images.csv",

    index=False

)



print(
    "Saved:",
    len(image_df)
)