import os
import boto3
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SESSIONS_TABLE = os.getenv("DDB_SESSIONS_TABLE", "sessions")
SEARCH_HISTORY_TABLE = os.getenv("DDB_SEARCH_HISTORY_TABLE", "search_history")
SAVED_RESEARCH_TABLE = os.getenv("DDB_SAVED_RESEARCH_TABLE", "saved_research")

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
executor = ThreadPoolExecutor()

def _get_table(table_name):
    return dynamodb.Table(table_name)

# --- Sessions ---
def _create_session(session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    table = _get_table(SESSIONS_TABLE)
    item = {"session_id": session_id}
    if user_id:
        item["user_id"] = user_id
    table.put_item(Item=item)
    return item

async def create_session(session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _create_session, session_id, user_id)

def _get_session(session_id: str) -> Optional[Dict[str, Any]]:
    table = _get_table(SESSIONS_TABLE)
    resp = table.get_item(Key={"session_id": session_id})
    return resp.get("Item")

async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_session, session_id)

def _update_session(session_id: str, updates: Dict[str, Any]):
    table = _get_table(SESSIONS_TABLE)
    update_expr = "SET " + ", ".join(f"{k}=:{k}" for k in updates)
    expr_attr_vals = {f":{k}": v for k, v in updates.items()}
    table.update_item(Key={"session_id": session_id}, UpdateExpression=update_expr, ExpressionAttributeValues=expr_attr_vals)

async def update_session(session_id: str, updates: Dict[str, Any]):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _update_session, session_id, updates)

def _delete_session(session_id: str):
    table = _get_table(SESSIONS_TABLE)
    table.delete_item(Key={"session_id": session_id})

async def delete_session(session_id: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _delete_session, session_id)

# --- Search History ---
def _add_search_history(session_id: str, entry: Dict[str, Any]):
    table = _get_table(SEARCH_HISTORY_TABLE)
    item = {"session_id": session_id, **entry}
    table.put_item(Item=item)

async def add_search_history(session_id: str, entry: Dict[str, Any]):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _add_search_history, session_id, entry)

def _get_search_history(session_id: str) -> List[Dict[str, Any]]:
    table = _get_table(SEARCH_HISTORY_TABLE)
    resp = table.query(KeyConditionExpression='session_id = :sid', ExpressionAttributeValues={':sid': session_id})
    return resp.get("Items", [])

async def get_search_history(session_id: str) -> List[Dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_search_history, session_id)

# --- Saved Research ---
def _save_research(session_id: str, research_data: Dict[str, Any]):
    table = _get_table(SAVED_RESEARCH_TABLE)
    item = {"session_id": session_id, **research_data}
    table.put_item(Item=item)

async def save_research(session_id: str, research_data: Dict[str, Any]):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save_research, session_id, research_data)

def _get_saved_research(session_id: str) -> List[Dict[str, Any]]:
    table = _get_table(SAVED_RESEARCH_TABLE)
    resp = table.query(KeyConditionExpression='session_id = :sid', ExpressionAttributeValues={':sid': session_id})
    return resp.get("Items", [])

async def get_saved_research(session_id: str) -> List[Dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_saved_research, session_id)

def _delete_saved_research(session_id: str, query: str):
    table = _get_table(SAVED_RESEARCH_TABLE)
    table.delete_item(Key={"session_id": session_id, "query": query})

async def delete_saved_research(session_id: str, query: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _delete_saved_research, session_id, query) 