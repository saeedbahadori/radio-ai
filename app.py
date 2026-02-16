from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import logging

# --------------------------------
# App Setup
# --------------------------------
app = FastAPI(title="Radio AI")

logging.basicConfig(level=logging.INFO)

# --------------------------------
# Environment Check
# --------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# --------------------------------
# Request Model
# --------------------------------
class ChatRequest(BaseModel):
    message: str


# --------------------------------
# Radio AI Personality
# --------------------------------
SYSTEM_PROMPT = """
تو یک گوینده رادیویی فارسی‌زبان به نام Radio AI هستی.

ویژگی‌ها:
- لحن گرم، صمیمی و حرفه‌ای
- حس اجرای برنامه رادیویی شبانه
- پاسخ‌ها کوتاه و شنیداری
- حداکثر 3 جمله
- کمی شاعرانه
- فارسی روان
- از توضیح فنی درباره هوش مصنوعی خودداری کن
"""

# --------------------------------
# Simple Memory (Session Memory)
# --------------------------------
conversation_history = []

MAX_HISTORY = 8


# --------------------------------
# Health Check
# --------------------------------
@app.get("/")
def home():
    return {"status": "Radio AI is alive 🎙️"}


# --------------------------------
# Chat Endpoint
# --------------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")

    try:
        # add user message
        conversation_history.append(
            {"role": "user", "content": req.message}
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history[-MAX_HISTORY:]
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.85,
            max_tokens=180,
            messages=messages,
        )

        reply_text = response.choices[0].message.content or "..."

        # store assistant reply
        conversation_history.append(
            {"role": "assistant", "content": reply_text}
        )

        logging.info("User: %s", req.message)
        logging.info("RadioAI: %s", reply_text)

        return {"reply": reply_text}

    except Exception as e:
        logging.error(str(e))

        raise HTTPException(
            status_code=500,
            detail="Radio AI encountered an internal error"
        )
