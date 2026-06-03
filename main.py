from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import schemas
import services
import models
import uuid
import os
from sqlalchemy.orm import Session

app = FastAPI(title="RepurposeAI - Social Media Generator")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
models.init_db()

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return FileResponse("index.html")

async def run_pipeline_task(task_id: str, input_type: str, content: str = None, file_bytes: bytes = None):
    db = models.SessionLocal()
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    try:
        task.status = "Processing"
        db.commit()

        # Step 1: Extract Text
        extracted_text = ""
        if input_type == "text":
            extracted_text = content
        elif input_type == "url":
            extracted_text = await services.extract_from_url(content)
        elif input_type == "pdf":
            extracted_text = await services.extract_from_pdf(file_bytes)
        
        # Step 2: Generate Content with Gemini
        results = await services.generate_repurposed_content(extracted_text)
        
        # Step 3: Generate Image (Optional)
        image_url = await services.generate_social_image(results.image_prompt)
        
        # Step 4: Save Results
        final_results = results.dict()
        final_results["image_url"] = image_url
        
        task.results = final_results
        task.status = "Completed"
        db.commit()
        
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        task.status = "Failed"
        task.error = str(e)
        db.commit()
    finally:
        db.close()

@app.post("/generate-socials")
async def generate_socials(
    background_tasks: BackgroundTasks,
    input_type: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None)
):
    task_id = str(uuid.uuid4())
    db = models.SessionLocal()
    
    # Store initial task
    new_task = models.Task(
        id=task_id,
        status="Pending",
        input_type=input_type,
        input_data=content if content else "File Upload"
    )
    db.add(new_task)
    db.commit()
    db.close()

    # Process background task
    file_bytes = None
    if input_type == "pdf" and file:
        file_bytes = await file.read()

    background_tasks.add_task(run_pipeline_task, task_id, input_type, content, file_bytes)
    
    return {"task_id": task_id}

@app.get("/status/{task_id}", response_model=schemas.TaskStatus)
async def get_status(task_id: str):
    db = models.SessionLocal()
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    db.close()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return schemas.TaskStatus(
        task_id=task.id,
        status=task.status,
        results=task.results if task.results else None,
        error=task.error
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
