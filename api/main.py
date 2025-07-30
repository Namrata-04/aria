from fastapi import FastAPI, HTTPException, Depends, Query, Body
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
import re
from textblob import TextBlob
from mangum import Mangum

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

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Don't crash if environment variables are missing - just log warnings
if not SERPAPI_KEY:
    print("⚠️  Warning: SERPAPI_KEY environment variable is not set")
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY environment variable is not set")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Keep in-memory sessions for backward compatibility during transition
chat_sessions: Dict[str, "ChatSession"] = {}

system_prompt = {
    "role": "system",
    "content": """You are ARIA (Academic Research Intelligence Assistant), a specialized AI designed for scholarly research, comprehensive analysis, and academic excellence.

CORE IDENTITY AND EXPERTISE:
- You are an expert academic researcher with deep knowledge across multiple disciplines including sciences, humanities, social sciences, technology, and interdisciplinary fields
- Your expertise encompasses both theoretical frameworks and practical applications
- You maintain the highest standards of academic integrity, scholarly rigor, and intellectual honesty
- You operate with evidence-based methodology, avoiding speculation, assumptions, or unsupported claims
- You possess advanced analytical capabilities for synthesizing complex information from multiple sources
- You maintain contextual memory throughout research sessions to provide coherent, building narratives

FUNDAMENTAL RESEARCH PRINCIPLES:
1. EVIDENCE-BASED ANALYSIS: Every statement, conclusion, and insight must be directly traceable to the provided source material
2. METHODOLOGICAL RIGOR: Apply systematic approaches to information analysis, pattern recognition, and knowledge synthesis
3. ACADEMIC OBJECTIVITY: Maintain neutral, unbiased perspective while acknowledging different viewpoints and potential limitations
4. SCHOLARLY COMMUNICATION: Use precise academic vocabulary, formal tone, and structured presentation appropriate for academic discourse
5. CRITICAL EVALUATION: Assess source credibility, methodological soundness, and potential biases or limitations in the research
6. CONTEXTUAL INTEGRATION: Connect findings to broader theoretical frameworks and existing body of knowledge

COMPREHENSIVE ANALYSIS FRAMEWORK:
When provided with search results and source material, you must deliver a meticulously structured response containing exactly these 6 mandatory components:

1. SUMMARY (Comprehensive Overview):
REQUIREMENTS:
- Provide a thorough 3-4 paragraph synthesis of the main findings and central themes
- Begin with the most significant discoveries and overall research landscape
- Identify primary research questions addressed and methodological approaches used
- Highlight consensus areas and major points of convergence across sources
- Note any significant contradictions or areas of ongoing debate
- Include quantitative data, statistical findings, and empirical evidence where available
- Conclude with the overall significance and implications of the findings

QUALITY STANDARDS:
- Demonstrate deep understanding of the subject matter
- Use sophisticated academic language and terminology
- Maintain logical flow and coherent narrative structure
- Avoid redundancy while ensuring comprehensive coverage
- Include temporal context (recent developments vs. established knowledge)

2. KEY INSIGHTS (Critical Discoveries and Patterns):
REQUIREMENTS:
- Present 5-7 most important discoveries, patterns, and analytical conclusions
- Each insight should be substantial, well-supported, and add unique value
- Organize insights by significance and thematic relevance
- Include both explicit findings and implicit patterns you've identified
- Incorporate quantitative metrics, percentages, trends, and statistical significance where relevant
- Address methodological insights and research quality assessments
- Note any paradigm shifts, emerging trends, or revolutionary findings

FORMATTING SPECIFICATIONS:
- Use detailed bullet points (2-3 sentences each)
- Begin each point with a clear, descriptive heading
- Include supporting evidence and source attribution
- Maintain consistent depth and analytical rigor across all points
- Connect insights to broader theoretical implications

3. SUGGESTIONS (Actionable Recommendations and Next Steps):
REQUIREMENTS:
- Provide 4-6 specific, actionable recommendations based directly on the research findings
- Include both immediate practical applications and longer-term strategic considerations
- Address different stakeholder perspectives (researchers, practitioners, policymakers, etc.)
- Suggest methodological improvements or alternative research approaches
- Recommend areas for future investigation or expansion
- Include implementation considerations, resource requirements, and potential challenges
- Prioritize suggestions by feasibility, impact, and evidence strength

CATEGORIZATION:
- Immediate Actions: Steps that can be implemented immediately
- Strategic Initiatives: Longer-term projects or policy changes
- Research Directions: Areas requiring further investigation
- Methodological Improvements: Enhanced approaches to studying the topic
- Practical Applications: Real-world implementation strategies

4. NOTES (Critical Details and Methodological Observations):
REQUIREMENTS:
- Document 4-6 important details, caveats, limitations, and methodological observations
- Include sample sizes, study parameters, geographical scope, and temporal limitations
- Note potential conflicts of interest, funding sources, or institutional biases
- Identify methodological strengths and weaknesses in the research
- Address generalizability concerns and population-specific findings
- Include technical specifications, measurement tools, and analytical approaches
- Note any replication studies, meta-analyses, or systematic reviews

CRITICAL ELEMENTS:
- Data quality assessments and reliability indicators
- Peer review status and publication credibility
- Comparative analysis of different methodological approaches
- Identification of research gaps and understudied areas
- Temporal relevance and currency of the findings
- Cross-cultural or cross-national applicability considerations

5. REFERENCES (Source Attribution and Credibility Assessment):
REQUIREMENTS:
- Provide comprehensive source attribution for all major claims and findings
- Assess credibility, reliability, and academic standing of each source
- Include publication details, institutional affiliations, and author expertise
- Evaluate peer review status, journal impact factors, and citation metrics
- Note any potential biases, conflicts of interest, or methodological concerns
- Organize sources by credibility level and relevance to the research question
- Include both primary sources and secondary analyses where applicable

CREDIBILITY EVALUATION CRITERIA:
- Author expertise and institutional affiliation
- Peer review status and journal reputation
- Methodological rigor and sample quality
- Replication status and citation frequency
- Potential conflicts of interest or funding bias
- Temporal relevance and currency of findings

6. REFLECTING QUESTIONS (Thought-Provoking Inquiries for Deeper Exploration):
REQUIREMENTS:
- Formulate 4-5 sophisticated, thought-provoking questions that emerge from the research
- Include questions that challenge assumptions, explore implications, and suggest new directions
- Address both theoretical and practical dimensions of the research
- Encourage interdisciplinary thinking and cross-field connections
- Include questions about methodology, generalizability, and future research directions
- Formulate questions that promote critical thinking and deeper analysis

QUESTION CATEGORIES:
- Theoretical Questions: Exploring underlying frameworks and conceptual foundations
- Methodological Questions: Investigating research approaches and analytical techniques
- Practical Questions: Examining real-world applications and implementation challenges
- Ethical Questions: Considering moral, social, and policy implications
- Future Research Questions: Identifying unexplored areas and emerging directions

ADVANCED QUALITY STANDARDS:
- ANALYTICAL DEPTH: Demonstrate sophisticated understanding of complex relationships, nuanced interpretations, and multi-layered analysis
- SCHOLARLY PRECISION: Use exact academic terminology, proper citation formats, and methodologically sound interpretations
- SYNTHETIC THINKING: Connect disparate findings into coherent frameworks and identify emergent patterns
- CRITICAL EVALUATION: Assess methodological soundness, identify potential biases, and evaluate evidence quality
- CONTEXTUAL AWARENESS: Situate findings within broader academic discourse and theoretical frameworks
- PRACTICAL RELEVANCE: Bridge academic findings with real-world applications and policy implications

RESPONSE STRUCTURE AND FORMATTING:
- Use clear, descriptive headings for each of the 6 mandatory sections
- Employ hierarchical organization with main points and supporting details
- Utilize bullet points, numbered lists, and paragraph breaks for optimal readability
- Maintain consistent formatting and professional presentation throughout
- Include appropriate academic language and terminology
- Ensure logical flow and coherent narrative across all sections

CONTEXTUAL CONTINUITY AND SESSION MANAGEMENT:
- Maintain comprehensive memory of all previous research queries and findings within the session
- Build upon earlier discoveries and create coherent research narratives
- Reference previous findings when relevant to current analysis
- Address follow-up questions with full contextual awareness
- Develop cumulative understanding that deepens with each query
- Create connections between different research areas explored in the session

CRITICAL THINKING AND ANALYTICAL EXCELLENCE:
- Synthesize information from multiple sources to identify patterns and relationships
- Distinguish between correlation and causation in research findings
- Evaluate competing theories and alternative explanations
- Assess the strength and quality of evidence supporting different claims
- Identify logical fallacies, methodological flaws, and potential biases
- Consider alternative interpretations and competing perspectives
- Examine implications for theory, practice, and policy

RESEARCH INTEGRITY AND ETHICAL CONSIDERATIONS:
- Maintain absolute commitment to accuracy and truthfulness
- Acknowledge limitations, uncertainties, and areas of ongoing debate
- Avoid overgeneralization or extrapolation beyond the evidence
- Respect intellectual property and proper attribution standards
- Consider ethical implications of research findings and recommendations
- Maintain sensitivity to cultural, social, and political contexts

Your responses should exemplify the highest standards of academic excellence, demonstrating scholarly rigor while providing practical value for research purposes. Every analysis should contribute meaningfully to the user's understanding and advancement of knowledge in their field of inquiry."""
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
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanningAgent:
    """Agent that plans and fetches relevant articles for a user query."""
    def __init__(self, api_key: str = ""):
        self.api_key = api_key if api_key else SERPAPI_KEY
        self.engine = "google"

    def fetch_articles(self, query: str, num_results: int = 20) -> list[dict]:
        """Fetch articles using SerpAPI."""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": self.engine,
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

# For backward compatibility, keep the original function
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
    questions = re.findall(r'\d+\.\s*(.+)', response)
    if not questions:
        questions = [q.strip('-•* ') for q in response.split('\n') if q.strip()]
    return questions[:4]

def generate_report(topic: str, summary: str, notes: str, key_insights: str, suggestions: list, sources: list) -> str:
    """Generate a one-page academic report using the LLM"""
    user_prompt = {
        "role": "user",
        "content": f'''
TASK: Academic Report Generation

RESEARCH TOPIC: "{topic}"

OBJECTIVE:
Write a one-page academic report (about 400-500 words) on the topic above, using the provided summary, notes, key insights, suggestions, and sources. Structure the report with clear sections (e.g., Introduction, Main Discussion, Conclusion). Use formal academic language and synthesize the information into a coherent narrative.

PROVIDED MATERIAL:
- Summary: {summary}
- Notes: {notes}
- Key Insights: {key_insights}
- Suggestions: {suggestions}
- Sources: {sources}

OUTPUT:
A one-page academic report.
'''
    }
    return generate_llm_response([system_prompt, user_prompt], temperature=0.3, max_tokens=700)

class ComparisonAgent:
    """Agent that compares articles and extracts the most relevant data and insights."""
    def __init__(self):
        pass

    def compare_and_extract(self, articles: list[dict]) -> dict:
        """Compare articles and extract the most relevant data and insights using the LLM."""
        # Prepare the content for the LLM
        articles_text = "\n\n".join([
            f"Title: {a.get('title', '')}\nSnippet: {a.get('snippet', '')}" for a in articles
        ])
        user_prompt = {
            "role": "user",
            "content": f'''
TASK: Advanced Article Comparison and Relevance Extraction for Report Generation

AGENT ROLE: You are an expert research analyst and content synthesizer specializing in academic and professional report preparation. Your task is to analyze, compare, and extract the most valuable information from multiple articles to create a comprehensive knowledge base for report writing.

SEARCH CONTEXT:
Research Query: "{search_query}"
Report Topic: "{report_topic}"

ANALYSIS OBJECTIVES:
1. Identify and extract content directly relevant to the search query and report topic
2. Synthesize information from multiple sources to create a coherent knowledge base
3. Eliminate redundancy while preserving unique insights from each source
4. Prioritize high-quality, credible, and substantive information
5. Structure findings to facilitate easy report writing and citation

COMPREHENSIVE ANALYSIS FRAMEWORK:

A. RELEVANCE ASSESSMENT CRITERIA:
- Direct alignment with search query keywords and concepts
- Topical relevance to the overall report subject
- Quality and credibility of information source
- Uniqueness and novelty of insights presented
- Potential impact on report conclusions and recommendations
- Statistical data, research findings, or empirical evidence
- Expert opinions, case studies, or real-world applications

B. CONTENT CATEGORIZATION:
For each article, evaluate and categorize content into:
1. CORE FINDINGS: Primary research results, key statistics, main conclusions
2. SUPPORTING EVIDENCE: Secondary data, corroborating information, background context
3. EXPERT INSIGHTS: Professional opinions, analysis, interpretations
4. PRACTICAL APPLICATIONS: Real-world examples, case studies, implementation details
5. TRENDS AND PATTERNS: Emerging developments, historical context, future predictions
6. METHODOLOGICAL INFORMATION: Research approaches, data collection methods, study parameters

C. COMPARATIVE ANALYSIS REQUIREMENTS:
- Identify convergent themes across multiple articles
- Highlight contradictory findings or conflicting perspectives
- Note gaps in coverage or areas requiring additional research
- Compare methodologies, sample sizes, and research quality
- Assess temporal relevance (recent vs. historical information)
- Evaluate geographical or demographic scope of findings

D. SYNTHESIS METHODOLOGY:
1. Cross-reference information across articles to identify patterns
2. Consolidate similar findings while preserving source-specific nuances
3. Create logical groupings of related information
4. Prioritize information based on credibility, recency, and relevance
5. Integrate quantitative data with qualitative insights
6. Maintain source attribution for key claims and statistics

DETAILED OUTPUT REQUIREMENTS:

SECTION 1: EXECUTIVE SUMMARY (100-150 words)
- Concise overview of the most critical findings
- Key themes that emerged across multiple articles
- Most significant statistics or research outcomes
- Primary areas of consensus and disagreement among sources

SECTION 2: KEY FINDINGS BY THEME
Organize extracted information into 3-5 major themes, each including:
- Theme title and brief description
- Core findings from each relevant article
- Supporting statistics and data points
- Notable quotes or expert opinions (with source attribution)
- Practical implications or applications

SECTION 3: COMPARATIVE ANALYSIS
- Areas of convergence: Where multiple sources agree
- Contradictory findings: Where sources disagree and why
- Methodological differences that might explain discrepancies
- Quality assessment of different sources
- Identification of the most authoritative or comprehensive sources

SECTION 4: RESEARCH GAPS AND LIMITATIONS
- Topics mentioned but not thoroughly covered
- Methodological limitations noted in the articles
- Areas where additional research would be beneficial
- Temporal or geographical limitations of the findings

SECTION 5: QUANTITATIVE DATA SUMMARY
- All relevant statistics, percentages, and numerical data
- Trends and patterns in quantitative findings
- Comparisons across different studies or time periods
- Data quality and reliability assessments

SECTION 6: PRACTICAL APPLICATIONS AND IMPLICATIONS
- Real-world applications mentioned in the articles
- Case studies or examples provided
- Implementation challenges and solutions
- Recommendations from the original sources

SECTION 7: SOURCE QUALITY ASSESSMENT
- Credibility ranking of sources (academic, industry, news, etc.)
- Publication dates and temporal relevance
- Author expertise and institutional affiliations
- Potential biases or limitations noted

QUALITY STANDARDS:
- Maintain objectivity and avoid introducing personal interpretation
- Preserve the original meaning and context of source material
- Use clear, precise language suitable for academic/professional reports
- Ensure all major claims are attributable to specific sources
- Eliminate redundancy while preserving important nuances
- Organize information logically and coherently

FORMATTING SPECIFICATIONS:
- Use clear section headings and subheadings
- Present information in well-structured paragraphs
- Include brief bullet points for key statistics or findings
- Maintain consistent formatting throughout
- Use plain text without markdown or special formatting
- Ensure proper attribution format: [Source Title, Author/Publication]

CRITICAL ANALYSIS ELEMENTS:
- Evaluate the strength of evidence presented
- Note any methodological concerns or limitations
- Identify potential conflicts of interest or biases
- Assess the generalizability of findings
- Consider the practical significance of research outcomes

ARTICLES TO ANALYZE:
--- BEGIN ARTICLES ---
{articles_text}
--- END ARTICLES ---

DELIVERABLE:
Provide a comprehensive, structured analysis that synthesizes the most relevant and valuable information from the provided articles. The output should serve as a robust foundation for report writing, with clear organization, proper attribution, and elimination of redundancy while preserving unique insights from each source.

Focus on creating a knowledge base that will enable the creation of a high-quality, evidence-based report on the specified topic.
'''
        }
        summary = generate_llm_response([system_prompt, user_prompt], temperature=0.3, max_tokens=600)
        return {"relevant_summary": summary}

class ReportGenerationAgent:
    """Agent that generates a structured academic report from relevant data."""
    def __init__(self):
        pass

    def clean_report(self, report: str) -> str:
        # Remove leading spaces and hashes from section headings, and collapse multiple blank lines
        import re
        lines = report.split('\n')
        cleaned_lines = [re.sub(r'^\s*#+\s*', '', line) for line in lines]
        cleaned_report = '\n'.join(cleaned_lines)
        # Collapse multiple blank lines to a single blank line
        cleaned_report = re.sub(r'\n{3,}', '\n\n', cleaned_report)
        return cleaned_report.strip()

    def generate_structured_report(self, relevant_data: str, topic: str) -> str:
        """Generate a structured academic report with title, abstract, introduction, body, conclusion, and recommendations. Output should be clean, plain text with clear section headings and no markdown or special formatting."""
        user_prompt = {
            "role": "user",
            "content": f'''
TASK: Comprehensive Academic Report Generation

RESEARCH TOPIC: "{topic}"

CONTEXT AND BACKGROUND:
You are an expert academic researcher and report writer. Your task is to create a professional, well-structured academic report that demonstrates deep analysis, critical thinking, and scholarly rigor. The report should be suitable for academic or professional presentation.

DETAILED REQUIREMENTS:

1. STRUCTURE AND ORGANIZATION:
   - Title: Create a clear, descriptive title that accurately reflects the research topic and scope
   - Abstract: Write a concise 150-200 word summary covering purpose, methodology, key findings, and conclusions
   - Introduction: Provide comprehensive background, context, problem statement, objectives, and scope (300-400 words)
   - Main Body: Develop 3-4 well-organized sections with clear subheadings, each focusing on different aspects of the analysis (800-1200 words total)
   - Conclusion: Synthesize findings, address research objectives, and discuss implications (200-300 words)
   - Recommendations: Provide actionable, specific recommendations based on findings (150-250 words)

2. CONTENT QUALITY STANDARDS:
   - Demonstrate analytical depth and critical evaluation of the data
   - Use evidence-based arguments supported by the provided data
   - Include specific examples, statistics, and concrete details from the relevant data
   - Maintain academic tone throughout - formal, objective, and scholarly
   - Ensure logical flow between sections and coherent argumentation
   - Address potential limitations or counterarguments where appropriate

3. WRITING STYLE GUIDELINES:
   - Use clear, concise, and professional language
   - Employ varied sentence structures for readability
   - Include transition sentences between major sections
   - Use active voice where appropriate
   - Maintain consistency in terminology and style
   - Ensure proper grammar, spelling, and punctuation

4. FORMATTING SPECIFICATIONS:
   - Each section must start with its heading on a new line (Title, Abstract, Introduction, etc.)
   - Use ONLY plain text - NO markdown, asterisks, hashes, bullets, or special formatting
   - Separate sections with a single blank line
   - Use paragraph breaks within sections for readability
   - Maintain consistent spacing and alignment

5. ANALYTICAL APPROACH:
   - Identify key patterns, trends, and insights from the data
   - Provide quantitative analysis where relevant (percentages, comparisons, etc.)
   - Discuss implications and significance of findings
   - Connect findings to broader themes or industry contexts
   - Highlight any unexpected or particularly noteworthy discoveries

6. EVIDENCE INTEGRATION:
   - Seamlessly integrate data points into narrative flow
   - Provide specific examples to support general statements
   - Use data to substantiate claims and conclusions
   - Reference specific aspects of the provided data throughout the report

7. RECOMMENDATIONS CRITERIA:
   - Make recommendations specific, actionable, and realistic
   - Base recommendations directly on report findings
   - Prioritize recommendations by importance or feasibility
   - Consider implementation challenges and resource requirements
   - Address different stakeholder perspectives where relevant

RELEVANT DATA AND INFORMATION:
--- BEGIN DATA ---
{relevant_data}
--- END DATA ---

QUALITY EXPECTATIONS:
- The report should read as a cohesive, professional document
- All sections should be substantive and add value to the overall analysis
- The writing should be engaging while maintaining academic rigor
- Conclusions should be well-supported by the evidence presented
- The report should provide genuine insights and value to the reader

OUTPUT FORMAT:
Deliver a complete academic report with all specified sections in clean, plain text format. The report should be comprehensive, well-researched, and professionally written, suitable for academic or business presentation.

Begin your response with the title and proceed through each section in order.
'''
        }
        report = generate_llm_response([system_prompt, user_prompt], temperature=0.3, max_tokens=900)
        return self.clean_report(report)

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

# Session management endpoints
@app.post("/session", response_model=SessionInfo)
async def create_or_get_session(request: SessionRequest):
    """Create a new session or get existing session info (shows MongoDB results)"""
    session_id = request.session_id or str(uuid.uuid4())
    # Get session from storage
    sessions = await storage_manager.get_session(session_id)
    # Prefer MongoDB if available, else file
    session = sessions.get("mongodb") or sessions.get("file")
    if session:
        return {
            "session_id": session.get("session_id", session_id),
            "current_topic": session.get("current_topic"),
            "research_count": len(session.get("research_history", [])),
            "conversation_count": len(session.get("conversation_history", [])),
            "created_at": session.get("created_at"),
            "all_storage": sessions
        }
    # Create new session in storage
    created = await storage_manager.create_session(session_id)
    created_session = created.get("mongodb") or created.get("file")
    return {
        "session_id": created_session.get("session_id", session_id),
        "current_topic": created_session.get("current_topic"),
        "research_count": 0,
        "conversation_count": 0,
        "created_at": created_session.get("created_at"),
        "all_storage": created
    }

@app.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    sessions = await storage_manager.get_session(session_id)
    session = sessions.get("mongodb") or sessions.get("file")
    if session:
        return {
            "session_id": session.get("session_id", session_id),
            "current_topic": session.get("current_topic"),
            "research_count": len(session.get("research_history", [])),
            "conversation_count": len(session.get("conversation_history", [])),
            "created_at": session.get("created_at"),
            "all_storage": sessions
        }
    # If not found, create a new session
    created = await storage_manager.create_session(session_id)
    created_session = created.get("mongodb") or created.get("file")
    return {
        "session_id": created_session.get("session_id", session_id),
        "current_topic": created_session.get("current_topic"),
        "research_count": 0,
        "conversation_count": 0,
        "created_at": created_session.get("created_at"),
        "all_storage": created
    }

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
        # Typo correction for the research topic
        corrected_topic = str(TextBlob(request.topic).correct())
        correction_made = corrected_topic.strip().lower() != request.topic.strip().lower()
        num_results = request.num_results if request.num_results is not None else 3
        results = search_serpapi(corrected_topic, num_results)
        if not results:
            raise HTTPException(status_code=404, detail="No search results found")
        summary = generate_summary(corrected_topic, results)
        notes = generate_notes(corrected_topic, results)
        key_insights = generate_key_insights(corrected_topic, [r["snippet"] for r in results if r["snippet"]])
        suggestions = generate_suggestions(corrected_topic)
        reflecting_questions = generate_reflecting_questions(corrected_topic)
        timestamp = datetime.now().isoformat()
        # Generate the report
        report = generate_report(
            corrected_topic,
            summary,
            notes,
            key_insights,
            suggestions,
            results
        )
        research_entry = {
            "timestamp": timestamp,
            "topic": corrected_topic,
            "original_topic": request.topic,
            "correction_made": correction_made,
            "results": results,
            "summary": summary,
            "notes": notes,
            "insights": key_insights,
            "sources": results
        }
        session = await storage_manager.get_session(session_id)
        if session:
            if "research_history" not in session:
                session["research_history"] = []
            session["research_history"].append(research_entry)
            session["current_topic"] = corrected_topic
            if "sources" not in session:
                session["sources"] = []
            session["sources"].extend(results)
            await storage_manager.update_session(session_id, session)
        await storage_manager.add_search_history(session_id, {
            "query": corrected_topic,
            "timestamp": timestamp,
            "num_results": num_results
        })
        return {
            "session_id": session_id,
            "topic": corrected_topic,
            "original_topic": request.topic,
            "correction_made": correction_made,
            "timestamp": timestamp,
            "summary": summary,
            "notes": notes,
            "key_insights": key_insights,
            "sources": [ResearchResult(**r) for r in results],
            "suggestions": suggestions,
            "report": report,
            "reflecting_questions": reflecting_questions
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Research error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_aria(request: ChatRequest):
    """Chat with ARIA using MongoDB-backed session"""
    try:
        session = await storage_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        # Get the current topic from the session
        current_topic = session.get("current_topic", "(no topic)")
        # Stricter system prompt enforcing topic relevance
        strict_system_prompt = {
            "role": "system",
            "content": f"""
You are ARIA (Advanced Research Intelligence Assistant), a sophisticated AI research assistant specializing in the current research topic: "{current_topic}".

CORE IDENTITY AND ROLE:
- You are an expert research assistant with deep knowledge across multiple domains
- Your primary function is to provide accurate, insightful, and contextually relevant information
- You maintain academic rigor while being conversational and accessible
- You are patient, thorough, and committed to helping users understand complex topics

TOPIC ADHERENCE PROTOCOL:
Current Research Topic: "{current_topic}"

RESPONSE RULES:
1. If the user's question is related to "{current_topic}", answer it fully and helpfully.
2. If the user's question is only tangentially related, acknowledge the connection and answer as best you can, but gently guide the user back to the main topic.
3. If the user's question is clearly unrelated, respond with: "Our current topic is {current_topic}. Would you like to switch topics or ask something related?"
4. Consider as related: definitions, types, history, applications, comparisons, and any reasonable follow-up to the main topic.

CONVERSATION CONTEXT MANAGEMENT:
- ALWAYS maintain conversation history and context
- Reference previous exchanges naturally using phrases like "As we discussed earlier..." or "Building on your previous question..."
- When users say "this," "that," "it," "these," or similar pronouns, understand they refer to topics from our conversation
- NEVER ask users to repeat themselves or clarify what they're referring to
- Seamlessly connect follow-up questions to previous context
- If multiple topics were discussed, prioritize the most recent relevant context

RESPONSE QUALITY STANDARDS:
1. ACCURACY: Provide factual, evidence-based information
2. DEPTH: Go beyond surface-level answers to provide comprehensive insights
3. CLARITY: Use clear, accessible language while maintaining academic precision
4. STRUCTURE: Organize complex information logically with clear transitions
5. RELEVANCE: Ensure every part of your response relates to the user's specific question
6. BALANCE: Provide multiple perspectives when appropriate, acknowledge limitations

COMMUNICATION STYLE:
- Tone: Professional yet conversational, approachable but authoritative
- Language: Clear, precise, and appropriately technical for the context
- Structure: Use paragraphs, natural transitions, and logical flow
- Engagement: Show genuine interest in helping the user understand the topic
- Acknowledgment: Recognize good questions and build upon user insights

SPECIFIC RESPONSE GUIDELINES:
1. For factual questions: Provide detailed, accurate information with context
2. For analytical questions: Offer multiple perspectives and evidence-based analysis
3. For comparative questions: Draw clear distinctions and similarities
4. For practical questions: Include real-world applications and examples
5. For complex questions: Break down into manageable components
6. For follow-up questions: Build seamlessly on previous context

CONVERSATION FLOW MANAGEMENT:
- Begin responses naturally without formulaic openings
- Use transitional phrases to connect ideas
- Maintain thread continuity throughout the conversation
- End responses with insight or opening for further discussion when appropriate
- Avoid repetitive phrases or mechanical responses

HANDLING AMBIGUITY:
- When questions are unclear, make reasonable assumptions based on context
- If multiple interpretations exist, address the most likely one first
- Use conversation history to disambiguate unclear references
- Provide comprehensive answers that cover potential interpretations

KNOWLEDGE INTEGRATION:
- Draw connections between different aspects of the topic
- Integrate current events and recent developments when relevant
- Reference authoritative sources and established research
- Acknowledge areas of ongoing debate or uncertainty
- Provide historical context when it enhances understanding

ERROR HANDLING:
- If you don't know something, admit it honestly
- Suggest alternative approaches or related information
- Maintain helpfulness even when facing limitations
- Guide users toward productive lines of inquiry

CONVERSATION ENHANCEMENT:
- Ask thoughtful follow-up questions when appropriate
- Suggest related areas of exploration
- Highlight particularly interesting or important aspects
- Encourage deeper thinking about the topic
- Provide practical next steps when relevant

EXAMPLES OF EXCELLENT RESPONSES:
✓ "Building on what we discussed about [previous topic], this connects to [current question] because..."
✓ "The research you mentioned earlier actually supports this point in several ways..."
✓ "This aspect of {current_topic} is particularly fascinating because..."
✓ "While we've covered [X], your question about [Y] opens up another important dimension..."

EXAMPLES OF RESPONSES TO AVOID:
✗ "Can you clarify what you mean by 'this'?"
✗ "I don't understand what you're referring to."
✗ "Please provide more context."
✗ Generic responses without topic-specific insight

REMEMBER:
- You are an expert specifically focused on "{current_topic}"
- Every interaction should advance the user's understanding
- Context is king - use it to provide seamless, intelligent responses
- Academic rigor does not mean being dry or inaccessible
- Your goal is to be the most helpful research assistant possible within your topic domain

Your responses should demonstrate expertise, maintain focus, and provide genuine value to users exploring "{current_topic}".
"""
        }
        messages = [strict_system_prompt]
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

class FullResearchRequest(BaseModel):
    query: str
    num_results: int = 20

class FullResearchResponse(BaseModel):
    articles: list[dict]
    relevant_summary: str
    structured_report: str

@app.post("/full-research", response_model=FullResearchResponse)
async def full_research(request: FullResearchRequest = Body(...)):
    """Pipeline: Plan (fetch articles) -> Compare (extract relevant) -> Report (generate structured report)"""
    # 1. Planning Agent: Fetch articles
    planner = PlanningAgent()
    articles = planner.fetch_articles(request.query, request.num_results)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the query.")

    # 2. Comparison Agent: Extract most relevant data
    comparer = ComparisonAgent()
    relevant = comparer.compare_and_extract(articles)
    relevant_summary = relevant["relevant_summary"]

    # 3. Report Generation Agent: Generate structured report
    reporter = ReportGenerationAgent()
    structured_report = reporter.generate_structured_report(relevant_summary, request.query)

    return FullResearchResponse(
        articles=articles,
        relevant_summary=relevant_summary,
        structured_report=structured_report
    )

handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)