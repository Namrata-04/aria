import os
import uuid
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Configure OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Don't crash if environment variables are missing - just log warnings
if not SERPAPI_KEY:
    print("⚠️  Warning: SERPAPI_KEY environment variable is not set")
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY environment variable is not set")

# Web search function
async def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """Search the web using SerpAPI"""
    if not SERPAPI_KEY:
        return []
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results,
            "engine": "google"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = []
        if "organic_results" in data:
            for result in data["organic_results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "author": result.get("author", "Unknown"),
                    "published": result.get("date", "Unknown")
                })
        
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

# AI analysis functions
async def generate_summary(topic: str, search_results: List[Dict]) -> str:
    """Generate a comprehensive summary using OpenAI"""
    if not OPENAI_API_KEY:
        print(f"⚠️  No OpenAI API key for summary generation")
        return f"Research summary for: {topic}"
    
    try:
        print(f"🔍 Generating summary for: {topic}")
        # Prepare context from search results
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the following search results about '{topic}', provide a comprehensive summary:

Search Results:
{context}

Please provide a detailed, well-structured summary that covers the key aspects of {topic}. Include main points, important details, and relevant context."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        print(f"✅ Summary generated successfully")
        return result
    except Exception as e:
        print(f"❌ Summary generation error: {e}")
        return f"Research summary for: {topic}"

async def generate_notes(topic: str, search_results: List[Dict]) -> str:
    """Generate detailed notes using OpenAI"""
    if not OPENAI_API_KEY:
        print(f"⚠️  No OpenAI API key for notes generation")
        return "Research notes would go here"
    
    try:
        print(f"🔍 Generating notes for: {topic}")
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the search results about '{topic}', create detailed research notes:

Search Results:
{context}

Please create comprehensive notes that include:
- Key facts and figures
- Important dates and events
- Relevant statistics
- Notable quotes or statements
- Background context"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        result = response.choices[0].message.content
        print(f"✅ Notes generated successfully")
        return result
    except Exception as e:
        print(f"❌ Notes generation error: {e}")
        return "Research notes would go here"

async def generate_key_insights(topic: str, search_results: List[Dict]) -> str:
    """Generate key insights using OpenAI"""
    if not OPENAI_API_KEY:
        print(f"⚠️  No OpenAI API key for insights generation")
        return "Key insights would go here"
    
    try:
        print(f"🔍 Generating insights for: {topic}")
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the search results about '{topic}', identify the most important insights:

Search Results:
{context}

Please provide 3-5 key insights that are:
- Most significant findings
- Surprising or unexpected information
- Implications for understanding the topic
- Trends or patterns identified"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        result = response.choices[0].message.content
        print(f"✅ Insights generated successfully")
        return result
    except Exception as e:
        print(f"❌ Insights generation error: {e}")
        return "Key insights would go here"

async def generate_suggestions(topic: str, search_results: List[Dict]) -> List[str]:
    """Generate research suggestions using OpenAI"""
    if not OPENAI_API_KEY:
        return ["Suggestion 1", "Suggestion 2"]
    
    try:
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the search results about '{topic}', suggest 3-5 related research areas or questions:

Search Results:
{context}

Please suggest:
- Related topics to explore
- Questions for further investigation
- Areas that need more research
- Different angles to consider"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        suggestions = response.choices[0].message.content.split('\n')
        return [s.strip() for s in suggestions if s.strip() and not s.startswith('-')]
    except Exception as e:
        print(f"Suggestions generation error: {e}")
        return ["Suggestion 1", "Suggestion 2"]

async def generate_reflecting_questions(topic: str, search_results: List[Dict]) -> List[str]:
    """Generate reflecting questions using OpenAI"""
    if not OPENAI_API_KEY:
        return ["Question 1", "Question 2"]
    
    try:
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the search results about '{topic}', generate 3-5 thoughtful reflecting questions:

Search Results:
{context}

Please create questions that:
- Encourage deeper thinking
- Challenge assumptions
- Explore implications
- Consider different perspectives
- Connect to broader themes"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        questions = response.choices[0].message.content.split('\n')
        return [q.strip() for q in questions if q.strip() and not q.startswith('-')]
    except Exception as e:
        print(f"Questions generation error: {e}")
        return ["Question 1", "Question 2"]

async def generate_chat_response(message: str, history: List[Dict] = None) -> str:
    """Generate a contextual chat response using OpenAI"""
    if not OPENAI_API_KEY:
        return f"Hello! I'm ARIA. You said: {message}"
    
    try:
        # Build context from chat history
        context = ""
        if history:
            context = "\n".join([f"User: {msg.get('user', '')}\nARIA: {msg.get('assistant', '')}" for msg in history[-5:]])
        
        prompt = f"""You are ARIA, an Academic Research Intelligence Assistant. You help users with research and provide thoughtful, informative responses.

Previous conversation:
{context}

User: {message}

Please provide a helpful, informative response that:
- Addresses the user's question directly
- Provides relevant information
- Suggests further research if appropriate
- Maintains a helpful and professional tone"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Chat response generation error: {e}")
        return f"Hello! I'm ARIA. You said: {message}"

# Pydantic models
class ResearchRequest(BaseModel):
    topic: str
    num_results: Optional[int] = 5

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ARIA Research Assistant API starting up...")
    print("Initializing with full research capabilities...")
    print("🔍 Web search and AI analysis enabled")
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
        response = await generate_chat_response(request.message, request.history)
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
    """Conduct comprehensive research"""
    try:
        # Perform web search
        search_results = await search_web(request.topic, request.num_results)
        
        # Generate AI analysis
        summary = await generate_summary(request.topic, search_results)
        notes = await generate_notes(request.topic, search_results)
        key_insights = await generate_key_insights(request.topic, search_results)
        suggestions = await generate_suggestions(request.topic, search_results)
        reflecting_questions = await generate_reflecting_questions(request.topic, search_results)
        
        # Convert search results to ResearchResult objects
        sources = []
        for result in search_results:
            sources.append(ResearchResult(
                title=result.get("title", ""),
                link=result.get("link", ""),
                author=result.get("author", "Unknown"),
                published=result.get("published", "Unknown"),
                snippet=result.get("snippet", "")
            ))
        
        return {
            "session_id": session_id or str(uuid.uuid4()),
            "topic": request.topic,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "notes": notes,
            "key_insights": key_insights,
            "sources": sources,
            "suggestions": suggestions,
            "reflecting_questions": reflecting_questions
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