import streamlit as st
from PIL import Image
import os
import zipfile
import shutil
from io import BytesIO

# Function to resize, convert, and store images
def resize_and_convert_images(uploaded_files, output_size, convert_format):
    resized_folder = "resized_images"
    if os.path.exists(resized_folder):
        shutil.rmtree(resized_folder)
    os.makedirs(resized_folder, exist_ok=True)

    previews = []

    for uploaded_file in uploaded_files:
        try:
            image = Image.open(uploaded_file).convert("RGB")  # Convert to RGB to avoid errors in saving
            resized = image.resize(output_size, Image.Resampling.LANCZOS)  # Updated resampling method

            new_filename = os.path.splitext(uploaded_file.name)[0] + f".{convert_format.lower()}"
            output_path = os.path.join(resized_folder, new_filename)
            resized.save(output_path, format=convert_format.upper())
            previews.append((uploaded_file.name, image, resized))
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
    return resized_folder, previews

# Function to zip a folder
def zip_folder(folder_path):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer

# --- Streamlit App UI ---
st.title("🖼️ Image Resizer with Format Conversion")
st.markdown("Upload images, resize them, preview the result, convert to JPG/PNG, and download as ZIP.")

uploaded_files = st.file_uploader("Upload image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

col1, col2 = st.columns(2)
with col1:
    width = st.slider("Output Width (px)", 32, 1024, 128, 8)
with col2:
    height = st.slider("Output Height (px)", 32, 1024, 128, 8)

convert_format = st.selectbox("Convert Images To", ["JPG", "PNG"])

if uploaded_files:
    if st.button("Resize, Convert & Preview"):
        with st.spinner("Processing..."):
            resized_folder, previews = resize_and_convert_images(
                uploaded_files, (width, height), convert_format
            )
            zip_file = zip_folder(resized_folder)

        st.success("✅ Images processed successfully!")
        st.markdown("### Preview of Resized & Converted Images:")

        for name, original, resized in previews:
            st.markdown(f"**{name}**")
            col1, col2 = st.columns(2)
            with col1:
                st.image(original, caption="Original", use_column_width=True)
            with col2:
                st.image(resized, caption=f"Resized to {width}x{height} ({convert_format})", use_column_width=True)

        st.download_button(
            label="📦 Download Resized Images as ZIP",
            data=zip_file,
            file_name=f"converted_images_{width}x{height}.{convert_format.lower()}.zip",
            mime="application/zip"
        )
