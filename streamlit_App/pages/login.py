import streamlit as st

from utils.auth import (
    login,
    register_user
)



st.title(
    "💄 Beauty AI Login"
)



option = st.radio(

    "Choose",

    [
        "Login",
        "Create Account"
    ]

)



email = st.text_input(
    "Email"
)


password = st.text_input(
    "Password",
    type="password"
)





if option=="Create Account":


    if st.button(
        "Register"
    ):


        if register_user(
            email,
            password
        ):

            st.success(
                "Account created! Login now."
            )


        else:

            st.error(
                "User already exists"
            )




else:


    if st.button(
        "Login"
    ):


        if login(
            email,
            password
        ):


            st.success(
                "Welcome to Beauty AI 💄"
            )


            st.switch_page(
                "app.py"
            )


        else:


            st.error(
                "Invalid email or password"
            )