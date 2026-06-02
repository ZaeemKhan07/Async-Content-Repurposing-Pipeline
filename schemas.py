from pydantic import BaseModel
from typing import List, Optional

class SocialsRequest(BaseModel):
    blog_text: str

class TwitterThread(BaseModel):
    tweets: List[str]

class SocialsOutput(BaseModel):
    summary: str
    twitter_thread: List[str]
    linkedin_post: str

class TaskStatus(BaseModel):
    task_id: int
    status: str
    summary: Optional[str] = None
    twitter_thread: Optional[List[str]] = None
    linkedin_post: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
