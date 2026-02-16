from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()

# OpenAI Client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# -----------------------------
# Request Model
# -----------------------------
class ChatRequest(BaseModel):
    message: str


# -----------------------------
# Radio AI Personality
# -----------------------------
SYSTEM_PROMPT = """
تو یک گوینده رادیویی فارسی‌زبان به نام Radio AI هستی.

ویژگی‌ها:
- لحن گرم، صمیمی و حرفه‌ای
- مناسب اجرای برنامه رادیویی
- پاسخ‌ها کوتاه و شنیداری باشند
- حداکثر 3 جمله
- کمی حس شاعرانه داشته باش
- فارسی روان بنویس
- از توضیح فنی درباره هوش مصنوعی خودداری کن
"""


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {"message": "Radio AI server is running"}


# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,   # حس انسانی‌تر
            max_tokens=200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.message}
            ]
        )

        reply_text = response.choices[0].message.content

        return {
            "reply": reply_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Radio AI error: {str(e)}"
        )
