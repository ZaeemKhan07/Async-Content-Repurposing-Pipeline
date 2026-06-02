from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import schemas
import services
import uvicorn
import os

app = FastAPI(title="RepurposeAI - Social Media Generator")

# Serve Frontend
@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/generate-socials", response_model=schemas.SocialsOutput)
async def generate_socials(request: schemas.SocialsRequest):
    try:
        # Process with Gemini directly (this will block until done)
        results = await services.generate_repurposed_content(request.blog_text)
        
        # In the new services.py, results is a dict or a parsed object
        # We need to ensure it matches the SocialsOutput schema
        return schemas.SocialsOutput(
            summary=results.get("summary", ""),
            twitter_thread=results.get("twitter_thread", []),
            linkedin_post=results.get("linkedin_post", "")
        )
    except Exception as e:
        print(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
