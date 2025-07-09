from fastapi import FastAPI, HTTPException, Depends, Query
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

# Import models and database
from models import (
    ResearchSession, SearchHistoryEntry, SavedResearch, SavedResearchSection,
    ResearchRequest, ChatRequest, SessionRequest, ResearchResult, ResearchResponse,
    ChatResponse, SessionInfo, SearchHistoryResponse, SavedResearchResponse, SaveResearchRequest
)

# Import storage manager
from storage_manager import storage_manager

# Load environment variables
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai.api_key = OPENAI_API_KEY

# Keep in-memory sessions for backward compatibility during transition
chat_sessions: Dict[str, "ChatSession"] = {}

system_prompt = {
    "role": "system",
    "content": """You are ARIA (Academic Research Intelligence Assistant), a specialized AI designed for scholarly research and analysis.

CORE IDENTITY:
- You are a diligent academic researcher with expertise across multiple disciplines
- You prioritize accuracy, objectivity, and scholarly rigor in all outputs
- You follow strict evidence-based methodology and avoid speculation
- You maintain context from previous conversations and can answer follow-up questions

OPERATIONAL GUIDELINES:
1. EVIDENCE-BASED ANALYSIS: Only use information explicitly provided in the source material
2. TONE: Maintain formal, clear, and professional language appropriate for scholarly work
3. STRUCTURED OUTPUT: Organize information logically with clear hierarchies and connections
4. CRITICAL THINKING: Identify patterns, contradictions, and gaps in the provided content
5. CITATION AWARENESS: Acknowledge the source material while avoiding direct copying
6. CONTEXTUAL CONTINUITY: Remember previous research and discussions in the session

QUALITY STANDARDS:
- Ensure all statements are traceable to the provided content
- Use precise academic vocabulary and terminology
- Maintain objectivity and avoid personal opinions or external assumptions
- Structure responses for maximum clarity and usability
- Build upon previous research findings when relevant

RESPONSE FORMAT:
- Use clear headings and logical organization
- Employ bullet points and numbered lists for complex information
- Provide comprehensive yet concise analysis
- Include methodological transparency in your approach"""
}

class ChatSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.research_history = []
        self.conversation_history = []
        self.current_topic = None
        self.sources = []

    def add_research(self, topic: str, results: List[Dict], summary: str, notes: str, insights: str):
        research_entry = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'results': results,
            'summary': summary,
            'notes': notes,
            'insights': insights
        }
        self.research_history.append(research_entry)
        self.current_topic = topic

    def add_conversation(self, user_message: str, assistant_response: str):
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_response
        })

    def get_context_for_llm(self) -> str:
        """Prepare context from research history for LLM"""
        context = ""
        if self.research_history:
            latest_research = self.research_history[-1]
            context += f"""
CURRENT RESEARCH CONTEXT:
Topic: {latest_research['topic']}
Summary: {latest_research['summary']}
Key Insights: {latest_research['insights']}

PREVIOUS CONVERSATION:
"""
            recent_conversations = self.conversation_history[-5:]
            for conv in recent_conversations:
                context += f"User: {conv['user']}\nARIA: {conv['assistant']}\n\n"

        return context

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ARIA Research Assistant API starting up...")
    print("Initializing storage system...")
    try:
        await storage_manager.initialize()
        print(f"✅ Storage initialized: {storage_manager.get_storage_type()}")
    except Exception as e:
        print(f"Warning: Could not initialize storage: {e}")
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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_serpapi(topic: str, num_results: int = 2) -> List[Dict]:
    """Search using SerpAPI"""
    url = "https://serpapi.com/search"
    params = {
        "q": topic,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": num_results
    }
    
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")

    results = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append({
            "title": item.get("title", "No Title"),
            "link": item.get("link", "No URL"),
            "author": item.get("source", "Unknown Source"),
            "published": item.get("date", f"Accessed on {datetime.now().strftime('%Y-%m-%d')}"),
            "snippet": item.get("snippet", "")
        })
    return results

def get_article_text(url: str) -> str:
    """Scrape article text from URL"""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:5000]
    except Exception as e:
        return f"Could not retrieve article: {e}"

def generate_llm_response(messages: list[dict], temperature: float = 0.3, max_tokens: int = 600) -> str:
    """Generate response using OpenAI API"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens
        )
    
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return "No response generated."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

def generate_summary(topic: str, snippets: List[Dict]) -> str:
    """Generate academic summary from search snippets"""
    combined = " ".join([r["snippet"] for r in snippets if r["snippet"]])
    user_prompt = {
        "role": "user",
        "content": f"""
TASK: Academic Summary Synthesis

RESEARCH TOPIC: "{topic}"

OBJECTIVE:
Create a comprehensive academic summary that synthesizes information from multiple search snippets into a coherent, scholarly overview.

METHODOLOGY:
1. CONTENT INTEGRATION: Merge information from all snippets without redundancy
2. THEMATIC ORGANIZATION: Structure content around key themes and concepts
3. LOGICAL FLOW: Ensure smooth transitions between ideas
4. ACADEMIC RIGOR: Maintain scholarly standards throughout

OUTPUT SPECIFICATIONS:
- Length: Approximately 250-300 words
- Structure: 3-4 well-developed paragraphs
- Style: Formal academic prose suitable for research papers
- Focus: Synthesis rather than mere compilation

SOURCE SNIPPETS:
--- BEGIN SNIPPETS ---
{combined}
--- END SNIPPETS ---

Generate your academic summary:"""
    }
    
    return generate_llm_response([system_prompt, user_prompt], temperature=0.3, max_tokens=500)

def generate_notes(topic: str, snippets: List[Dict]) -> str:
    """Generate structured academic notes"""
    combined = " ".join([r["snippet"] for r in snippets if r["snippet"]])
    user_prompt = {
        "role": "user",
        "content": f"""
TASK: Structured Academic Note Generation

RESEARCH TOPIC: "{topic}"

PURPOSE:
Transform search snippets into comprehensive, well-organized study notes suitable for academic research.

STRUCTURAL REQUIREMENTS:
Use hierarchical organization with clear sections and bullet points.

SOURCE MATERIAL:
--- BEGIN SNIPPETS ---
{combined}
--- END SNIPPETS ---

Generate structured academic notes:"""
    }
    
    return generate_llm_response([system_prompt, user_prompt], temperature=0.2, max_tokens=350)

def generate_key_insights(topic: str, articles: List[str]) -> str:
    """Generate key insights from article texts"""
    combined = "\n\n".join(articles)
    user_prompt = {
        "role": "user",
        "content": f"""
TASK: Academic Insight Extraction and Analysis

RESEARCH TOPIC: "{topic}"

Generate 5-7 key insights with structured analysis.

SOURCE MATERIAL:
--- BEGIN ARTICLES ---
{combined}
--- END ARTICLES ---

Please proceed with your structured analysis:"""
    }
    
    return generate_llm_response([system_prompt, user_prompt], temperature=0.3, max_tokens=350)

def generate_suggestions(topic: str) -> List[str]:
    """Generate research suggestions"""
    user_prompt = {
        "role": "user",
        "content": f"""
TASK: Academic Research Question Development

PRIMARY RESEARCH TOPIC: "{topic}"

Generate three sophisticated research questions or subtopics that extend from the primary topic.

Generate three research suggestions:"""
    }
    
    suggestions_text = generate_llm_response([system_prompt, user_prompt], temperature=0.4, max_tokens=200)
    
    import re
    questions = re.findall(r'\*\*Research Question \d+:\*\*\s*(.+?)(?=\n\*\*Rationale|$)', suggestions_text, re.DOTALL)
    suggestions = [q.strip() for q in questions if q.strip()]

    if not suggestions:
        suggestions_raw = suggestions_text.split("\n")
        suggestions = [s.strip("•-0123456789. *") for s in suggestions_raw if s.strip() and not s.startswith("**")]
        suggestions = [s for s in suggestions if len(s) > 20]

    return suggestions[:3]

def generate_reflecting_questions(topic: str) -> list[str]:
    """Generate 3-4 reflecting questions for deeper understanding of the topic."""
    user_prompt = {
        "role": "user",
        "content": f'''
TASK: Reflecting Question Generation

RESEARCH TOPIC: "{topic}"

OBJECTIVE:
Generate 3-4 thought-provoking, open-ended questions that encourage deeper reflection, critical thinking, or discussion about the topic. These should not be factual questions, but rather prompts for analysis, debate, or personal connection.

OUTPUT:
- List each question on a new line, numbered or bulleted.
'''
    }
    response = generate_llm_response([system_prompt, user_prompt], temperature=0.4, max_tokens=120)
    # Extract questions as a list
    import re
    questions = re.findall(r'\d+\.\s*(.+)', response)
    if not questions:
        questions = [q.strip('-•* ') for q in response.split('\n') if q.strip()]
    return questions[:4]

def get_or_create_session(session_id: Optional[str] = None) -> ChatSession:
    """Get existing session or create new one"""
    if session_id and session_id in chat_sessions:
        return chat_sessions[session_id]
    
    new_session_id = session_id or str(uuid.uuid4())
    session = ChatSession(new_session_id)
    chat_sessions[new_session_id] = session
    return session


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ARIA - Academic Research Intelligence Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "research": "/research - Conduct comprehensive research on a topic",
            "chat": "/chat - Chat with ARIA about research",
            "session": "/session - Create or get session info",
            "sessions": "/sessions - List all active sessions"
        }
    }



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(chat_sessions)
    }

# Session management endpoints
@app.post("/session", response_model=SessionInfo)
async def create_or_get_session(request: SessionRequest):
    """Create a new session or get existing session info"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Check if session exists
    existing_session = await storage_manager.get_session(session_id)
    if existing_session:
        return SessionInfo(
            session_id=existing_session["session_id"],
            current_topic=existing_session.get("current_topic"),
            research_count=len(existing_session.get("research_history", [])),
            conversation_count=len(existing_session.get("conversation_history", [])),
            created_at=existing_session["created_at"]
        )
    
    # Create new session
    session = await storage_manager.create_session(session_id)
    return SessionInfo(
        session_id=session["session_id"],
        current_topic=session.get("current_topic"),
        research_count=0,
        conversation_count=0,
        created_at=session["created_at"]
    )

@app.get("/sessions")
async def list_sessions():
    """List all sessions"""
    from database import research_sessions
    sessions = []
    for session_id, session_data in research_sessions.items():
        sessions.append({
            "session_id": session_id,
            "current_topic": session_data.get("current_topic"),
            "research_count": len(session_data.get("research_history", [])),
            "conversation_count": len(session_data.get("conversation_history", [])),
            "created_at": session_data["created_at"]
        })
    return {"sessions": sessions, "total": len(sessions)}

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest, session_id: Optional[str] = None):
    """Conduct research and save to in-memory storage"""
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required for research")
    
    try:
        num_results = request.num_results if request.num_results is not None else 3
        results = search_serpapi(request.topic, num_results)
        if not results:
            raise HTTPException(status_code=404, detail="No search results found")
        
        summary = generate_summary(request.topic, results)
        notes = generate_notes(request.topic, results)
        key_insights = generate_key_insights(request.topic, [r["snippet"] for r in results if r["snippet"]])
        suggestions = generate_suggestions(request.topic)
        reflecting_questions = generate_reflecting_questions(request.topic)
        timestamp = datetime.now().isoformat()
        
        # Save to in-memory storage
        research_entry = {
            "timestamp": timestamp,
            "topic": request.topic,
            "results": results,
            "summary": summary,
            "notes": notes,
            "insights": key_insights,
            "sources": results  # Add sources to the saved research entry
        }
        
        session = await storage_manager.get_session(session_id)
        if session:
            if "research_history" not in session:
                session["research_history"] = []
            session["research_history"].append(research_entry)
            session["current_topic"] = request.topic
            # Also save sources to the session
            if "sources" not in session:
                session["sources"] = []
            session["sources"].extend(results)
            await storage_manager.update_session(session_id, session)
        
        # Add to search history
        await storage_manager.add_search_history(session_id, {
            "query": request.topic,
            "timestamp": timestamp,
            "num_results": num_results
        })
        
        return ResearchResponse(
            session_id=session_id,
            topic=request.topic,
            timestamp=timestamp,
            summary=summary,
            notes=notes,
            key_insights=key_insights,
            sources=[ResearchResult(**r) for r in results],
            suggestions=suggestions,
            report=None,
            reflecting_questions=reflecting_questions
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Research error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_aria(request: ChatRequest):
    """Chat with ARIA using MongoDB-backed session"""
    try:
        # Get session from storage
        session = await storage_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build messages for LLM
        messages = [
            {"role": "system", "content": "You are ARIA, a helpful research assistant. Always use the previous conversation context to answer follow-up questions, even if the user refers to 'these', 'it', or similar pronouns. Never ask the user to repeat themselves. Be academically rigorous but conversational."}
        ]

        if request.history and isinstance(request.history, list) and len(request.history) > 0:
            for msg in request.history:
                if msg.get("role") in ("user", "ai") and msg.get("content"):
                    messages.append({
                        "role": "assistant" if msg["role"] == "ai" else "user",
                        "content": msg["content"]
                    })
            if not (messages and messages[-1]["role"] == "user" and messages[-1]["content"] == request.message):
                messages.append({"role": "user", "content": request.message})
        else:
            # Use session context
            context = ""
            if session.get("research_history"):
                latest_research = session["research_history"][-1]
                context += f"""
CURRENT RESEARCH CONTEXT:
Topic: {latest_research['topic']}
Summary: {latest_research['summary']}
Key Insights: {latest_research['insights']}

PREVIOUS CONVERSATION:
"""
                recent_conversations = session.get("conversation_history", [])[-5:]
                for conv in recent_conversations:
                    context += f"User: {conv['user']}\nARIA: {conv['assistant']}\n\n"

            messages.append({
                "role": "user", 
                "content": f"\nCONTEXT FROM CURRENT SESSION:\n{context}\n\nUSER QUESTION/MESSAGE:\n{request.message}\n"
            })

        assistant_response = generate_llm_response(messages, temperature=0.4, max_tokens=600)

        # Save to storage
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": request.message,
            "assistant": assistant_response
        }

        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].append(conversation_entry)
        await storage_manager.update_session(request.session_id, session)

        return ChatResponse(
            session_id=request.session_id,
            response=assistant_response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/search-history/{session_id}")
async def get_search_history(session_id: str):
    """Get search history for a session"""
    try:
        searches = await storage_manager.get_search_history(session_id)
        return {"searches": searches, "total": len(searches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search history: {str(e)}")

@app.post("/save-research")
async def save_research_section(request: SaveResearchRequest):
    """Save a research section to in-memory storage"""
    try:
        await storage_manager.save_research(request.session_id, {
            "query": request.query,
            "section_name": request.section_name,
            "content": request.content,
            "saved_at": datetime.now().isoformat()
        })
        return {"message": f"Research section '{request.section_name}' saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving research: {str(e)}")

@app.get("/saved-research/{session_id}")
async def get_saved_research(session_id: str):
    """Get saved research for a session"""
    try:
        saved_items = await storage_manager.get_saved_research(session_id)
        return {"saved_research": saved_items, "total": len(saved_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving saved research: {str(e)}")

@app.delete("/saved-research/{session_id}/{query}")
async def delete_saved_research(session_id: str, query: str):
    """Delete saved research for a specific query"""
    try:
        await storage_manager.delete_saved_research(session_id, query)
        return {"message": f"Saved research for '{query}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting saved research: {str(e)}")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its data"""
    try:
        await storage_manager.delete_session(session_id)
        return {"message": f"Session {session_id} and all related data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@app.get("/saved-research-all")
async def get_all_saved_research():
    """Get all saved research across all sessions"""
    try:
        # Use the MongoDB service directly to fetch all documents
        from mongodb_service import database, SAVED_RESEARCH_COLLECTION
        if database is None:
            raise HTTPException(status_code=500, detail="MongoDB not connected")
        cursor = database[SAVED_RESEARCH_COLLECTION].find({}).sort("timestamp", -1)
        items = await cursor.to_list(length=None)
        for item in items:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        return {"saved_research": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving all saved research: {str(e)}")

@app.get("/search-history-all")
async def get_all_search_history():
    """Get all search history entries across all sessions"""
    try:
        from mongodb_service import database, SEARCH_HISTORY_COLLECTION
        if database is None:
            raise HTTPException(status_code=500, detail="MongoDB not connected")
        cursor = database[SEARCH_HISTORY_COLLECTION].find({}).sort("timestamp", -1)
        items = await cursor.to_list(length=None)
        for item in items:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        return {"search_history": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving all search history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)