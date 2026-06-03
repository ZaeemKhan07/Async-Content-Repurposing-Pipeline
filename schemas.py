from pydantic import BaseModel
from typing import List, Optional, Dict

class SocialsRequest(BaseModel):
    input_type: str = "text" # text, url, file
    content: str # Raw text or URL
    # For files, we will handle them as multipart/form-data in main.py

class SocialsOutput(BaseModel):
    summary: str
    twitter_thread: List[str]
    linkedin_post: str
    instagram_caption: str
    image_prompt: str
    image_url: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    results: Optional[SocialsOutput] = None
    error: Optional[str] = None
