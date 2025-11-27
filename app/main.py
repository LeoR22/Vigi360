# app/main.py
from fastapi import FastAPI
from app.routers import analytics, chatbot, crimes, geo
from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI(title="Santander Security API", version="1.0.0")

@app.get("/health")
def health():
 return {"status": "ok"}

app.add_middleware(
 CORSMiddleware,
 allow_origins=["http://localhost:5173"], 
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

app.include_router(analytics.router)
app.include_router(crimes.router)
app.include_router(geo.router)
app.include_router(chatbot.router)