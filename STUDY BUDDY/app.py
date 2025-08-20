import streamlit as st
import utils

st.set_page_config(page_title="AI Tutor", layout="wide")

# Session state init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login / Signup
if not st.session_state.logged_in:
    st.title("🔑 Welcome to AI Tutor")
    choice = st.radio("Login or Sign Up", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Submit"):
        if choice == "Login":
            if utils.login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid credentials.")
        else:
            if utils.register_user(username, password):
                st.success("Account created! Please login.")
            else:
                st.error("User already exists.")
else:
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Study", "Quiz", "Doubts", "Logout"])

    if page == "Logout":
        st.session_state.logged_in = False
        st.experimental_rerun()

    elif page == "Dashboard":
        utils.show_dashboard(st.session_state.username)

    elif page == "Study":
        utils.study_mode(st.session_state.username)

    elif page == "Quiz":
        utils.quiz_mode(st.session_state.username)

    elif page == "Doubts":
        utils.doubt_mode(st.session_state.username)
