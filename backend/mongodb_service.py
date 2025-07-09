import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "aria_db")

SESSIONS_COLLECTION = "sessions"
SEARCH_HISTORY_COLLECTION = "search_history"
SAVED_RESEARCH_COLLECTION = "saved_research"

client: Optional[AsyncIOMotorClient] = None
database = None

async def connect_to_mongodb():
    """Connect to MongoDB"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.admin.command('ping')
        database = client[DATABASE_NAME]
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        return True
    except ConnectionFailure as e:
        print(f" Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f" MongoDB connection error: {e}")
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("🔌MongoDB connection closed")

async def create_indexes():
    """Create indexes for better performance"""
    if database is None:
        return
    
    try:
        await database[SESSIONS_COLLECTION].create_index("session_id", unique=True)
        await database[SESSIONS_COLLECTION].create_index("created_at")
        
        await database[SEARCH_HISTORY_COLLECTION].create_index("session_id")
        await database[SEARCH_HISTORY_COLLECTION].create_index("timestamp")
        
        # Create indexes for saved research collection
        await database[SAVED_RESEARCH_COLLECTION].create_index("session_id")
        await database[SAVED_RESEARCH_COLLECTION].create_index("query")
        
        print("✅ MongoDB indexes created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create indexes: {e}")

# Session management functions
async def create_session(session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new session in MongoDB"""
    if database is None:
        raise Exception("MongoDB not connected")
    
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "research_history": [],
        "conversation_history": []
    }
    
    await database[SESSIONS_COLLECTION].insert_one(session)
    return session

async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session from MongoDB"""
    if database is None:
        return None
    
    session = await database[SESSIONS_COLLECTION].find_one({"session_id": session_id})
    return session

async def update_session(session_id: str, updates: Dict[str, Any]):
    """Update session in MongoDB"""
    if database is None:
        return
    
    updates["updated_at"] = datetime.now().isoformat()
    await database[SESSIONS_COLLECTION].update_one(
        {"session_id": session_id},
        {"$set": updates}
    )

async def delete_session(session_id: str):
    """Delete session and related data from MongoDB"""
    if database is None:
        return
    
    await database[SESSIONS_COLLECTION].delete_one({"session_id": session_id})
    
    await database[SEARCH_HISTORY_COLLECTION].delete_many({"session_id": session_id})
    
    await database[SAVED_RESEARCH_COLLECTION].delete_many({"session_id": session_id})

async def add_search_history(session_id: str, entry: Dict[str, Any]):
    """Add search history entry to MongoDB"""
    if database is None:
        return
    
    entry["session_id"] = session_id
    entry["timestamp"] = datetime.now().isoformat()
    await database[SEARCH_HISTORY_COLLECTION].insert_one(entry)

async def get_search_history(session_id: str) -> List[Dict[str, Any]]:
    """Get search history for a session from MongoDB"""
    if database is None:
        return []
    
    cursor = database[SEARCH_HISTORY_COLLECTION].find(
        {"session_id": session_id}
    ).sort("timestamp", -1)
    
    return await cursor.to_list(length=None)

async def save_research(session_id: str, research_data: Dict[str, Any]):
    """Save research data to MongoDB"""
    if database is None:
        return
    
    research_data["session_id"] = session_id
    research_data["timestamp"] = datetime.now().isoformat()
    await database[SAVED_RESEARCH_COLLECTION].insert_one(research_data)

async def get_saved_research(session_id: str) -> List[Dict[str, Any]]:
    """Get saved research for a session from MongoDB"""
    if database is None:
        return []
    
    cursor = database[SAVED_RESEARCH_COLLECTION].find(
        {"session_id": session_id}
    ).sort("timestamp", -1)
    
    items = await cursor.to_list(length=None)
    # Convert ObjectId to string for each document
    for item in items:
        if "_id" in item:
            item["_id"] = str(item["_id"])
    return items

async def delete_saved_research(session_id: str, query: str):
    """Delete saved research by query from MongoDB"""
    if database is None:
        return
    
    await database[SAVED_RESEARCH_COLLECTION].delete_one({
        "session_id": session_id,
        "query": query
    })

# Migration helper functions
async def migrate_from_json_to_mongodb():
    """Migrate data from JSON files to MongoDB"""
    if database is None:
        print(" MongoDB not connected, cannot migrate")
        return
    
    print(" Starting migration from JSON to MongoDB...")
    
    from database import (
        load_data_from_file, SESSIONS_FILE, SEARCH_HISTORY_FILE, SAVED_RESEARCH_FILE
    )
    
    try:
        sessions_data = load_data_from_file(SESSIONS_FILE, {})
        if sessions_data:
            for session_id, session_data in sessions_data.items():
                await database[SESSIONS_COLLECTION].replace_one(
                    {"session_id": session_id},
                    session_data,
                    upsert=True
                )
            print(f" Migrated {len(sessions_data)} sessions")
        
        search_history_data = load_data_from_file(SEARCH_HISTORY_FILE, {})
        if search_history_data:
            for session_id, entries in search_history_data.items():
                for entry in entries:
                    entry["session_id"] = session_id
                    await database[SEARCH_HISTORY_COLLECTION].insert_one(entry)
            print(f" Migrated search history for {len(search_history_data)} sessions")
        
        saved_research_data = load_data_from_file(SAVED_RESEARCH_FILE, {})
        if saved_research_data:
            for session_id, entries in saved_research_data.items():
                for entry in entries:
                    entry["session_id"] = session_id
                    await database[SAVED_RESEARCH_COLLECTION].insert_one(entry)
            print(f" Migrated saved research for {len(saved_research_data)} sessions")
        
        print(" Migration completed successfully!")
        
    except Exception as e:
        print(f" Migration failed: {e}") 