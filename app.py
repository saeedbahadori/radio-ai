from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# -----------------------------
# Conversation State
# -----------------------------
state = {
    "step": "ask_topic",
    "topic": None,
    "duration": None,
    "tone": None,
    "script": None
}

# -----------------------------
# Request Model
# -----------------------------
class ChatRequest(BaseModel):
    message: str


# -----------------------------
# AI Prompt
# -----------------------------
SYSTEM_PROMPT = """
تو یک گوینده و تهیه‌کننده حرفه‌ای رادیو به نام Radio AI هستی.

ویژگی‌ها:
- لحن گرم و رادیویی
- پاسخ کوتاه (حداکثر 3 جمله)
- طبیعی و شنیداری
- فارسی روان
- حس شاعرانه ملایم
"""


# -----------------------------
# AI Call Function
# -----------------------------
def ask_ai(user_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.85,
        max_tokens=250,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {"message": "Radio AI server is running"}


# -----------------------------
# Chat Flow
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    global state
    user_msg = req.message.strip()

    try:

        # STEP 1 — Ask topic
        if state["step"] == "ask_topic":
            state["step"] = "get_topic"
            return {"reply": "موضوع برنامه امروز چیه؟ 🎙️"}

        # STEP 2 — Save topic
        elif state["step"] == "get_topic":
            state["topic"] = user_msg
            state["step"] = "ask_duration"
            return {"reply": "مدت برنامه چند دقیقه باشه؟"}

        # STEP 3 — Save duration
        elif state["step"] == "ask_duration":
            state["duration"] = user_msg
            state["step"] = "ask_tone"
            return {"reply": "حال‌وهوای اجرا چطور باشه؟ (صمیمی، رسمی، احساسی...)"}

        # STEP 4 — Save tone
        elif state["step"] == "ask_tone":
            state["tone"] = user_msg
            state["step"] = "generate_script"

            prompt = f"""
یک متن اجرای رادیویی بنویس.

موضوع: {state['topic']}
مدت برنامه: {state['duration']}
لحن اجرا: {state['tone']}

متن شنیداری، حرفه‌ای و مناسب گویندگی باشد.
"""

            script = ask_ai(prompt)
            state["script"] = script
            state["step"] = "confirm"

            return {
                "reply": f"🎧 متن پیشنهادی:\n\n{script}\n\nاگر تایید می‌کنی بنویس: تایید"
            }

        # STEP 5 — Confirmation
        elif state["step"] == "confirm":

            if "تایید" in user_msg:
                final_script = state["script"]

                # reset
                state = {
                    "step": "ask_topic",
                    "topic": None,
                    "duration": None,
                    "tone": None,
                    "script": None
                }

                return {
                    "reply": f"🎙️ متن نهایی آماده اجرا:\n\n{final_script}"
                }

            else:
                state["step"] = "ask_tone"
                return {"reply": "چه تغییری می‌خوای در لحن یا فضا ایجاد کنیم؟"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
