import streamlit as st
import cv2
import tempfile
from PIL import Image
import numpy as np
import os
import requests
import json
import re
from image_analyzer import analyze_image

prompt = \
    """You are helping parents identify potential hazards in a room where young children (under 5 years old) may play.

From the uploaded image, identify only realistic and significant safety risks, such as:

- Potentially toxic substances (e.g., cleaning supplies, medications, chemicals)
- Items that could cause strangulation (e.g., cords, strings) or suffocation (e.g., plastic bags, pillows)
- Sharp edges at child height
- Exposed electrical outlets
- Open drawers or cabinets and unstable furniture
- Small choking hazards on the floor
- Bottles containing liquids on the floor
- Heavy or hot objects within child reach
- Dangerous items within reach (e.g., knives, scissors)

Output a json list where each entry contains the 2D bounding box in "box_2d" and a text label in "label"."""

def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def extract_json_from_string(text):
    # Try to extract the first JSON-like object or array
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}. TEXT: {text}")
    else:
        print("No JSON found. TEXT: {text}")
    return None

def setup_page():
    """Configure page settings and styling."""
    st.set_page_config(page_title="SafeNest AI", layout="centered")
    st.title("🛡️ SafeNest AI")
    st.write("Upload a room video to detect potential child safety hazards.")

# Function to send image to Gemini API and get bounding boxes
def get_bounding_boxes_from_gemini(image: Image.Image) -> list:
    global prompt
    """
    Sends the image to the Gemini API and retrieves bounding boxes.
    """
    try:
        with st.spinner("AI is analyzing each frame..."):
            boxes = extract_json_from_string(analyze_image(image, prompt))
            print("\n Analyzed boxes: ", boxes)
            return boxes
            # print("is_valid:", is_valid_json(boxes))
            # if not is_valid_json(boxes):
            #     return []
            # else:
            #     # boxes = json.loads(boxes)
            #     return boxes
    except Exception as e:
        st.error(f"Error generating boxes: {e}")
        return []

def main():
    """Main application function."""
    setup_page()
    # display_header()
    
    # # Add decorative container
    # with st.container():
    #     st.markdown("<div style='padding: 20px; background-color: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
    #     # Video upload
    #     uploaded_video = st.file_uploader("Upload your room video", type=["mp4", "mov", "avi"])
        
    #     # Process image if uploaded
    #     image, compliment = process_image(uploaded_file)
        
    #     # Show compliment button only if image is uploaded
    #     if image is not None:
    #         # Centered button
    #         col1, col2, col3 = st.columns([1, 2, 1])
    #         with col2:
    #             if st.button("✨ Get My Compliment"):
    #                 compliment = generate_compliment(image)
        
    #     # Display compliment if available
    #     if compliment:
    #         st.success("Here's what the AI says:")
    #         st.markdown(f"<div class='result-box'><em>{compliment}</em></div>", unsafe_allow_html=True)
            
    #         # Add option to try again
    #         col1, col2, col3 = st.columns([1, 2, 1])
    #         with col2:
    #             if st.button("Try Another Photo"):
    #                 st.session_state.compliment = None
    #                 st.rerun()
                    
    #     st.markdown("</div>", unsafe_allow_html=True)
    
    # # Footer
    # st.markdown("<div style='text-align: center; margin-top: 40px; color: #718096; font-size: 14px;'>Made with ❤️ for Google AI Hackathon</div>", unsafe_allow_html=True)

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
                    ymin, xmin, ymax, xmax = box['box_2d']
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

if __name__ == "__main__":
    main()

