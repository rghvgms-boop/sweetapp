import streamlit as st
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from PIL import Image
import tempfile
import base64
import json

# ---------------------------
# 🔥 FIREBASE INIT (Secrets Based)
# ---------------------------

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://apicall-4ca93-default-rtdb.firebaseio.com"
    })

# ---------------------------
# 🎨 UI
# ---------------------------

st.set_page_config(page_title="Face Verification System", layout="centered")

st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 Face Verification System")

menu = st.sidebar.selectbox("Select Option", ["Register", "Verify"])

# ---------------------------
# 📌 FACE DETECTION FUNCTION
# ---------------------------

def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

# ---------------------------
# 📌 REGISTER
# ---------------------------

if menu == "Register":

    st.subheader("📸 Register New Face")
    name = st.text_input("Enter Name")

    image = st.camera_input("Take a Picture")

    if image and name:

        img = Image.open(image)
        img_np = np.array(img)

        faces = detect_face(img_np)

        if len(faces) == 0:
            st.error("No face detected!")
        else:
            # Convert image to base64
            _, buffer = cv2.imencode(".jpg", img_np)
            img_base64 = base64.b64encode(buffer).decode()

            ref = db.reference("faces")
            ref.push({
                "name": name,
                "image": img_base64
            })

            st.success(f"✅ {name} Registered Successfully!")

# ---------------------------
# 📌 VERIFY
# ---------------------------

elif menu == "Verify":

    st.subheader("🔎 Verify Face")
    image = st.camera_input("Take a Picture")

    if image:

        img = Image.open(image)
        img_np = np.array(img)

        faces = detect_face(img_np)

        if len(faces) == 0:
            st.error("No face detected!")
        else:
            ref = db.reference("faces")
            data = ref.get()

            if not data:
                st.warning("No registered users found.")
            else:
                matched = False

                for key in data:
                    person = data[key]
                    stored_img = base64.b64decode(person["image"])
                    stored_np = np.frombuffer(stored_img, np.uint8)
                    stored_img = cv2.imdecode(stored_np, cv2.IMREAD_COLOR)

                    stored_faces = detect_face(stored_img)

                    if len(stored_faces) > 0:
                        matched = True
                        st.success(f"✅ Face Detected (User: {person['name']})")
                        break

                if not matched:
                    st.error("❌ Face Not Matched")
                    
