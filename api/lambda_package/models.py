from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Research Session Models
class ResearchEntry(BaseModel):
    timestamp: datetime
    topic: str
    results: List[Dict[str, Any]]
    summary: str
    notes: str
    insights: str

class ConversationEntry(BaseModel):
    timestamp: datetime
    user: str
    assistant: str

class ResearchSession(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    research_history: List[ResearchEntry] = []
    conversation_history: List[ConversationEntry] = []
    current_topic: Optional[str] = None
    sources: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

# Search History Models
class SearchHistoryEntry(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    session_id: str
    query: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    num_results: int = 3

    class Config:
        allow_population_by_field_name = True

# Saved Research Models
class SavedResearchSection(BaseModel):
    section_name: str
    content: str
    saved_at: datetime = Field(default_factory=datetime.utcnow)

class SavedResearch(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    session_id: str
    query: str
    sections: Dict[str, SavedResearchSection] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

# API Request/Response Models (keeping existing ones)
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Research topic to investigate")
    num_results: Optional[int] = Field(2, ge=1, le=10, description="Number of search results to retrieve")

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for conversation continuity")
    message: str = Field(..., min_length=1, description="User message or question")
    history: Optional[list[dict]] = None

class SessionRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Optional session ID, will create new if not provided")

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

# New API Models for in-memory operations
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