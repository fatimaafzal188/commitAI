from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class DiffRequest(BaseModel):
    diff: str
    style: str = "conventional"

@app.get("/")
def root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.post("/generate")
def generate_commit(request: DiffRequest):
    style_prompts = {
        "conventional": "Write a conventional commit message (e.g. feat: add login page). Only return the commit message, nothing else.",
        "emoji": "Write a commit message with a relevant emoji at the start (e.g. ✨ add login page). Only return the commit message, nothing else.",
        "detailed": "Write a detailed multi-line commit message with a title and bullet points explaining the changes. Only return the commit message, nothing else.",
        "simple": "Write a short simple one-line commit message. Only return the commit message, nothing else."
    }

    prompt = style_prompts.get(request.style, style_prompts["conventional"])

    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Git diff:\n{request.diff}"}
        ]
    )

    message = chat.choices[0].message.content.strip()
    return {"message": message}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)