import requests
import time
import sys

def test_pipeline():
    base_url = "http://127.0.0.1:8000"
    
    print("1. Testing POST /generate-socials...")
    payload = {
        "input_type": "text",
        "content": "Artificial Intelligence is transforming how we repurpose content. By using LLMs like Gemini, we can turn a single blog post into a week's worth of social media content automatically."
    }
    
    try:
        # Using data= for multipart/form-data as main.py expects Form fields
        response = requests.post(f"{base_url}/generate-socials", data=payload)
        response.raise_for_status()
        task_id = response.json().get("task_id")
        print(f"   Success! Task ID: {task_id}")
    except Exception as e:
        print(f"   Error starting task: {e}")
        return

    print("2. Polling for results...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            status_res = requests.get(f"{base_url}/status/{task_id}")
            status_res.raise_for_status()
            data = status_res.json()
            
            status = data.get("status")
            print(f"   Current Status: {status}")
            
            if status == "Completed":
                print("\n✅ PIPELINE SUCCESS!")
                results = data.get("results")
                print(f"   Summary: {results.get('summary')[:50]}...")
                print(f"   Twitter: {len(results.get('twitter_thread'))} tweets")
                print(f"   Image URL: {'Generated' if results.get('image_url') else 'Skipped'}")
                return
            elif status == "Failed":
                print(f"   ❌ Task Failed: {data.get('error')}")
                return
                
        except Exception as e:
            print(f"   Polling error: {e}")
            
        time.sleep(2)
        retry_count += 1

    print("   ❌ Polling timed out.")

if __name__ == "__main__":
    test_pipeline()
