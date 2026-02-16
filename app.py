from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Radio AI server is running"}


@app.post("/chat")
def chat(req: ChatRequest):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Radio AI, a smart radio assistant."},
            {"role": "user", "content": req.message}
        ]
    )

    return {
        "reply": response.choices[0].message.content
    }
