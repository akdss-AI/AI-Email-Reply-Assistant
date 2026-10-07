from fastapi import FastAPI
import models 
from database import Base , engine 
from routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "https://ai-email-reply-assistant-frontend-5n1eua4ki-aq-6178.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

from routes.sessions import router as session_router
from routes.messages import router as message_router

app.include_router(session_router)
app.include_router(message_router)
app.include_router(auth_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "AI Email Reply Draft API is running"}
