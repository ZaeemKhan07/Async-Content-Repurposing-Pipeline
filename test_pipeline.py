import requests
import time
import sys

BASE_URL = "http://localhost:8000"

SAMPLE_BLOG_POST = """
The Future of Artificial Intelligence: Why Agentic Workflows are the Next Big Thing

Artificial Intelligence has evolved rapidly over the last decade. We've moved from simple rule-based systems to massive Large Language Models (LLMs) that can write code, compose music, and even pass the bar exam. However, the current paradigm of "prompting and waiting" is reaching its limits. The next frontier isn't just bigger models; it's agentic workflows.

What are Agentic Workflows?
An agentic workflow is a system where an AI model isn't just a static responder but an active participant in a multi-step process. Instead of asking an AI to "write a whole app," you give it a goal, and it breaks that goal down into tasks: research, planning, coding, and testing. It can use tools, search the web, and even fix its own errors.

Why This Matters for Businesses
For businesses, this means moving from simple chatbots to autonomous employees. Imagine an AI that doesn't just answer customer support tickets but identifies the root cause of a bug, creates a ticket in Jira, and suggests a code fix. This level of autonomy increases efficiency by orders of magnitude.

Conclusion
As we look toward 2026, the focus will shift from 'how many parameters does your model have' to 'how capable is your agentic system.' Companies that embrace this shift early will lead the next wave of digital transformation.
"""

def test_pipeline():
    print("🚀 Starting Async Content Repurposing Pipeline Test...")
    
    # 1. Submit the blog post
    print("\n[Step 1] Submitting blog post to /generate-socials...")
    try:
        response = requests.post(
            f"{BASE_URL}/generate-socials",
            json={"blog_text": SAMPLE_BLOG_POST}
        )
        response.raise_for_status()
        data = response.json()
        task_id = data["task_id"]
        print(f"✅ Task submitted successfully! Task ID: {task_id}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure main.py is running on port 8000.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error submitting task: {e}")
        sys.exit(1)

    # 2. Poll for status
    print("\n[Step 2] Polling /status/{task_id} until completion...")
    max_attempts = 12  # 1 minute total (5s * 12)
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        data = response.json()
        status = data["status"]
        
        print(f"   - Current Status: {status} (Attempt {attempt + 1}/{max_attempts})")
        
        if status == "COMPLETED":
            print("\n🎉 TASK COMPLETED!")
            print("-" * 50)
            print("📝 SUMMARY:")
            print(data["summary"])
            print("\n🐦 TWITTER THREAD:")
            for i, tweet in enumerate(data["twitter_thread"]):
                print(f"  {i+1}. {tweet}")
            print("\n💼 LINKEDIN POST:")
            print(data["linkedin_post"])
            print("-" * 50)
            return
        
        if status == "FAILED":
            print(f"❌ Task Failed! Error: {data.get('error_message')}")
            sys.exit(1)
            
        time.sleep(5)
        attempt += 1

    print("⚠️ Test timed out after 60 seconds.")

if __name__ == "__main__":
    test_pipeline()
