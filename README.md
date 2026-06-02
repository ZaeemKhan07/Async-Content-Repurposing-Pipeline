# 🚀 RepurposeAI: Async Content Repurposing Pipeline

RepurposeAI is a powerful backend API and web interface that transforms massive blog posts (up to 3,000+ words) into engaging social media content. Using **Gemini 2.5 Flash-Lite** and **FastAPI**, it asynchronously summarizes your content and generates a 5-part Twitter thread and a professional LinkedIn post.

## ✨ Features
- **Async Processing**: Immediately returns a `task_id` so the user doesn't wait for LLM generation.
- **Prompt Chaining**: Uses a multi-step workflow (Summarization -> Social Generation) for better context.
- **Gemini 2.5 Flash-Lite**: Leverages the latest, most efficient model from Google.
- **Live UI**: A clean web interface to submit posts and track status in real-time.
- **Vercel Ready**: Optimized for serverless deployment.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **LLM**: Gemini 2.5 Flash-Lite (via `google-genai` SDK)
- **Database**: SQLite (SQLAlchemy)
- **Frontend**: Vanilla HTML/JS + CSS
- **Task Management**: FastAPI BackgroundTasks

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### 2. Installation
```bash
git clone https://github.com/yourusername/async-content-repurposing-pipeline.git
cd async-content-repurposing-pipeline
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.5-flash-lite
```

### 4. Running Locally
```bash
python main.py
```
Visit `http://localhost:8000` in your browser.

## ☁️ Deployment (Vercel)
1. Push your code to GitHub.
2. Connect your repository to [Vercel](https://vercel.com).
3. **Crucial**: Add `GEMINI_API_KEY` to your Vercel Environment Variables.
4. Deployment will be automatic. 

*Note: On Vercel, the app uses an in-memory database, so task history is cleared whenever the server sleeps.*

## 🛣️ API Endpoints
- `POST /generate-socials`: Submit a blog post.
- `GET /status/{task_id}`: Check generation status and retrieve results.
- `GET /`: Access the web UI.

## 📄 License
MIT
