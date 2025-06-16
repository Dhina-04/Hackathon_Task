import streamlit as st
import requests
import json
from PIL import Image
from io import BytesIO

# --- Config ---
N8N_WEBHOOK_URL = "https://dhina04.app.n8n.cloud/webhook-test/928753fa-c20f-4ebb-a0fc-2efd71a8b100"  # Replace this with your actual n8n webhook URL

# --- Streamlit UI ---
st.title("Event Photo Quality Filter")
st.markdown("Upload event photos, and the best ones will be selected using brightness + sharpness scoring.")

uploaded_files = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

num_required = st.number_input("Number of top images to select", min_value=1, value=3)

if st.button("Process Images") and uploaded_files:
    with st.spinner("Uploading and processing..."):

        # Step 1: Prepare files for upload to n8n
        files_payload = [("images", (file.name, file, file.type)) for file in uploaded_files]
        data_payload = {"num_required": num_required}

        try:
            response = requests.post(N8N_WEBHOOK_URL, files=files_payload, data=data_payload)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            st.error(f"Error processing images: {e}")
            st.stop()

        # Step 2: Extract selected and original image data
        selected_filenames = [img['filename'] for img in result.get("selected", [])]
        original_images = result.get("originalImages", [])

        # Step 3: Display selected images in carousel
        st.success(f"Top {len(selected_filenames)} images selected.")
        st.subheader("🎯 Selected Image Previews")

        for image_data in original_images:
            if image_data["filename"] in selected_filenames:
                st.markdown(f"**{image_data['filename']}**")
                file_bytes = next((f.read() for f in uploaded_files if f.name == image_data["filename"]), None)
                if file_bytes:
                    st.image(file_bytes, width=300)
                st.write(f"Brightness: {image_data['brightness']} | Sharpness: {image_data['sharpness']}")
                st.markdown("---")

        # Step 4: Show Final JSON
        st.subheader("📦 Final Output JSON")
        st.json(result)

else:
    st.info("Please upload image files to begin.")
