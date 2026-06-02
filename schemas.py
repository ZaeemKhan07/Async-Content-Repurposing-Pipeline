from pydantic import BaseModel
from typing import List

class SocialsRequest(BaseModel):
    blog_text: str

class SocialsOutput(BaseModel):
    summary: str
    twitter_thread: List[str]
    linkedin_post: str
