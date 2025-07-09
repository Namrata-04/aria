# ARIA Research Assistant - Connected Setup

This project connects a FastAPI backend, React frontend, and MongoDB database for an AI-powered research assistant.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   MongoDB       │
│   (Port 5173)   │◄──►│   (Port 8000)   │◄──►│   (Port 27017)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

1. **Start all services:**
   ```bash
   ./start_aria.sh
   ```

2. **Check health:**
   ```bash
   ./health_check.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
aria/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── models.py           # Pydantic models
│   ├── database.py         # MongoDB connection
│   ├── mongodb_service.py  # MongoDB operations
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/aria/          # React frontend
│   ├── src/
│   │   ├── pages/         # React components
│   │   ├── components/    # UI components
│   │   ├── lib/api.ts     # API client
│   │   └── hooks/         # React hooks
│   ├── package.json       # Node.js dependencies
│   └── .env              # Frontend environment variables
├── start_aria.sh          # Startup script
├── health_check.sh        # Health check script
└── connect_all.sh         # Initial setup script
```

## 🔧 Configuration

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=aria_research
SERPAPI_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_DEV_MODE=true
```

## 🗄️ MongoDB Collections

- `research_sessions`: Stores research session data
- `search_history`: Stores search queries and results
- `saved_research`: Stores saved research sections

## 🔌 API Endpoints

### Session Management
- `POST /session` - Create or get session
- `GET /sessions` - List all sessions
- `DELETE /session/{session_id}` - Delete session

### Research
- `POST /research` - Conduct research on a topic
- `POST /chat` - Chat with ARIA

### MongoDB-specific
- `POST /mongodb/session` - MongoDB session management
- `POST /mongodb/research` - MongoDB research
- `POST /mongodb/chat` - MongoDB chat
- `GET /mongodb/search-history/{session_id}` - Get search history
- `POST /mongodb/save-research` - Save research section
- `GET /mongodb/saved-research/{session_id}` - Get saved research

## 🎯 Features

### Regular Version
- In-memory session management
- Real-time research and chat
- Basic data persistence

### MongoDB Version
- Persistent session management
- Search history tracking
- Saved research sections
- Cross-device data access
- Better scalability

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend/aria
npm run dev
```

### MongoDB Management
```bash
# Start MongoDB
brew services start mongodb/brew/mongodb-community  # macOS
sudo systemctl start mongod                        # Linux

# Connect to MongoDB shell
mongosh
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   lsof -ti:8000 | xargs kill -9  # Backend
   lsof -ti:5173 | xargs kill -9  # Frontend
   ```

2. **MongoDB not running:**
   ```bash
   brew services start mongodb/brew/mongodb-community  # macOS
   sudo systemctl start mongod                        # Linux
   ```

3. **API keys missing:**
   - Add your API keys to `backend/.env`
   - Get SERPAPI_KEY from https://serpapi.com/
   - Get OPENAI_API_KEY from https://platform.openai.com/

4. **Dependencies not installed:**
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt

   # Frontend
   cd frontend/aria
   npm install
   ```

## 📊 Monitoring

Use the health check script to monitor all services:
```bash
./health_check.sh
```

## 🚀 Production Deployment

For production deployment, consider:
- Using a production MongoDB instance
- Setting up proper CORS configuration
- Using environment-specific configurations
- Implementing proper logging and monitoring
- Setting up SSL/TLS certificates

## 📝 License

This project is for educational and research purposes.
