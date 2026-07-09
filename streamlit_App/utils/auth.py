import streamlit as st
import hashlib
import json
from pathlib import Path



# ============================================================
# USER DATABASE
# ============================================================


USER_FILE = Path(__file__).parent / "users.json"



# Create database if missing

if not USER_FILE.exists():

    with open(USER_FILE,"w") as f:

        json.dump(
            {},
            f
        )




# ============================================================
# PASSWORD HASH
# ============================================================


def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()




# ============================================================
# LOAD USERS
# ============================================================


def load_users():

    with open(USER_FILE,"r") as f:

        return json.load(f)




# ============================================================
# SAVE USERS
# ============================================================


def save_users(users):

    with open(USER_FILE,"w") as f:

        json.dump(
            users,
            f,
            indent=4
        )





# ============================================================
# REGISTER
# ============================================================


def register_user(email,password):


    users = load_users()



    if email in users:

        return False



    users[email] = hash_password(
        password
    )


    save_users(users)


    return True






# ============================================================
# LOGIN
# ============================================================


def login(email,password):


    users = load_users()



    if email not in users:

        return False



    if users[email] == hash_password(password):


        st.session_state.logged_in=True

        st.session_state.user=email


        return True



    return False





# ============================================================
# LOGOUT
# ============================================================


def logout():

    st.session_state.logged_in=False

    st.session_state.user=None