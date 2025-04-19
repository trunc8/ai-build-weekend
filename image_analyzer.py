"""
Image analysis using Google's Gemini API.
This script takes an image and generates a creative description focusing on outfit colors.
"""

import os
from PIL import Image
from google import genai
from dotenv import load_dotenv

def setup_client():
    """Initialize and return the Gemini API client."""
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not found. Please check your .env file.")
    
    return genai.Client(api_key=api_key)

def analyze_image(image, prompt_text, model_name="gemini-2.0-flash"):
    """
    Analyze an image using Google's Gemini model.
    
    Args:
        image (Image): Image file
        prompt_text (str): Text prompt to send with the image
        model_name (str): Name of the Gemini model to use
        
    Returns:
        str: The generated response text
    """
    try:
        # Setup client
        client = setup_client()
        
        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=[image, prompt_text]
        )
        
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def analyze_image_from_path(image_path, prompt_text, model_name="gemini-2.0-flash"):
    """
    Analyze an image using Google's Gemini model.
    
    Args:
        image_path (str): Path to the image file
        prompt_text (str): Text prompt to send with the image
        model_name (str): Name of the Gemini model to use
        
    Returns:
        str: The generated response text
    """
    try:
        # Setup client
        client = setup_client()
        
        # Open image
        image = Image.open(image_path)
        
        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=[image, prompt_text]
        )
        
        return response.text
    except FileNotFoundError:
        return f"Error: Image file '{image_path}' not found."
    except Exception as e:
        return f"Error generating content: {str(e)}"

def main():
    """Main function to run the image analysis."""
    image_path = "outfit-1.jpg"
    prompt = "Give a kind and creative compliment about the person in this photo. Make sure to specify the colors in the outfit."
    
    result = analyze_image_from_path(image_path, prompt)
    print(result)

if __name__ == "__main__":
    main()