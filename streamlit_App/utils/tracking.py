import pandas as pd
from pathlib import Path
from datetime import datetime
import os


# ============================================================
# STORAGE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


DATA_DIR = (
    BASE_DIR
    /
    "data"
)


EVENT_FILE = (
    DATA_DIR
    /
    "user_events.csv"
)



# create folder automatically

DATA_DIR.mkdir(
    exist_ok=True
)



# ============================================================
# ADD EVENT
# ============================================================


def add_event(
    user_id,
    product_id,
    event_type
):


    event = {

        "user_id": user_id,

        "product_id": product_id,

        "event_type": event_type,

        "timestamp":
        datetime.now()

    }


    if EVENT_FILE.exists():

        df = pd.read_csv(
            EVENT_FILE
        )


        df = pd.concat(

            [
                df,
                pd.DataFrame([event])
            ],

            ignore_index=True

        )


    else:


        df = pd.DataFrame(
            [event]
        )


    df.to_csv(

        EVENT_FILE,

        index=False

    )