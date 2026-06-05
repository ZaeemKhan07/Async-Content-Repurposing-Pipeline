from pydantic import BaseModel
from typing import List, Optional, Dict
import datetime


class SocialsRequest(BaseModel):
    input_type: str = "text"
    content: str


class SocialsOutput(BaseModel):
    summary: str
    twitter_thread: List[str]
    linkedin_post: str
    facebook_post: str
    instagram_caption: str
    image_prompt: str
    image_url: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    status: str
    results: Optional[SocialsOutput] = None
    error: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    credential: str


class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class MyContentItem(BaseModel):
    task_id: str
    status: str
    input_type: str
    input_preview: str
    created_at: datetime.datetime
    results: Optional[SocialsOutput] = None
    error: Optional[str] = None
