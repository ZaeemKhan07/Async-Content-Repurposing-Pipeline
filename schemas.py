from pydantic import BaseModel, field_validator
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

    @field_validator('twitter_thread')
    @classmethod
    def check_tweet_lengths(cls, v: List[str]) -> List[str]:
        for i, tweet in enumerate(v):
            if len(tweet) > 280:
                raise ValueError(f"Tweet {i+1} exceeds 280 character limit (length: {len(tweet)})")
        return v

    @field_validator('summary', 'linkedin_post', 'facebook_post', 'instagram_caption', 'image_prompt')
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Content cannot be empty")
        return v


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
