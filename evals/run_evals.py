import asyncio
import json
import sys
import os

# Add root directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import generate_repurposed_content
from evals.judge import evaluate_content

async def run_evals():
    # Load dataset
    with open('evals/dataset.json', 'r') as f:
        dataset = json.load(f)
    
    results = []
    print(f"🚀 Starting evaluations on {len(dataset)} examples...")
    
    for item in dataset:
        print(f"📝 Processing: {item['title']}...")
        try:
            # Generate content using the main pipeline
            generated = await generate_repurposed_content(item['content'])
            
            # Evaluate using the judge
            score = await evaluate_content(item['content'], generated)
            
            results.append({
                "id": item['id'],
                "title": item['title'],
                "scores": score.model_dump(),
                "generated": generated
            })
            print(f"✅ Faithfulness: {score.faithfulness}/5 | Engagement: {score.engagement}/5")
        except Exception as e:
            print(f"❌ Error processing {item['title']}: {e}")

    # Save results
    with open('evals/results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Print summary
    avg_faithfulness = sum(r['scores']['faithfulness'] for r in results) / len(results) if results else 0
    avg_engagement = sum(r['scores']['engagement'] for r in results) / len(results) if results else 0
    
    print("\n" + "="*30)
    print("📊 EVALUATION SUMMARY")
    print(f"Total Examples: {len(results)}")
    print(f"Avg Faithfulness: {avg_faithfulness:.2f}/5")
    print(f"Avg Engagement: {avg_engagement:.2f}/5")
    print("="*30)
    print("Full results saved to evals/results.json")

if __name__ == "__main__":
    asyncio.run(run_evals())
