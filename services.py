import os
import httpx
import trafilatura
import fitz  # PyMuPDF
from guardrails import Guard
from dotenv import load_dotenv
import logfire
import json
import base64
from schemas import SocialsOutput

load_dotenv()

# Configure Logfire (non-blocking for local dev)
logfire.configure(send_to_logfire=False) 

# Initialize Guardrails
# Guardrails uses LiteLLM, so we set the API key for Gemini
if "GEMINI_API_KEY" not in os.environ and os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Define the Guard from the Pydantic model
guard = Guard.for_pydantic(output_class=SocialsOutput)

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
    # Use the Guard to call the LLM
    # gemini-1.5-flash is often more available
    model_name = f"gemini/{os.getenv('MODEL_NAME', 'gemini-1.5-flash')}"
    
    prompt = f"""
    You are an expert social media manager. Based on the provided blog content, generate a comprehensive social media package.
    1. A concise summary of the core message.
    2. A 5-tweet Twitter thread that is engaging and uses hooks.
    3. A professional LinkedIn post that encourages discussion.
    4. An engaging Facebook post suitable for a community or personal page.
    5. An Instagram caption with relevant hashtags.
    6. A highly descriptive 'Image Prompt' for an AI image generator that captures the essence of this content visually.

    Blog Content:
    {text[:8000]}
    """

    # Run the guard
    # Note: Guardrails 0.4+ async call is .__call__(..., pydantic_ai_mode=False) 
    # but let's use the standard synchronous call wrapped in a thread if needed, 
    # or check for async support. Guardrails does have async support.
    
    result = guard(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        metadata={"text": text[:8000]}
    )
    
    # Return the validated data as a dictionary
    if result.validation_passed:
        return result.validated_output
    else:
        # If it failed and couldn't be fixed
        raise Exception(f"Validation failed: {result.error}")

