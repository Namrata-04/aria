from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import openai
from datetime import datetime
import json
import uuid
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import traceback
import re
from textblob import TextBlob
from mangum import Mangum

# Load environment variables
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Don't crash if environment variables are missing - just log warnings
if not SERPAPI_KEY:
    print("⚠️  Warning: SERPAPI_KEY environment variable is not set")
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY environment variable is not set")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Simple Pydantic models
class ResearchRequest(BaseModel):
    topic: str
    num_results: Optional[int] = 2

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[list[dict]] = None

class SessionRequest(BaseModel):
    session_id: Optional[str] = None

class ResearchResult(BaseModel):
    title: str
    link: str
    author: str
    published: str
    snippet: str

class ResearchResponse(BaseModel):
    session_id: str
    topic: str
    timestamp: str
    summary: str
    notes: str
    key_insights: str
    sources: List[ResearchResult]
    suggestions: List[str]
    report: Optional[str] = None
    reflecting_questions: List[str]

class ChatResponse(BaseModel):
    session_id: str
    response: str
    timestamp: str

class SessionInfo(BaseModel):
    session_id: str
    current_topic: Optional[str]
    research_count: int
    conversation_count: int
    created_at: str

class SearchHistoryResponse(BaseModel):
    searches: List[Dict[str, Any]]
    total: int

class SavedResearchResponse(BaseModel):
    saved_research: List[Dict[str, Any]]
    total: int

class SaveResearchRequest(BaseModel):
    session_id: str
    query: str
    section_name: str
    content: str

# Keep in-memory sessions for backward compatibility during transition
chat_sessions: Dict[str, "ChatSession"] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ARIA Research Assistant API starting up...")
    print("Initializing in basic mode...")
    yield
    print("ARIA Research Assistant API shutting down...")

app = FastAPI(
    title="ARIA - Academic Research Intelligence Assistant",
    description="Advanced AI-powered research assistant for scholarly analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    try:
        return {
            "message": "ARIA - Academic Research Intelligence Assistant API",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "research": "/research - Conduct comprehensive research on a topic",
                "chat": "/chat - Chat with ARIA about research",
                "session": "/session - Create or get session info",
                "sessions": "/sessions - List all active sessions"
            }
        }
    except Exception as e:
        return {
            "message": "ARIA - Academic Research Intelligence Assistant API",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "ARIA API is running",
            "env_vars": {
                "openai_set": bool(OPENAI_API_KEY),
                "serpapi_set": bool(SERPAPI_KEY)
            }
        }
    except Exception as e:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "ARIA API is running (with warnings)",
            "error": str(e)
        }

@app.post("/session")
async def create_or_get_session(request: SessionRequest):
    """Create a new session or get existing session info"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        return {
            "session_id": session_id,
            "current_topic": None,
            "research_count": 0,
            "conversation_count": 0,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
    except Exception as e:
        return {
            "session_id": str(uuid.uuid4()),
            "current_topic": None,
            "research_count": 0,
            "conversation_count": 0,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "error": str(e)
        }

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session info"""
    try:
        return {
            "session_id": session_id,
            "current_topic": None,
            "research_count": 0,
            "conversation_count": 0,
            "created_at": datetime.now().isoformat(),
            "status": "retrieved"
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "current_topic": None,
            "research_count": 0,
            "conversation_count": 0,
            "created_at": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }

@app.post("/chat")
async def chat_with_aria(request: ChatRequest):
    """Chat with ARIA"""
    try:
        response = f"Hello! I'm ARIA. You said: {request.message}"
        return {
            "session_id": request.session_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "session_id": request.session_id,
            "response": "Sorry, I'm having trouble right now.",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/research")
async def conduct_research(request: ResearchRequest, session_id: Optional[str] = None):
    """Conduct research"""
    try:
        return {
            "session_id": session_id or str(uuid.uuid4()),
            "topic": request.topic,
            "timestamp": datetime.now().isoformat(),
            "summary": f"Research summary for: {request.topic}",
            "notes": "Research notes would go here",
            "key_insights": "Key insights would go here",
            "sources": [],
            "suggestions": ["Suggestion 1", "Suggestion 2"],
            "reflecting_questions": ["Question 1", "Question 2"]
        }
    except Exception as e:
        return {
            "session_id": session_id or str(uuid.uuid4()),
            "topic": request.topic,
            "timestamp": datetime.now().isoformat(),
            "summary": "Error occurred during research",
            "notes": "",
            "key_insights": "",
            "sources": [],
            "suggestions": [],
            "reflecting_questions": [],
            "error": str(e)
        }