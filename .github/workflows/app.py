import streamlit as st
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db, storage
from PIL import Image
import tempfile
import uuid
import os
import datetime

# ---------------------------
# 🔥 FIREBASE CONFIG
# ---------------------------

if not firebase_admin._apps:
    cred = credentials.Certificate("apicall-4ca93-firebase-adminsdk-fbsvc-eebe670471.json")  # download from firebase
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://apicall-4ca93-default-rtdb.firebaseio.com",
        'storageBucket': "apicall-4ca93.firebasestorage.app"
    })

bucket = storage.bucket()

# ---------------------------
# 🎨 UI CONFIG
# ---------------------------

st.set_page_config(page_title="Face Verification System", layout="centered")

st.markdown("""
<style>
.main { background-color: #0f172a; color:white; }
button { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔐 Real Face Verification System")

menu = st.sidebar.selectbox("Select Option", ["Register Face", "Verify Face"])

# ---------------------------
# 📌 FUNCTION: Upload Image To Firebase Storage
# ---------------------------

def upload_to_storage(file_path, filename):
    blob = bucket.blob(f"faces/{filename}")
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url

# ---------------------------
# 📌 FUNCTION: Save Encoding To Firebase DB
# ---------------------------

def save_to_firebase(name, encoding, image_url):
    ref = db.reference("faces")
    ref.push({
        "name": name,
        "encoding": encoding.tolist(),
        "image_url": image_url,
        "created_at": str(datetime.datetime.now())
    })

# ---------------------------
# 📌 FUNCTION: Load All Faces
# ---------------------------

def load_faces():
    ref = db.reference("faces")
    data = ref.get()
    known_faces = []

    if data:
        for key in data:
            person = data[key]
            known_faces.append({
                "name": person["name"],
                "encoding": np.array(person["encoding"])
            })

    return known_faces

# ===========================
# 🟢 REGISTER FACE
# ===========================

if menu == "Register Face":

    st.subheader("📸 Register New Face")

    name = st.text_input("Enter Name")

    image = st.camera_input("Take a Picture")

    if image and name:

        img = Image.open(image)
        img_np = np.array(img)

        encodings = face_recognition.face_encodings(img_np)

        if len(encodings) == 0:
            st.error("No face detected!")
        else:
            encoding = encodings[0]

            # Save temp image
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            img.save(temp_file.name)

            image_url = upload_to_storage(temp_file.name, str(uuid.uuid4()) + ".jpg")

            save_to_firebase(name, encoding, image_url)

            st.success(f"✅ {name} Registered Successfully!")

# ===========================
# 🔵 VERIFY FACE
# ===========================

elif menu == "Verify Face":

    st.subheader("🔎 Verify Your Face")

    image = st.camera_input("Take a Picture")

    if image:

        img = Image.open(image)
        img_np = np.array(img)

        encodings = face_recognition.face_encodings(img_np)

        if len(encodings) == 0:
            st.error("No face detected!")
        else:
            encoding = encodings[0]

            known_faces = load_faces()

            if len(known_faces) == 0:
                st.warning("No registered faces in database.")
            else:
                matched = False

                for person in known_faces:
                    result = face_recognition.compare_faces(
                        [person["encoding"]],
                        encoding,
                        tolerance=0.5
                    )

                    if result[0]:
                        st.success(f"✅ Verified: {person['name']}")
                        matched = True
                        break

                if not matched:
                    st.error("❌ Face Not Matched")
