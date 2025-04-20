import streamlit as st
from PIL import Image
import random

# Page settings
st.set_page_config(page_title="Compliment Me AI", layout="centered")

# Styling for a compliment-friendly vibe
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }

    h1, h2, h3 {
        color: #4b3f72;
        font-weight: bold;
    }

    .stButton > button {
        background-color: #f7b7a3;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 18px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        border: none;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #f1917c;
        transform: scale(1.05);
    }

    .stMarkdown {
        font-size: 18px;
    }

    .compliment-box {
        font-size: 26px;
        color: #4CAF50;
        background-color: #ffffffcc;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Optional: Inject some CSS for style
st.markdown("""
<style>
    .stApp {
        background-color: #f7f9fc;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown("<h1 style='text-align: center;'>Compliment Me AI 😄✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload your photo and get an AI-generated compliment!</p>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("**Upload your image**", type=["jpg", "jpeg", "png"])

# Show image if uploaded
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your uploaded image", use_container_width=True)

    # Centered button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Get My Compliment"):
            compliments = [
                "You look absolutely radiant!",
                "Your smile could light up a room!",
                "You have such a kind and warm aura!",
                "This photo is bursting with joy!",
                "You are stunningly unique!",
                "You exude confidence and beauty!",
                "Looking fabulous, as always!"
            ]
            compliment = random.choice(compliments)

            # Display compliment nicely
            st.success("Here's what the AI says:")
            st.markdown(f"<div class='compliment-box'><em>{compliment}</em></div>", unsafe_allow_html=True)

