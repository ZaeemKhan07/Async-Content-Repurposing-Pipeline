import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    print(f"Checking models for API Key: {api_key[:10]}...")
    
    try:
        print("\nAvailable models that support 'generateContent':")
        print("-" * 50)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"NAME: {m.name}")
                print(f"DISPLAY: {m.display_name}")
                print("-" * 50)
    except Exception as e:
        print(f"❌ Error listing models: {e}")
