import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

load_dotenv()

# File-based storage paths
DATA_DIR = "data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
SEARCH_HISTORY_FILE = os.path.join(DATA_DIR, "search_history.json")
SAVED_RESEARCH_FILE = os.path.join(DATA_DIR, "saved_research.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# In-memory storage (loaded from files)
research_sessions: Dict[str, Dict[str, Any]] = {}
search_history: Dict[str, List[Dict[str, Any]]] = {}
saved_research: Dict[str, List[Dict[str, Any]]] = {}

def load_data_from_file(file_path: str, default_value: Any) -> Any:
    """Load data from JSON file, return default if file doesn't exist"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
    return default_value

def save_data_to_file(file_path: str, data: Any):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving {file_path}: {e}")

def load_all_data():
    """Load all data from files into memory"""
    global research_sessions, search_history, saved_research
    
    research_sessions = load_data_from_file(SESSIONS_FILE, {})
    search_history = load_data_from_file(SEARCH_HISTORY_FILE, {})
    saved_research = load_data_from_file(SAVED_RESEARCH_FILE, {})

def save_all_data():
    """Save all data from memory to files"""
    save_data_to_file(SESSIONS_FILE, research_sessions)
    save_data_to_file(SEARCH_HISTORY_FILE, search_history)
    save_data_to_file(SAVED_RESEARCH_FILE, saved_research)

# Load data on module import
load_all_data()

# Database utilities
async def get_database():
    return {
        "research_sessions": research_sessions,
        "search_history": search_history,
        "saved_research": saved_research
    }

async def close_database():
    """Save all data before closing"""
    save_all_data()

# Index creation for better performance (no-op for file-based)
async def create_indexes():
    pass

# Session management functions
async def create_session(session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "research_history": [],
        "conversation_history": []
    }
    research_sessions[session_id] = session
    save_data_to_file(SESSIONS_FILE, research_sessions)
    return session

async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return research_sessions.get(session_id)

async def update_session(session_id: str, updates: Dict[str, Any]):
    if session_id in research_sessions:
        research_sessions[session_id].update(updates)
        research_sessions[session_id]["updated_at"] = datetime.now().isoformat()
        save_data_to_file(SESSIONS_FILE, research_sessions)

async def delete_session(session_id: str):
    if session_id in research_sessions:
        del research_sessions[session_id]
        save_data_to_file(SESSIONS_FILE, research_sessions)
    if session_id in search_history:
        del search_history[session_id]
        save_data_to_file(SEARCH_HISTORY_FILE, search_history)
    if session_id in saved_research:
        del saved_research[session_id]
        save_data_to_file(SAVED_RESEARCH_FILE, saved_research)

async def add_search_history(session_id: str, entry: Dict[str, Any]):
    if session_id not in search_history:
        search_history[session_id] = []
    search_history[session_id].append(entry)
    save_data_to_file(SEARCH_HISTORY_FILE, search_history)

async def get_search_history(session_id: str) -> List[Dict[str, Any]]:
    return search_history.get(session_id, [])

async def save_research(session_id: str, research_data: Dict[str, Any]):
    if session_id not in saved_research:
        saved_research[session_id] = []
    saved_research[session_id].append(research_data)
    save_data_to_file(SAVED_RESEARCH_FILE, saved_research)

async def get_saved_research(session_id: str) -> List[Dict[str, Any]]:
    return saved_research.get(session_id, [])

async def delete_saved_research(session_id: str, query: str):
    if session_id in saved_research:
        saved_research[session_id] = [
            item for item in saved_research[session_id] 
            if item.get("query") != query
        ]
        save_data_to_file(SAVED_RESEARCH_FILE, saved_research) 