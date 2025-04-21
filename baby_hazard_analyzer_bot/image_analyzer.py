"""
Image analysis using Google's Gemini API.
This script takes an image and generates a creative description focusing on outfit colors.
"""

import os
from PIL import Image
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions, Part, SafetySetting
from dotenv import load_dotenv

from pydantic import BaseModel

# Helper class to represent a bounding box
class BoundingBox(BaseModel):
    """
    Represents a bounding box with its 2D coordinates and associated label.

    Attributes:
        box_2d (list[int]): A list of integers representing the 2D coordinates of the bounding box,
                            typically in the format [x_min, y_min, x_max, y_max].
        label (str): A string representing the label or class associated with the object within the bounding box.
    """

    box_2d: list[int]
    label: str

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

        config = GenerateContentConfig(
            system_instruction="""
            Return bounding boxes as an array with labels.
            Never return masks. Limit to 25 objects.
            If an object is present multiple times, give each object a unique label
            according to its distinct characteristics (colors, size, position, etc..).
            """,
            temperature=0.5,
            safety_settings=[
                SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
            ],
            response_mime_type="application/json",
            response_schema=list[BoundingBox],  # Add BoundingBox class to the response schema
        )
        
        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=[image, prompt_text],
            config=config
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