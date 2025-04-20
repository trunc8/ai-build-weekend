from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import time

def setup_client():
    """Initialize and return the Gemini API client."""
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not found. Please check your .env file.")
    
    return genai.Client(api_key=api_key)

def analyze_video_from_path(video_path, prompt_text, model_name="gemini-2.0-flash"):
    """
    Analyze an video using Google's Gemini model.
    
    Args:
        video_path (str): Path to the video file
        prompt_text (str): Text prompt to send with the video
        model_name (str): Name of the Gemini model to use
        
    Returns:
        str: The generated response text
    """
    try:
        # Setup client
        client = setup_client()
        
        # Open video
        video_file = client.files.upload(file=video_path)

        # Wait until the uploaded video is available
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
                
        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=[video_file, prompt_text]
        )
        response = client.models.generate_content(
            model=f"models/{model_name}",
            contents=[
                "Summarise this video please.",
                video_file
                ],
            config=types.GenerateContentConfig(
                system_instruction=prompt_text,
                ),
            )

        # delete video
        client.files.delete(name=video_file.name)
        
        return response.text
    except FileNotFoundError:
        return f"Error: Video file '{video_path}' not found."
    except Exception as e:
        return f"Error generating content: {str(e)}"

def main():
    """Main function to run the video analysis."""
    video_path = "house_video-1.mp4"
    prompt = "You should provide a quick 2 or 3 sentence summary of what is happening in the video."
    
    result = analyze_video_from_path(video_path, prompt)
    print(result)

if __name__ == "__main__":
    main()