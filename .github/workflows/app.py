import streamlit as st
import random
import time

st.set_page_config(page_title="Face Verification Demo")

st.title("🔐 Face Verification System")

if "step" not in st.session_state:
    st.session_state.step = "welcome"

# Welcome Screen
if st.session_state.step == "welcome":
    st.subheader("Verify Your Identity")
    if st.button("Start Verification"):
        st.session_state.step = "camera"
        st.rerun()

# Camera Screen
elif st.session_state.step == "camera":
    st.subheader("Position Your Face")
    st.image("https://placehold.co/600x400?text=Camera+Preview")

    if st.button("Capture Photo"):
        st.session_state.step = "verifying"
        st.rerun()

# Verifying Screen
elif st.session_state.step == "verifying":
    st.subheader("Verifying...")
    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)

    success = random.random() > 0.3

    if success:
        st.session_state.step = "success"
    else:
        st.session_state.step = "failure"

    st.rerun()

# Success Screen
elif st.session_state.step == "success":
    st.success("✅ Verification Successful")
    if st.button("Continue"):
        st.session_state.step = "welcome"
        st.rerun()

# Failure Screen
elif st.session_state.step == "failure":
    st.error("❌ Verification Failed")
    if st.button("Try Again"):
        st.session_state.step = "camera"
        st.rerun()
