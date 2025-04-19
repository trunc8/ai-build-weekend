import streamlit as st
from PIL import Image
import random

# Page settings
st.set_page_config(page_title="Compliment Me AI", layout="centered")

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
    st.image(image, caption="Your uploaded image", use_column_width=True)

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
            st.markdown(f"<div style='font-size: 24px; text-align: center; color: #4CAF50;'><em>{compliment}</em></div>", unsafe_allow_html=True)
