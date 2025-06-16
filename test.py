import streamlit as st
from PIL import Image
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load Gemini API Key from .env or directly paste here
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyCghE5Vps0zVOYX64PUZCoNsRmWG3HPGcI") or "PASTE-YOUR-API-KEY-HERE"

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

def generate_caption_and_hashtags(image_path):
    model = genai.GenerativeModel('gemini-2.0-flash')
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    response = model.generate_content([
        "You're an expert event social media manager. Write a short caption and 5 relevant hashtags for this photo.",
        image_bytes
    ])
    return response.text.strip()

# Streamlit UI
st.set_page_config(page_title="Event Carousel Approver", layout="wide")
st.title("📸 Auto Photo Captioning & Approval")

uploaded_images = st.file_uploader("Upload Event Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_images:
    st.subheader("AI Carousel Generator")
    approved_data = []

    for img_file in uploaded_images:
        image = Image.open(img_file)
        img_path = f"temp_{img_file.name}"
        image.save(img_path)

        with st.spinner(f"Generating caption for {img_file.name}..."):
            try:
                caption_output = generate_caption_and_hashtags(img_path)
            except Exception as e:
                caption_output = f"❌ Error generating caption: {e}"

        st.image(image, width=300, caption="Preview")
        st.markdown(f"**✍️ AI-Generated Caption + Hashtags:**\n\n{caption_output}")

        approved = st.checkbox(f"✅ Approve this image: {img_file.name}")
        if approved:
            approved_data.append({
                "filename": img_file.name,
                "caption": caption_output
            })

        os.remove(img_path)

    if approved_data and st.button("🚀 Submit Approved Carousel"):
        webhook_url = "https://your-n8n-instance.webhook.url/approved-carousel"  # Replace with real URL
        with st.spinner("Sending to n8n backend..."):
            try:
                response = requests.post(webhook_url, json={"carousel": approved_data})
                if response.status_code == 200:
                    st.success("✅ Successfully sent to backend.")
                else:
                    st.error(f"❌ Failed: {response.status_code} {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
