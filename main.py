from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Response, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import schemas
import services
import models
import auth
import uuid
import os
import traceback

app = FastAPI(title="RepurposeAI - Social Media Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

models.init_db()


@app.get("/")
def read_root():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config")
def config():
    return {"google_client_id": auth.GOOGLE_CLIENT_ID or ""}


@app.post("/auth/google")
def auth_google(payload: schemas.GoogleAuthRequest, response: Response, db: Session = Depends(models.get_db)):
    idinfo = auth.verify_google_id_token(payload.credential)
    user = auth.upsert_user(db, idinfo)
    token = auth.issue_session_jwt(user.id)
    response.set_cookie(
        key=auth.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=auth.COOKIE_SECURE,
        samesite="lax",
        max_age=auth.JWT_TTL_DAYS * 24 * 3600,
        path="/",
    )
    return schemas.UserOut(id=user.id, email=user.email, name=user.name, picture=user.picture)


@app.post("/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(key=auth.COOKIE_NAME, path="/")
    return {"status": "ok"}


@app.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(auth.get_current_user)):
    return schemas.UserOut(id=user.id, email=user.email, name=user.name, picture=user.picture)


async def run_pipeline_task(task_id: str, user_id: str, input_type: str, content: str = None, file_bytes: bytes = None):
    db = models.SessionLocal()
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    try:
        task.status = "Processing"
        db.commit()

        extracted_text = ""
        if input_type == "text":
            extracted_text = content
        elif input_type == "url":
            extracted_text = await services.extract_from_url(content)
        elif input_type == "pdf":
            extracted_text = await services.extract_from_pdf(file_bytes)

        results = await services.generate_repurposed_content(extracted_text)

        if isinstance(results, dict):
            final_results = results.copy()
        elif hasattr(results, "dict"):
            final_results = results.dict()
        else:
            final_results = dict(results)

        task.results = final_results
        task.status = "Completed"
        db.commit()

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Task {task_id} failed: {error_msg}")
        task.status = "Failed"
        task.error = error_msg
        db.commit()
    finally:
        db.close()


@app.post("/generate-socials")
async def generate_socials(
    background_tasks: BackgroundTasks,
    input_type: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None),
    user: models.User = Depends(auth.get_current_user),
):
    task_id = str(uuid.uuid4())
    db = models.SessionLocal()

    new_task = models.Task(
        id=task_id,
        user_id=user.id,
        status="Pending",
        input_type=input_type,
        input_data=content if content else "File Upload",
    )
    db.add(new_task)
    db.commit()
    db.close()

    file_bytes = None
    if input_type == "pdf" and file:
        file_bytes = await file.read()

    background_tasks.add_task(run_pipeline_task, task_id, user.id, input_type, content, file_bytes)

    return {"task_id": task_id}


@app.get("/status/{task_id}", response_model=schemas.TaskStatus)
async def get_status(task_id: str, user: models.User = Depends(auth.get_current_user), db: Session = Depends(models.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    return schemas.TaskStatus(
        task_id=task.id,
        status=task.status,
        results=task.results if task.results else None,
        error=task.error,
    )


@app.get("/my-content", response_model=List[schemas.MyContentItem])
def my_content(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(models.get_db),
    limit: int = 50,
):
    tasks = (
        db.query(models.Task)
        .filter(models.Task.user_id == user.id)
        .order_by(models.Task.created_at.desc())
        .limit(limit)
        .all()
    )

    out = []
    for t in tasks:
        preview = ""
        if t.input_data:
            preview = t.input_data[:80].replace("\n", " ")
        out.append(
            schemas.MyContentItem(
                task_id=t.id,
                status=t.status,
                input_type=t.input_type,
                input_preview=preview,
                created_at=t.created_at,
                results=t.results if t.results else None,
                error=t.error,
            )
        )
    return out


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
