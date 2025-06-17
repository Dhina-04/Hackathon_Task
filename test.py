import streamlit as st
import requests
import time
from PIL import Image
from io import BytesIO

# Configuration
N8N_WEBHOOK_URL = "https://dhina04.app.n8n.cloud/webhook-test/928753fa-c20f-4ebb-a0fc-2efd71a8b100"  # <-- update this
POLLING_WAIT_SECONDS = 5

# Streamlit UI
st.title("📸 Event Photo Auto-Caption & Approval")
st.write("Upload event images, auto-analyze, and generate captions.")

uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files and st.button("📤 Send to AI Caption Generator"):
    # Prepare and send images to n8n webhook
    with st.spinner("Uploading and analyzing images..."):
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        response = requests.post(N8N_WEBHOOK_URL, files=files)
        if response.status_code == 200:
            st.success("✅ Images sent successfully!")
            workflow_response = response.json()

            # Expect n8n to return:
            # {
            #   "selected": [{"filename": "image1.jpg", "caption": "A moment from the event"}, ...],
            #   "originalImages": [{...}]
            # }

            if "selected" in workflow_response and isinstance(workflow_response["selected"], list):
                selected = workflow_response["selected"]

                st.header("🖼️ Carousel Preview")
                for idx, item in enumerate(selected):
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        image_url = item.get("url")
                        if not image_url:
                            image_path = next((f for f in uploaded_files if f.name == item["filename"]), None)
                            if image_path:
                                image = Image.open(image_path)
                                st.image(image, caption=item["filename"], width=300)
                            else:
                                st.warning("Image not found.")
                        else:
                            img_data = requests.get(image_url).content
                            image = Image.open(BytesIO(img_data))
                            st.image(image, caption=item["filename"], width=300)

                    with col2:
                        st.subheader(f"Caption for {item['filename']}")
                        st.info(item["caption"])
                        col_approve, col_reject, col_regen = st.columns(3)
                        if col_approve.button(f"✅ Approve {idx}"):
                            st.success(f"{item['filename']} approved ✅")
                        if col_reject.button(f"❌ Reject {idx}"):
                            st.warning(f"{item['filename']} rejected ❌")
                        if col_regen.button(f"♻️ Regenerate {idx}"):
                            st.info(f"{item['filename']} will be regenerated 🔄")
                            # TODO: Trigger n8n caption regeneration (e.g. via another webhook)

            else:
                st.error("⚠️ Invalid response from AI workflow.")
        else:
            st.error("🚫 Failed to contact the webhook. Check URL and try again.")
