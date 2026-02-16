from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI(title="Radio AI")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Models
# -----------------------------
class ChatRequest(BaseModel):
    message: str


# -----------------------------
# Conversation State
# -----------------------------
state = {
    "stage": "ASK_TOPIC",
    "topic": "",
    "script": ""
}

conversation_history = []

# -----------------------------
# Prompts
# -----------------------------
RADIO_WRITER_PROMPT = """
تو نویسنده حرفه‌ای برنامه رادیویی هستی.
یک متن اجرای رادیویی کوتاه و شنیداری بنویس.
حداکثر 6 جمله.
لحن گرم و جذاب.
"""

STYLE_PROMPT = """
متن زیر را با مشخصات اجرایی جدید بازنویسی کن:

- لحن اجرا
- جنس صدا
- سبک برنامه

متن:
"""

# -----------------------------
# Health
# -----------------------------
@app.get("/")
def home():
    return {"status": "Radio AI running 🎙️"}


# -----------------------------
# Chat Logic
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    user_msg = req.message.strip()

    # ===== STAGE 1 =====
    if state["stage"] == "ASK_TOPIC":
        state["stage"] = "WRITE_SCRIPT"
        return {
            "reply": "موضوع برنامه امروز چیه؟ 🎙️"
        }

    # ===== STAGE 2 =====
    if state["stage"] == "WRITE_SCRIPT":

        state["topic"] = user_msg

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": RADIO_WRITER_PROMPT},
                {"role": "user", "content": f"موضوع برنامه: {user_msg}"}
            ]
        )

        script = response.choices[0].message.content
        state["script"] = script
        state["stage"] = "CONFIRM_SCRIPT"

        return {
            "reply": f"""این متن پیشنهادی برنامه است:

{script}

اگر تایید می‌کنی بنویس: تایید
یا بگو تغییرش بدم."""
        }

    # ===== STAGE 3 =====
    if state["stage"] == "CONFIRM_SCRIPT":

        if "تایید" in user_msg:
            state["stage"] = "ASK_STYLE"
            return {
                "reply": "عالی 👌 حالا بگو اجرا با چه لحنی باشه؟ (مثلاً: صمیمی، هیجانی، زنانه، رسمی، شبانه...)"
            }

        else:
            state["stage"] = "WRITE_SCRIPT"
            return {
                "reply": "باشه، موضوع رو دوباره بگو تا متن جدید بسازم."
            }

    # ===== STAGE 4 =====
    if state["stage"] == "ASK_STYLE":

        style = user_msg

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": STYLE_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
سبک اجرا:
{style}

{state["script"]}
"""
                }
            ]
        )

        final_script = response.choices[0].message.content

        state["stage"] = "ASK_TOPIC"  # reset flow

        return {
            "reply": f"""🎧 نسخه نهایی برنامه آماده است:

{final_script}

برای برنامه جدید فقط پیام بده."""
        }

    raise HTTPException(status_code=400, detail="Invalid state")
