# ARIA - Academic Research Intelligence Assistant

ARIA is an AI-powered research assistant that helps with scholarly analysis and research tasks. The application uses file-based persistent storage to maintain data between server restarts.

## Features

- **Research Conducting**: Search and analyze academic topics
- **Chat Interface**: Interactive conversation with ARIA about research
- **Session Management**: Persistent research sessions
- **Search History**: Track previous research queries
- **Saved Research**: Save and manage research sections
- **File-based Storage**: Persistent data storage using JSON files

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   SERPAPI_KEY=your_serpapi_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Run the backend:
   ```bash
   python main.py
   ```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/aria
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will start on `http://localhost:5173`

## API Endpoints

- `POST /session` - Create or get session
- `GET /sessions` - List all sessions
- `POST /research` - Conduct research on a topic
- `POST /chat` - Chat with ARIA
- `GET /search-history/{session_id}` - Get search history
- `POST /save-research` - Save research section
- `GET /saved-research/{session_id}` - Get saved research
- `DELETE /saved-research/{session_id}/{query}` - Delete saved research
- `DELETE /session/{session_id}` - Delete session

## Architecture

- **Backend**: FastAPI with file-based JSON storage
- **Frontend**: React with TypeScript and Tailwind CSS
- **AI**: OpenAI GPT-4 for research analysis
- **Search**: SerpAPI for web search results
- **Storage**: JSON files in `backend/data/` directory

## Data Persistence

All data is stored in JSON files in the `backend/data/` directory:
- `sessions.json` - Research sessions
- `search_history.json` - Search history
- `saved_research.json` - Saved research sections

Data persists between server restarts and is automatically loaded when the server starts.

## Usage

1. Start both backend and frontend servers
2. Navigate to the frontend application
3. Choose "Storage Version" for the persistent storage interface
4. Enter a research topic and start exploring!

The application will maintain sessions and data across server restarts using the file-based storage system.

## Recent Changes

- Implemented file-based persistent storage
- Removed MongoDB dependency
- Simplified setup process
- Data persists between server restarts
- No authentication required - simple session-based usage 