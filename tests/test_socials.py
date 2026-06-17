import pytest
import os
import json
import sys
from dotenv import load_dotenv
load_dotenv()

# Add root directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# DeepEval and Guardrails/LiteLLM both need API keys
if "GOOGLE_API_KEY" not in os.environ and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models import GeminiModel
from services import generate_repurposed_content
import asyncio

# Load the dataset
def load_dataset():
    with open('evals/dataset.json', 'r') as f:
        return json.load(f)

dataset = load_dataset()

@pytest.mark.parametrize("item", dataset)
def test_social_generation(item):
    # 1. Generate content using our pipeline
    generated = asyncio.run(generate_repurposed_content(item['content']))

    # 2. Prepare the LLMTestCase
    test_case = LLMTestCase(
        input=item['content'],
        actual_output=f"Summary: {generated['summary']}\nLinkedIn: {generated['linkedin_post']}",
        retrieval_context=[item['content']]
    )

    # 3. Define metrics with Gemini as the evaluator
    # Use gemini-1.5-flash which is more likely to be available in free tier
    evaluator_model = GeminiModel(model_name="gemini-1.5-flash") 

    faithfulness_metric = FaithfulnessMetric(threshold=0.7, model=evaluator_model)
    relevancy_metric = AnswerRelevancyMetric(threshold=0.7, model=evaluator_model)

    # 4. Assert evaluations
    assert_test(test_case, [faithfulness_metric, relevancy_metric])

