# Implementation Plan: Guardrails AI & DeepEval Integration

This plan details the steps to integrate **Guardrails AI** for runtime validation and **DeepEval** for systematic evaluations.

## 1. Objective
Enhance the reliability and safety of the RepurposeAI pipeline by:
- Using **Guardrails AI** to enforce platform constraints (Twitter lengths) and safety (profanity, competition) with automatic re-asking.
- Using **DeepEval** to provide standardized, metric-based evaluations of model performance.

## 2. Phase 1: Dependencies & Setup
1.  Update `requirements.txt` to include:
    - `guardrails-ai`
    - `deepeval`
    - `litellm`
2.  Install dependencies.
3.  Initialize Guardrails and download necessary validators from the Hub.

## 3. Phase 2: Refactoring services.py (Guardrails AI)
1.  **Define Guard:** Create a `guardrails.Guard` from the existing `SocialsOutput` schema.
2.  **Add Hub Validators:** 
    - `twitter_length_check` (Custom or Hub)
    - `profanity_free`
3.  **Update Generation Logic:** 
    - Use `guard.call` with `model="gemini/gemini-2.5-flash-lite"`.
    - Configure `on_fail="reask"` for automated correction of long tweets.

## 4. Phase 3: Evaluation Suite (DeepEval)
1.  **Create Test File:** `tests/test_socials.py`.
2.  **Configure Judge:** Set up `deepeval.models.GeminiModel` as the evaluator.
3.  **Define Metrics:**
    - `FaithfulnessMetric`: Measures how well the output reflects the blog.
    - `AnswerRelevancyMetric`: Measures if the social posts are relevant to the input.
4.  **Run Evals:** Use `deepeval test run` to execute and view results.

## 5. Verification
- **Runtime Check:** Verify that long tweets are automatically fixed by Guardrails.
- **Eval Check:** Ensure DeepEval produces a standardized score report.
