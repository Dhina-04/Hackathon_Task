import streamlit as st
import requests
from PIL import Image
import os

st.set_page_config(page_title="Event Upload", layout="wide")
st.title("📸 Upload Event Images")

uploaded_images = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
num_images = st.slider("How many images do you want in the carousel?", 1, 10, 3)

if uploaded_images:
    st.success(f"{len(uploaded_images)} images uploaded successfully.")
    st.info("They will be sent to AI for quality filtering and caption generation.")

    if st.button("🚀 Send to Backend for Processing"):
        files_payload = {}
        for i, file in enumerate(uploaded_images):
            files_payload[f"file{i}"] = (file.name, file.getvalue(), file.type)

        # Replace with your actual n8n webhook URL
        webhook_url = "http://localhost:5678/webhook/event-carousel-upload"

        try:
            response = requests.post(
                webhook_url,
                files=files_payload,
                data={"num_required": num_images}
            )
            if response.status_code == 200:
                st.success("✅ Sent to backend!")
                st.json(response.json())
            else:
                st.error(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
