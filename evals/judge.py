import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from dotenv import load_dotenv

load_dotenv()

class EvalResult(BaseModel):
    faithfulness: int = Field(description="Score from 1 to 5 on how faithful the content is to the source")
    engagement: int = Field(description="Score from 1 to 5 on how engaging the social media posts are")
    reasoning: str = Field(description="Brief explanation for the scores")

# Use a more powerful model for judging if available, otherwise same
model_name = os.getenv("JUDGE_MODEL_NAME", "gemini-2.5-pro")
if "GOOGLE_API_KEY" not in os.environ and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

model = GeminiModel(model_name)

judge_agent = Agent(
    model,
    output_type=EvalResult,
    system_prompt=(
        "You are an expert content critic. Your job is to evaluate social media content generated from a blog post.\n"
        "Check for:\n"
        "1. Faithfulness: Does it represent the original facts correctly without hallucinating?\n"
        "2. Engagement: Are the hooks strong? Is the tone appropriate for each platform?"
    )
)

async def evaluate_content(source: str, generated: dict):
    prompt = f"""
    SOURCE BLOG:
    {source}
    
    GENERATED CONTENT:
    {generated}
    """
    result = await judge_agent.run(prompt)
    return result.output
