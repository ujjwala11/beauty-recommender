import streamlit as st


st.title(
"✨ AI Beauty Guide"
)


skin = st.selectbox(
"Skin Type",
[
"Dry",
"Oily",
"Combination",
"Sensitive"
]
)


concern = st.selectbox(
"Concern",
[
"Acne",
"Dark spots",
"Hydration",
"Aging"
]
)



if st.button(
"Generate Routine"
):


    st.success(
f"""
Morning Routine:

1. Gentle cleanser
2. {skin} friendly moisturizer
3. Treatment for {concern}
4. SPF 50 sunscreen


Night Routine:

1. Cleanser
2. Serum
3. Moisturizer

"""
)