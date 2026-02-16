from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Radio AI server is running"}