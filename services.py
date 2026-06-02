import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

async def generate_repurposed_content(text: str):
    # Step 1: Summarize
    summary_prompt = f"""
    Summarize the following blog post into key takeaways and a concise summary.
    Focus on the most important points that would be interesting for social media.
    
    Blog Post:
    {text}
    """
    
    summary_response = client.models.generate_content(
        model=model_name,
        contents=summary_prompt
    )
    summary_text = summary_response.text
    
    # Step 2: Generate Socials using the summary (Prompt Chaining)
    socials_prompt = f"""
    Based on the following summary of a blog post, generate:
    1. A 5-part Twitter thread (engaging and punchy).
    2. A professional LinkedIn post (thought-provoking and authoritative).
    
    Summary:
    {summary_text}
    """
    
    # Use the new SDK's structured output capability
    socials_response = client.models.generate_content(
        model=model_name,
        contents=socials_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "summary": {"type": "STRING"},
                    "twitter_thread": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "linkedin_post": {"type": "STRING"}
                },
                "required": ["summary", "twitter_thread", "linkedin_post"]
            }
        )
    )
    
    try:
        # The new SDK parses JSON automatically if a schema is provided
        return socials_response.parsed
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # Manual parse fallback
        content = json.loads(socials_response.text)
        return content
