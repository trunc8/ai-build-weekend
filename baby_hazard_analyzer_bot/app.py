import streamlit as st
import cv2
import tempfile
from PIL import Image
from PIL import ImageOps
import numpy as np
import os
import requests
import json
import re
from image_analyzer import analyze_image
from stqdm import stqdm

prompt = \
"""You are helping parents identify potential hazards in a room where young children (under 5 years old) may play.

From the uploaded image, identify only realistic and significant safety risks, such as:

- Items that could cause strangulation (e.g., cords, strings) or suffocation (e.g., plastic bags, pillows)
- Sharp edges at child height
- Exposed electrical outlets
- Open drawers or cabinets and unstable furniture
- Small choking hazards on the floor
- Bottles containing liquids on the floor
- Heavy or hot objects within child reach
- Dangerous items within reach (e.g., knives, scissors)

Output a json list where each entry contains the 2D bounding box as [ymin, xmin, ymax, xmax] in "box_2d" and a text label in "label"."""

def extract_json_from_string(text):
    # Try to extract the first JSON-like object or array
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}. TEXT: {text}")
    else:
        print(f"No JSON found. TEXT: {text}")
    return []

def setup_page():
    """Configure page settings and styling."""
    st.set_page_config(page_title="SafeNest AI", layout="centered")
    st.title("🛡️ SafeNest AI")
    st.write("Upload a room video to detect potential child safety hazards.")

# Function to send image to Gemini API and get bounding boxes
def get_bounding_boxes_from_gemini(image: Image.Image) -> list:
    global prompt
    # """
    # Sends the image to the Gemini API and retrieves bounding boxes.
    # """
    try:
        response = analyze_image(image, prompt)
        print(response)
        boxes = extract_json_from_string(response)
        print("\n Analyzed boxes: ", boxes)
        return boxes
    except Exception as e:
        st.error(f"Error generating boxes: {e}")
        return []

def main():
    """Main application function."""
    setup_page()

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

            for idx in stqdm(range(len(frames))):
                frame = frames[idx]
                # Get bounding boxes from Gemini API
                boxes = get_bounding_boxes_from_gemini(frame)

                # Convert PIL Image to OpenCV format
                frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                # Rotate by 90 degrees clockwise
                frame_cv = cv2.rotate(frame_cv, cv2.ROTATE_90_CLOCKWISE)

                # Draw bounding boxes
                for box in boxes:
                    if 'box_2d' in box and len(box['box_2d']) == 4:
                        ymin, xmin, ymax, xmax = box['box_2d']
                        cv2.rectangle(frame_cv, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        
                        label = box['label']
                        # Set font and scale
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.6
                        font_thickness = 2
                        text_size, _ = cv2.getTextSize(label, font, font_scale, font_thickness)

                        # Position for the label
                        label_origin = (xmin, ymin - 10)

                        cv2.putText(frame_cv, label, label_origin, font, font_scale, (0, 0, 0), font_thickness)

                # Convert back to PIL Image for Streamlit
                annotated_frame = Image.fromarray(cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB))
                annotated_frame = ImageOps.exif_transpose(annotated_frame)
                annotated_frames.append(annotated_frame)

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

            os.system(f"ffmpeg -i {temp_output_video_path} -vcodec libx264 {temp_output_video_path}_out.mp4") 

            # Display the annotated video in Streamlit
            st.video(f"{temp_output_video_path}_out.mp4")

            # Optionally, delete the temporary files after use
            # os.unlink(temp_video_path)
            # os.unlink(temp_output_video_path)

if __name__ == "__main__":
    main()

