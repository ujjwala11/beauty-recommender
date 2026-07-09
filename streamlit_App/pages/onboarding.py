import streamlit as st


from cold_start import save_user_preferences



st.set_page_config(

    page_title="Beauty AI Setup",

    page_icon="💄"

)



st.title(
    "💄 Personal Beauty Setup"
)



if "logged_in" not in st.session_state:

    st.session_state.logged_in=False



if not st.session_state.logged_in:

    st.warning(
        "Please login first"
    )

    st.stop()



user_id = st.session_state.user





st.write(

    "Tell us about yourself so AI can personalize recommendations"

)





skin_type = st.selectbox(

    "Skin Type",

    [

        "Dry",

        "Oily",

        "Combination",

        "Sensitive",

        "Normal"

    ]

)





concern = st.selectbox(

    "Main Concern",

    [

        "Acne",

        "Anti Aging",

        "Hydration",

        "Dark Spots",

        "Sensitive Skin",

        "None"

    ]

)





category = st.selectbox(

    "Interested Category",

    [

        "Skincare",

        "Makeup",

        "Hair",

        "Fragrance",

        "Body"

    ]

)





budget = st.selectbox(

    "Budget",

    [

        "Low",

        "Medium",

        "High"

    ]

)





brands=[

    "None",

    "Rare Beauty",

    "Sephora Collection",

    "The Ordinary",

    "CeraVe",

    "Clinique"

]



brand=st.selectbox(

    "Favourite Brand",

    brands

)







if st.button(

    "Create My Beauty Profile"

):


    preferences={


        "skin_type":skin_type,


        "concern":concern,


        "category":category,


        "budget":budget,


        "brand":brand

    }





    save_user_preferences(

        user_id,

        preferences

    )



    st.success(

        "Profile created!"

    )



    st.switch_page(

        "pages/user_profile.py"

    )