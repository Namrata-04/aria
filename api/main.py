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
from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Configure OpenAI client
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

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
def generate_summary(topic: str, search_results: List[Dict]) -> str:
    """Generate a comprehensive summary using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for summary generation")
        return f"Research summary for: {topic}"
    
    try:
        print(f"🔍 Generating summary for: {topic}")
        # Prepare context from search results
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the following search results about '{topic}', provide a comprehensive summary:

Search Results:
{context}

Please provide a detailed, well-structured summary that covers the key aspects of {topic}. Include main points, important details, and relevant context."""

        response = openai_client.chat.completions.create(
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

def generate_notes(topic: str, search_results: List[Dict]) -> str:
    """Generate detailed notes using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for notes generation")
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

        response = openai_client.chat.completions.create(
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

def generate_key_insights(topic: str, search_results: List[Dict]) -> str:
    """Generate key insights using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for insights generation")
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

        response = openai_client.chat.completions.create(
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

def generate_suggestions(topic: str, search_results: List[Dict]) -> List[str]:
    """Generate research suggestions using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for suggestions generation")
        return ["Suggestion 1", "Suggestion 2"]
    
    try:
        print(f"🔍 Generating suggestions for: {topic}")
        context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}\n" for r in search_results])
        
        prompt = f"""Based on the search results about '{topic}', suggest 3-5 related research areas or questions:

Search Results:
{context}

Please suggest:
- Related topics to explore
- Questions for further investigation
- Areas that need more research
- Different angles to consider"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        suggestions = response.choices[0].message.content.split('\n')
        result = [s.strip() for s in suggestions if s.strip() and not s.startswith('-')]
        print(f"✅ Suggestions generated successfully")
        return result
    except Exception as e:
        print(f"❌ Suggestions generation error: {e}")
        return ["Suggestion 1", "Suggestion 2"]

def generate_reflecting_questions(topic: str, search_results: List[Dict]) -> List[str]:
    """Generate reflecting questions using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for questions generation")
        return ["Question 1", "Question 2"]
    
    try:
        print(f"🔍 Generating questions for: {topic}")
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

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        questions = response.choices[0].message.content.split('\n')
        result = [q.strip() for q in questions if q.strip() and not q.startswith('-')]
        print(f"✅ Questions generated successfully")
        return result
    except Exception as e:
        print(f"❌ Questions generation error: {e}")
        return ["Question 1", "Question 2"]

# Enhanced 3-Agent Report Generation System

async def agent_1_fetch_articles(topic: str, num_results: int = 20) -> List[Dict]:
    """Agent 1: Fetches comprehensive articles using multiple search strategies"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for article fetching")
        return []
    
    try:
        print(f"🔍 Agent 1: Fetching articles for: {topic}")
        
        # Multiple search strategies for comprehensive coverage
        search_queries = [
            topic,
            f"{topic} overview",
            f"{topic} analysis",
            f"{topic} research",
            f"{topic} latest developments",
            f"{topic} trends",
            f"{topic} applications",
            f"{topic} benefits",
            f"{topic} challenges"
        ]
        
        all_articles = []
        
        for query in search_queries[:5]:  # Use first 5 queries to get variety
            try:
                articles = await search_web(query, 4)  # 4 articles per query
                all_articles.extend(articles)
            except Exception as e:
                print(f"⚠️  Search failed for query '{query}': {e}")
                continue
        
        # Remove duplicates based on URL
        unique_articles = []
        seen_urls = set()
        for article in all_articles:
            if article.get('link') not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article.get('link'))
        
        print(f"✅ Agent 1: Fetched {len(unique_articles)} unique articles")
        return unique_articles[:20]  # Limit to 20 articles
        
    except Exception as e:
        print(f"❌ Agent 1 error: {e}")
        return []

async def agent_2_analyze_relevance(topic: str, articles: List[Dict]) -> Dict:
    """Agent 2: Analyzes articles and finds most relevant content"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for content analysis")
        return {"relevant_articles": [], "key_themes": [], "analysis": ""}
    
    try:
        print(f"🔍 Agent 2: Analyzing relevance for: {topic}")
        
        # Prepare article data for analysis
        articles_text = "\n\n".join([
            f"Article {i+1}:\nTitle: {article.get('title', '')}\nContent: {article.get('snippet', '')}\nURL: {article.get('link', '')}"
            for i, article in enumerate(articles)
        ])
        
        prompt = f"""You are an expert research analyst. Analyze the following articles about '{topic}' and:

1. **Identify the most relevant articles** (rank them by relevance to the search query)
2. **Extract key themes and patterns** across the articles
3. **Find conflicting or complementary information**
4. **Identify gaps in the research**

Articles to analyze:
{articles_text}

Please provide:
- Top 5 most relevant articles with relevance scores (1-10)
- Key themes and patterns found
- Important insights and findings
- Research gaps identified
- Quality assessment of the sources

Format your response as structured analysis."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        analysis = response.choices[0].message.content
        print(f"✅ Agent 2: Analysis completed")
        
        # Extract relevant articles (top 5)
        relevant_articles = articles[:5] if len(articles) >= 5 else articles
        
        return {
            "relevant_articles": relevant_articles,
            "analysis": analysis,
            "total_articles_analyzed": len(articles)
        }
        
    except Exception as e:
        print(f"❌ Agent 2 error: {e}")
        return {"relevant_articles": articles[:5], "analysis": "", "total_articles_analyzed": len(articles)}

async def agent_3_generate_structured_report(topic: str, relevant_articles: List[Dict], analysis: str) -> str:
    """Agent 3: Generates comprehensive structured report"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for report generation")
        return "No report generated."
    
    try:
        print(f"🔍 Agent 3: Generating structured report for: {topic}")
        
        # Prepare content for report generation
        articles_content = "\n\n".join([
            f"Source {i+1}:\nTitle: {article.get('title', '')}\nContent: {article.get('snippet', '')}\nAuthor: {article.get('author', 'Unknown')}\nPublished: {article.get('published', 'Unknown')}\nURL: {article.get('link', '')}"
            for i, article in enumerate(relevant_articles)
        ])
        
        prompt = f"""You are an expert research report writer. Create a comprehensive, well-structured research report about '{topic}' based on the following sources and analysis.

**Sources:**
{articles_content}

**Analysis:**
{analysis}

**Report Structure Requirements:**
1. **Abstract** (150-200 words): Executive summary of key findings
2. **Introduction** (200-300 words): Background, context, and research objectives
3. **Main Body** (800-1200 words): 
   - Literature Review
   - Key Findings and Analysis
   - Current State of Knowledge
   - Critical Analysis
4. **Recommendations** (300-400 words): Actionable insights and suggestions
5. **Conclusion** (200-300 words): Summary and future implications
6. **References**: Include proper citations with the actual URLs from the sources provided

**Writing Guidelines:**
- Use academic writing style
- Include proper citations and references with actual URLs
- Maintain logical flow and coherence
- Provide evidence-based analysis
- Use clear headings and subheadings
- Include relevant statistics and data where available
- Address potential limitations and gaps
- DO NOT include word count at the end

Format the report professionally with clear sections, bullet points where appropriate, and proper academic structure. Include a References section with numbered citations and the actual URLs from the sources."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        
        report = response.choices[0].message.content
        print(f"✅ Agent 3: Structured report generated successfully")
        return report
        
    except Exception as e:
        print(f"❌ Agent 3 error: {e}")
        return "No report generated."

async def generate_comprehensive_report(topic: str) -> str:
    """Orchestrates the 3-agent system for comprehensive report generation"""
    try:
        print(f"🚀 Starting 3-agent report generation for: {topic}")
        
        # Agent 1: Fetch comprehensive articles
        print("📊 Agent 1: Fetching articles...")
        articles = await agent_1_fetch_articles(topic, 20)
        
        if not articles:
            return "Unable to fetch articles for report generation."
        
        # Agent 2: Analyze and find relevant content
        print("🔍 Agent 2: Analyzing relevance...")
        analysis_result = await agent_2_analyze_relevance(topic, articles)
        
        # Agent 3: Generate structured report
        print("📝 Agent 3: Generating structured report...")
        report = await agent_3_generate_structured_report(
            topic, 
            analysis_result["relevant_articles"], 
            analysis_result["analysis"]
        )
        
        print(f"✅ 3-agent report generation completed successfully")
        return report
        
    except Exception as e:
        print(f"❌ 3-agent system error: {e}")
        return f"Error in report generation: {str(e)}"

async def generate_chat_response(message: str, history: List[Dict] = None, research_topic: str = None) -> str:
    """Generate a contextual chat response using OpenAI"""
    if not openai_client:
        print(f"⚠️  No OpenAI client for chat response")
        return f"Hello! I'm ARIA. You said: {message}"
    
    try:
        # Build context from chat history
        context = ""
        if history:
            context = "\n".join([f"User: {msg.get('user', '')}\nARIA: {msg.get('assistant', '')}" for msg in history[-5:]])
        
        # Create topic-specific prompt
        if research_topic:
            prompt = f"""You are ARIA, an Academic Research Intelligence Assistant. You are currently helping with research about '{research_topic}'.

**IMPORTANT**: Focus your responses specifically on topics related to '{research_topic}'. If the user asks about something unrelated to this topic, politely redirect them back to '{research_topic}' or suggest how their question might relate to '{research_topic}'.

Previous conversation:
{context}

User: {message}

Please provide a helpful, informative response that:
- Addresses the user's question directly
- Focuses specifically on '{research_topic}' and related topics
- Provides relevant information about '{research_topic}'
- If the question is unrelated to '{research_topic}', politely redirect to the topic
- Suggests further research within the '{research_topic}' domain if appropriate
- Maintains a helpful and professional tone
- Uses the research context to provide accurate, detailed answers

Example: If researching 'brain cancer' and user asks 'What are the symptoms?', provide detailed brain cancer symptoms. If they ask about 'drones', redirect to brain cancer topics."""
        else:
            prompt = f"""You are ARIA, an Academic Research Intelligence Assistant. You help users with research and provide thoughtful, informative responses.

Previous conversation:
{context}

User: {message}

Please provide a helpful, informative response that:
- Addresses the user's question directly
- Provides relevant information
- Suggests further research if appropriate
- Maintains a helpful and professional tone"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
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
    research_topic: Optional[str] = None

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
        # Extract research topic from the request or use a default
        research_topic = getattr(request, 'research_topic', None)
        
        response = await generate_chat_response(request.message, request.history, research_topic)
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
        summary = generate_summary(request.topic, search_results)
        notes = generate_notes(request.topic, search_results)
        key_insights = generate_key_insights(request.topic, search_results)
        suggestions = generate_suggestions(request.topic, search_results)
        reflecting_questions = generate_reflecting_questions(request.topic, search_results)
        report = await generate_comprehensive_report(request.topic) # Changed to use the new 3-agent system
        
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
            "reflecting_questions": reflecting_questions,
            "report": report
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
            "report": "Error generating report",
            "error": str(e)
        }

@app.get("/test-openai")
async def test_openai():
    """Test OpenAI API functionality"""
    try:
        if not openai_client:
            return {"error": "No OpenAI client available", "status": "failed"}
        
        print(f"🔍 Testing OpenAI API...")
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI test successful: {result}")
        
        return {
            "status": "success",
            "response": result,
            "client_available": bool(openai_client)
        }
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "client_available": bool(openai_client)
        }