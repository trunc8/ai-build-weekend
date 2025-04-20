import streamlit as st
import cv2
import tempfile
from PIL import Image
import numpy as np
import os
import requests
import json

# Function to send image to Gemini API and get bounding boxes
def get_bounding_boxes_from_gemini(image: Image.Image) -> list:
    """
    Sends the image to the Gemini API and retrieves bounding boxes.
    This is a placeholder function. Replace with actual API integration.
    """
    # Convert PIL image to bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image_file:
        image.save(temp_image_file.name, format='JPEG')
        temp_image_path = temp_image_file.name

    # Read the image bytes
    with open(temp_image_path, 'rb') as f:
        image_bytes = f.read()

    # Delete the temporary image file
    os.unlink(temp_image_path)

    # Placeholder for API request
    # Replace the following lines with actual API request to Gemini
    # For example:
    # response = requests.post(
    #     'https://api.gemini.com/detect',
    #     files={'image': image_bytes},
    #     headers={'Authorization': 'Bearer YOUR_API_KEY'}
    # )
    # boxes = response.json().get('boxes', [])

    # Mock response for demonstration purposes
    boxes = [
        [100, 150, 200, 250],  # [ymin, xmin, ymax, xmax]
        [300, 400, 350, 450]
    ]

    return boxes

# Set up the Streamlit page
st.set_page_config(page_title="SafeNest AI", layout="centered")
st.title("🛡️ SafeNest AI")
st.write("Upload a room video to detect potential child safety hazards.")

# Video upload
uploaded_video = st.file_uploader("Upload your room video", type=["mp4", "mov", "avi"])

if uploaded_video:
    # Create a temporary file to store the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        temp_video_file.write(uploaded_video.read())
        temp_video_path = temp_video_file.name

    # Display the uploaded video
    st.video(temp_video_path)

    # Extract frames at 1 FPS
    cap = cv2.VideoCapture(temp_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        st.error("Could not retrieve FPS from the video.")
    else:
        frame_interval = int(fps)  # 1 frame per second

        frames = []
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
            frame_count += 1
        cap.release()

        st.success(f"Extracted {len(frames)} frames at 1 FPS.")

        annotated_frames = []

        for idx, frame in enumerate(frames):
            # Get bounding boxes from Gemini API
            boxes = get_bounding_boxes_from_gemini(frame)

            # Convert PIL Image to OpenCV format
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

            # Draw bounding boxes
            for box in boxes:
                ymin, xmin, ymax, xmax = box
                cv2.rectangle(frame_cv, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # Convert back to PIL Image for Streamlit
            annotated_frame = Image.fromarray(cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB))
            annotated_frames.append(annotated_frame)

            # Display the annotated frame
            st.image(annotated_frame, caption=f"Annotated Frame {idx + 1}", use_container_width=True)

        # Define video properties
        frame_height, frame_width = annotated_frames[0].size[1], annotated_frames[0].size[0]
        output_fps = 1  # 1 frame per second

        # Create a temporary file to save the annotated video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output_video_file:
            temp_output_video_path = temp_output_video_file.name

        # Initialize VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(temp_output_video_path, fourcc, output_fps, (frame_width, frame_height))

        # Write frames to the video
        for frame in annotated_frames:
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            video_writer.write(frame_cv)

        video_writer.release()

        # Display the annotated video in Streamlit
        st.video(temp_output_video_path)

        # Optionally, delete the temporary files after use
        # os.unlink(temp_video_path)
        # os.unlink(temp_output_video_path)




