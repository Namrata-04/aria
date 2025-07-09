# ARIA Research Assistant - MongoDB Integration

This document explains the MongoDB integration added to the ARIA Research Assistant project.

## 🎯 What's New

The MongoDB integration adds persistent storage for:
- **Research Sessions**: Complete session data with research history and conversations
- **Search History**: All search queries with timestamps and metadata
- **Saved Research**: User-saved research sections with cross-device access

## 🏗️ Architecture

### Backend Changes

#### New Files:
- `backend/models.py` - MongoDB data models using Pydantic
- `backend/database.py` - MongoDB connection and configuration
- `backend/mongodb_service.py` - Service layer for MongoDB operations

#### Updated Files:
- `backend/main.py` - Added MongoDB endpoints alongside existing ones
- `backend/requirements.txt` - Added Motor async MongoDB driver

### Frontend Changes

#### New Files:
- `frontend/aria/src/pages/ChatMongoDB.tsx` - MongoDB-enabled chat interface

#### Updated Files:
- `frontend/aria/src/lib/api.ts` - Added MongoDB API methods
- `frontend/aria/src/App.tsx` - Added MongoDB route
- `frontend/aria/src/pages/Index.tsx` - Added MongoDB version link

## 🚀 Quick Setup

### 1. Install MongoDB

Run the setup script:
```bash
./setup_mongodb.sh
```

Or install manually:
- **macOS**: `brew install mongodb-community`
- **Linux**: Follow [MongoDB installation guide](https://docs.mongodb.com/manual/installation/)

### 2. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend/aria
npm install
```

### 3. Configure Environment

Create `backend/.env`:
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=aria_research

# API Keys
SERPAPI_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Start Services

```bash
# Start MongoDB (if not already running)
brew services start mongodb/brew/mongodb-community  # macOS
sudo systemctl start mongod  # Linux

# Start Backend
cd backend
python main.py

# Start Frontend
cd frontend/aria
npm run dev
```

## 📊 Database Schema

### Research Sessions Collection
```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: String (optional),
  research_history: [
    {
      timestamp: DateTime,
      topic: String,
      results: Array,
      summary: String,
      notes: String,
      insights: String
    }
  ],
  conversation_history: [
    {
      timestamp: DateTime,
      user: String,
      assistant: String
    }
  ],
  current_topic: String,
  sources: Array,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Search History Collection
```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: String (optional),
  query: String,
  timestamp: DateTime,
  num_results: Number
}
```

### Saved Research Collection
```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: String (optional),
  query: String,
  sections: {
    "summary": {
      section_name: String,
      content: String,
      saved_at: DateTime
    }
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

## 🔌 API Endpoints

### MongoDB Session Management
- `POST /mongodb/session` - Create or get MongoDB session
- `GET /mongodb/sessions` - List all MongoDB sessions
- `DELETE /mongodb/session/{session_id}` - Delete MongoDB session

### MongoDB Research
- `POST /mongodb/research` - Conduct research with MongoDB persistence
- `POST /mongodb/chat` - Chat with ARIA using MongoDB session

### MongoDB Search History
- `GET /mongodb/search-history/{session_id}` - Get search history

### MongoDB Saved Research
- `POST /mongodb/save-research` - Save research section
- `GET /mongodb/saved-research/{session_id}` - Get saved research
- `DELETE /mongodb/saved-research/{session_id}/{query}` - Delete saved research

## 🎨 Frontend Features

### MongoDB Version (`/chat-mongodb`)
- **Database Icon**: Visual indicator that MongoDB is enabled
- **Persistent Sessions**: Research sessions survive browser restarts
- **Search History**: Loaded from MongoDB with timestamps
- **Saved Research**: Cross-device access to saved content
- **Real-time Updates**: Immediate feedback for MongoDB operations

### Key Differences from localStorage Version:
- ✅ **Persistence**: Data survives browser restarts
- ✅ **Cross-device**: Access data from any device
- ✅ **Scalability**: Can handle multiple users
- ✅ **Backup**: Data can be backed up and restored
- ✅ **Analytics**: Can track usage patterns

## 🔧 Development

### Adding New MongoDB Features

1. **Add Model** in `backend/models.py`:
```python
class NewFeature(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    # ... other fields
```

2. **Add Service Method** in `backend/mongodb_service.py`:
```python
@staticmethod
async def new_feature_method():
    # Implementation
    pass
```

3. **Add API Endpoint** in `backend/main.py`:
```python
@app.post("/mongodb/new-feature")
async def new_feature_endpoint():
    # Implementation
    pass
```

4. **Add Frontend Method** in `frontend/aria/src/lib/api.ts`:
```typescript
async newFeature(): Promise<any> {
    return this.request('/mongodb/new-feature', {
        method: 'POST',
        // ... options
    });
}
```

### Database Operations

```python
# Insert document
result = await collection.insert_one(document.dict(by_alias=True))

# Find documents
cursor = collection.find(filter_query)
documents = []
async for doc in cursor:
    documents.append(doc)

# Update document
result = await collection.update_one(
    {"_id": object_id},
    {"$set": update_data}
)

# Delete document
result = await collection.delete_one({"session_id": session_id})
```

## 🚨 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Start MongoDB
brew services start mongodb/brew/mongodb-community  # macOS
sudo systemctl start mongod  # Linux

# Check MongoDB logs
tail -f /usr/local/var/log/mongodb/mongo.log  # macOS
tail -f /var/log/mongodb/mongod.log  # Linux
```

### Python Dependencies
```bash
# Install Motor driver
pip install motor==3.3.2

# Check installed packages
pip list | grep motor
```

### Database Indexes
The application automatically creates indexes for better performance:
- Session ID indexes for fast lookups
- Timestamp indexes for sorting
- Compound indexes for complex queries

## 📈 Performance Considerations

### Indexes
- Session lookups: `session_id` index
- Time-based queries: `timestamp` index
- User queries: `user_id` index

### Connection Pooling
- Motor handles connection pooling automatically
- Default pool size: 100 connections
- Configure via `MONGODB_URL` with parameters

### Data Size
- Research sessions: ~1-5KB per session
- Search history: ~100 bytes per search
- Saved research: ~1-10KB per saved item

## 🔒 Security

### Environment Variables
- Never commit API keys to version control
- Use `.env` file for local development
- Use environment variables in production

### Database Security
- MongoDB runs on localhost by default
- No authentication required for local development
- Add authentication for production deployment

## 🚀 Production Deployment

### MongoDB Atlas (Cloud)
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/aria_research
```

### Self-hosted MongoDB
```env
MONGODB_URL=mongodb://username:password@your-server:27017/aria_research
```

### Environment Variables
```env
# Production
MONGODB_URL=mongodb://production-server:27017
DATABASE_NAME=aria_research_prod
SERPAPI_KEY=your_production_key
OPENAI_API_KEY=your_production_key
```

## 📝 Migration from localStorage

The application maintains backward compatibility:
- Original endpoints still work with in-memory storage
- MongoDB endpoints provide persistent storage
- Users can choose which version to use
- Data migration tools can be added later

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add MongoDB functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 