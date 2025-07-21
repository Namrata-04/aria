import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

# Storage configuration
USE_MONGODB = os.getenv("USE_MONGODB", "true").lower() == "true"

class StorageManager:
    """Hybrid storage manager that uses both MongoDB and DynamoDB (and file as fallback)"""
    
    def __init__(self):
        self.use_mongodb = USE_MONGODB
        self.mongo_service = None
        self.dynamo_service = None
        try:
            from mongodb_service import (
                connect_to_mongodb, create_session as mongo_create_session,
                get_session as mongo_get_session, update_session as mongo_update_session,
                delete_session as mongo_delete_session, add_search_history as mongo_add_search_history,
                get_search_history as mongo_get_search_history, save_research as mongo_save_research,
                get_saved_research as mongo_get_saved_research, delete_saved_research as mongo_delete_saved_research
            )
            self.mongo_service = {
                'connect': connect_to_mongodb,
                'create_session': mongo_create_session,
                'get_session': mongo_get_session,
                'update_session': mongo_update_session,
                'delete_session': mongo_delete_session,
                'add_search_history': mongo_add_search_history,
                'get_search_history': mongo_get_search_history,
                'save_research': mongo_save_research,
                'get_saved_research': mongo_get_saved_research,
                'delete_saved_research': mongo_delete_saved_research
            }
            print("🔗 Using MongoDB storage")
        except ImportError as e:
            print(f"⚠️ MongoDB not available: {e}")
            self.use_mongodb = False
        try:
            import dynamodb_service as ddb
            self.dynamo_service = ddb
            print("🔗 Using DynamoDB storage")
        except ImportError as e:
            print(f"⚠️ DynamoDB not available: {e}")
            self.dynamo_service = None
        if not self.use_mongodb and not self.dynamo_service:
            # Fallback to file storage
            from database import (
                create_session as file_create_session,
                get_session as file_get_session, update_session as file_update_session,
                delete_session as file_delete_session, add_search_history as file_add_search_history,
                get_search_history as file_get_search_history, save_research as file_save_research,
                get_saved_research as file_get_saved_research, delete_saved_research as file_delete_saved_research
            )
            self.file_service = {
                'create_session': file_create_session,
                'get_session': file_get_session,
                'update_session': file_update_session,
                'delete_session': file_delete_session,
                'add_search_history': file_add_search_history,
                'get_search_history': file_get_search_history,
                'save_research': file_save_research,
                'get_saved_research': file_get_saved_research,
                'delete_saved_research': file_delete_saved_research
            }
            print("📁 Using file storage (fallback)")

    async def initialize(self):
        """Initialize the storage system"""
        if self.mongo_service is not None:
            try:
                connected = await self.mongo_service['connect']()
                if connected is False:
                    print("⚠️ MongoDB connection failed")
                    self.use_mongodb = False
            except Exception as e:
                print(f"⚠️ MongoDB initialization failed: {e}")
                self.use_mongodb = False
        # No explicit init for DynamoDB

    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session in both DBs"""
        results = {}
        errors = []
        if self.mongo_service is not None:
            try:
                results['mongodb'] = await self.mongo_service['create_session'](session_id, user_id)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                results['dynamodb'] = await self.dynamo_service.create_session(session_id, user_id)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not results and hasattr(self, 'file_service'):
            results['file'] = await self.file_service['create_session'](session_id, user_id)
        if errors:
            print("Storage errors:", errors)
        return results

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session from both DBs"""
        results = {}
        errors = []
        if self.mongo_service is not None:
            try:
                results['mongodb'] = await self.mongo_service['get_session'](session_id)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                results['dynamodb'] = await self.dynamo_service.get_session(session_id)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not results and hasattr(self, 'file_service'):
            results['file'] = await self.file_service['get_session'](session_id)
        if errors:
            print("Storage errors:", errors)
        return results

    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        errors = []
        if self.mongo_service is not None:
            try:
                await self.mongo_service['update_session'](session_id, updates)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                await self.dynamo_service.update_session(session_id, updates)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not (self.mongo_service or self.dynamo_service) and hasattr(self, 'file_service'):
            await self.file_service['update_session'](session_id, updates)
        if errors:
            print("Storage errors:", errors)

    async def delete_session(self, session_id: str):
        errors = []
        if self.mongo_service is not None:
            try:
                await self.mongo_service['delete_session'](session_id)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                await self.dynamo_service.delete_session(session_id)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not (self.mongo_service or self.dynamo_service) and hasattr(self, 'file_service'):
            await self.file_service['delete_session'](session_id)
        if errors:
            print("Storage errors:", errors)

    async def add_search_history(self, session_id: str, entry: Dict[str, Any]):
        errors = []
        if self.mongo_service is not None:
            try:
                await self.mongo_service['add_search_history'](session_id, entry)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                await self.dynamo_service.add_search_history(session_id, entry)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not (self.mongo_service or self.dynamo_service) and hasattr(self, 'file_service'):
            await self.file_service['add_search_history'](session_id, entry)
        if errors:
            print("Storage errors:", errors)

    async def get_search_history(self, session_id: str) -> Dict[str, Any]:
        results = {}
        errors = []
        if self.mongo_service is not None:
            try:
                results['mongodb'] = await self.mongo_service['get_search_history'](session_id)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                results['dynamodb'] = await self.dynamo_service.get_search_history(session_id)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not results and hasattr(self, 'file_service'):
            results['file'] = await self.file_service['get_search_history'](session_id)
        if errors:
            print("Storage errors:", errors)
        return results

    async def save_research(self, session_id: str, research_data: Dict[str, Any]):
        errors = []
        if self.mongo_service is not None:
            try:
                await self.mongo_service['save_research'](session_id, research_data)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                await self.dynamo_service.save_research(session_id, research_data)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not (self.mongo_service or self.dynamo_service) and hasattr(self, 'file_service'):
            await self.file_service['save_research'](session_id, research_data)
        if errors:
            print("Storage errors:", errors)

    async def get_saved_research(self, session_id: str) -> Dict[str, Any]:
        results = {}
        errors = []
        if self.mongo_service is not None:
            try:
                results['mongodb'] = await self.mongo_service['get_saved_research'](session_id)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                results['dynamodb'] = await self.dynamo_service.get_saved_research(session_id)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not results and hasattr(self, 'file_service'):
            results['file'] = await self.file_service['get_saved_research'](session_id)
        if errors:
            print("Storage errors:", errors)
        return results

    async def delete_saved_research(self, session_id: str, query: str):
        errors = []
        if self.mongo_service is not None:
            try:
                await self.mongo_service['delete_saved_research'](session_id, query)
            except Exception as e:
                errors.append(f"MongoDB: {e}")
        if self.dynamo_service is not None:
            try:
                await self.dynamo_service.delete_saved_research(session_id, query)
            except Exception as e:
                errors.append(f"DynamoDB: {e}")
        if not (self.mongo_service or self.dynamo_service) and hasattr(self, 'file_service'):
            await self.file_service['delete_saved_research'](session_id, query)
        if errors:
            print("Storage errors:", errors)

    def get_storage_type(self) -> str:
        types = []
        if self.mongo_service is not None:
            types.append("MongoDB")
        if self.dynamo_service is not None:
            types.append("DynamoDB")
        if not types:
            types.append("File Storage")
        return ", ".join(types)

# Global storage manager instance
storage_manager = StorageManager() 