import streamlit as st
import requests
from PIL import Image
import io

# 🔁 CONFIG: Replace with your actual webhook URL
N8N_WEBHOOK_URL = "https://dhina04.app.n8n.cloud/webhook-test/928753fa-c20f-4ebb-a0fc-2efd71a8b100"

st.title("📸 Event Photo Caption Generator")

# Step 1: Upload multiple image files
uploaded_files = st.file_uploader("Upload Event Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("📤 Upload and Generate Captions"):
        with st.spinner("Uploading to AI pipeline..."):
            files = []
            for i, file in enumerate(uploaded_files):
                files.append(
                    ("file", (file.name, file, file.type))
                )

            # Call the webhook with images
            try:
                response = requests.post(N8N_WEBHOOK_URL, files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Captions generated successfully!")

                    # Load and display carousel
                    if "selected" in data:
                        st.subheader("📷 Review Photos & Captions")
                        for idx, item in enumerate(data["selected"]):
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(item["url"], caption=item["filename"], use_column_width=True)
                            with col2:
                                st.markdown(f"**Caption:** {item['caption']}")
                                st.markdown(f"**Hashtags:** {item['hashtags']}")
                                action = st.radio(
                                    f"Action for Image {idx + 1}:", 
                                    ["Approve", "Reject", "Regenerate"],
                                    key=f"action_{idx}"
                                )
                                st.write(f"➡️ You selected: `{action}`")
                else:
                    st.error(f"Webhook Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")
