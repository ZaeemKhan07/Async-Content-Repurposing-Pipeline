import os
import httpx
import trafilatura
import fitz  # PyMuPDF
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import base64

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

async def extract_from_url(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception("Failed to download content from URL")
    text = trafilatura.extract(downloaded)
    if not text:
        raise Exception("Failed to extract text from URL content")
    return text

async def extract_from_pdf(file_content: bytes) -> str:
    doc = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

async def generate_repurposed_content(text: str):
    # Prompt for multi-platform content
    prompt = f"""
    You are an expert social media manager. Based on the following blog content, generate a comprehensive social media package.
    
    1. A concise summary of the core message.
    2. A 5-tweet Twitter thread that is engaging and uses hooks.
    3. A professional LinkedIn post that encourages discussion.
    4. An Instagram caption with relevant hashtags.
    5. A highly descriptive 'Image Prompt' for an AI image generator that captures the essence of this content visually.
    
    Blog Content:
    {text[:8000]} # Truncate to avoid context limits if necessary
    """
    
    # Use structured output
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
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
                    "linkedin_post": {"type": "STRING"},
                    "instagram_caption": {"type": "STRING"},
                    "image_prompt": {"type": "STRING"}
                },
                "required": ["summary", "twitter_thread", "linkedin_post", "instagram_caption", "image_prompt"]
            }
        )
    )
    
    # Explicitly return a dict to avoid attribute errors in main.py
    if hasattr(response, "parsed"):
        # If it's a Pydantic model (SDK behavior), convert to dict
        if hasattr(response.parsed, "model_dump"):
            return response.parsed.model_dump()
        elif hasattr(response.parsed, "dict"):
            return response.parsed.dict()
        return response.parsed
    
    # Fallback to manual parsing if necessary
    return json.loads(response.text)

