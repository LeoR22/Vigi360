# app/main.py
from fastapi import FastAPI
from app.routers import crimes, analytics, chatbot

app = FastAPI(title="Santander Security API", version="0.1.0")

app.include_router(crimes.router)
app.include_router(analytics.router)
app.include_router(chatbot.router)

@app.get("/health")
def health():
    return {"status":"ok"}
