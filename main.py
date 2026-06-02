from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import models
import schemas
import services
from models import SessionLocal, init_db
import uvicorn
import os

app = FastAPI(title="Async Content Repurposing Pipeline")

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Serve Frontend
@app.get("/")
def read_root():
    return FileResponse("index.html")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def process_blog_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return

    try:
        # Update status to processing
        task.status = "PROCESSING"
        db.commit()

        # Step 1 & 2: Process with Gemini
        results = await services.generate_repurposed_content(task.original_text)
        
        # Update task with results
        task.summary = results.get("summary")
        task.twitter_thread = results.get("twitter_thread")
        task.linkedin_post = results.get("linkedin_post")
        task.status = "COMPLETED"
        db.commit()
    except Exception as e:
        task.status = "FAILED"
        task.error_message = str(e)
        db.commit()
        print(f"Task {task_id} failed: {e}")

@app.post("/generate-socials", response_model=schemas.TaskStatus)
async def generate_socials(
    request: schemas.SocialsRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    # Create a new task
    db_task = models.Task(original_text=request.blog_text, status="PENDING")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Add the processing to background tasks
    background_tasks.add_task(process_blog_task, db_task.id, db)

    return schemas.TaskStatus(task_id=db_task.id, status=db_task.status)

@app.get("/status/{task_id}", response_model=schemas.TaskStatus)
def get_status(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return schemas.TaskStatus(
        task_id=db_task.id,
        status=db_task.status,
        summary=db_task.summary,
        twitter_thread=db_task.twitter_thread,
        linkedin_post=db_task.linkedin_post,
        error_message=db_task.error_message
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
