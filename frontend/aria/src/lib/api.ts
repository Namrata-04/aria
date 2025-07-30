const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
export interface ResearchRequest {
  topic: string;
  num_results?: number;
}

export interface ChatMessage {
  role: 'user' | 'ai';
  content: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  history?: ChatMessage[];
}

export interface SessionRequest {
  session_id?: string;
}

export interface ResearchResult {
  title: string;
  link: string;
  author: string;
  published: string;
  snippet: string;
}

export interface ResearchResponse {
  session_id: string;
  topic: string;
  original_topic?: string;
  correction_made?: boolean;
  timestamp: string;
  summary: string;
  notes: string;
  key_insights: string;
  sources: ResearchResult[];
  suggestions: string[];
  report?: string;
  reflecting_questions: string[];
}

export interface ChatResponse {
  session_id: string;
  response: string;
  timestamp: string;
}

export interface SessionInfo {
  session_id: string;
  current_topic?: string;
  research_count: number;
  conversation_count: number;
  created_at: string;
}

// MongoDB-specific interfaces
export interface SaveResearchRequest {
  session_id: string;
  query: string;
  section_name: string;
  content: string;
}

export interface SearchHistoryResponse {
  searches: Array<{
    query: string;
    timestamp: string;
    num_results: number;
  }>;
  total: number;
}

export interface SavedResearchResponse {
  saved_research: Array<{
    query: string;
    section_name: string;
    content: string;
    saved_at: string;
  }>;
  total: number;
}

export interface FullResearchRequest {
  query: string;
  num_results?: number;
}

export interface FullResearchResponse {
  articles: ResearchResult[];
  relevant_summary: string;
  structured_report: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Ensure the base URL does not have a trailing slash and the endpoint has a leading slash
    const cleanedBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    const cleanedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    const url = `${cleanedBaseUrl}${cleanedEndpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Session management
  async createOrGetSession(sessionId?: string): Promise<SessionInfo> {
    return this.request<SessionInfo>('/session', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  async listSessions(): Promise<SessionInfo[]> {
    return this.request<SessionInfo[]>('/sessions');
  }

  async getSessionHistory(sessionId: string): Promise<any> {
    return this.request(`/session/${sessionId}/history`);
  }

  async deleteSession(sessionId: string): Promise<void> {
    return this.request(`/session/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // Research functionality
  async conductResearch(
    topic: string,
    numResults: number = 3,
    sessionId?: string
  ): Promise<ResearchResponse> {
    const params = new URLSearchParams();
    if (sessionId) {
      params.append('session_id', sessionId);
    }

    return this.request<ResearchResponse>(`/research?${params.toString()}`, {
      method: 'POST',
      body: JSON.stringify({
        topic,
        num_results: numResults,
      }),
    });
  }

  // Chat functionality
  async chatWithAria(sessionId: string, message: string, history?: ChatMessage[]): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        message,
        history,
      }),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  // Search History
  async getSearchHistory(sessionId: string): Promise<SearchHistoryResponse> {
    return this.request<SearchHistoryResponse>(`/search-history/${sessionId}`);
  }

  // Saved Research
  async saveResearchSection(request: SaveResearchRequest): Promise<{ message: string }> {
    return this.request<{ message: string }>('/save-research', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getSavedResearch(sessionId: string): Promise<SavedResearchResponse> {
    return this.request<SavedResearchResponse>(`/saved-research/${sessionId}`);
  }

  async deleteSavedResearch(sessionId: string, query: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/saved-research/${sessionId}/${encodeURIComponent(query)}`, {
      method: 'DELETE',
    });
  }

  async getAllSavedResearch(): Promise<SavedResearchResponse> {
    return this.request<SavedResearchResponse>(`/saved-research-all`);
  }

  async getAllSearchHistory(): Promise<{ search_history: any[]; total: number }> {
    return this.request<{ search_history: any[]; total: number }>(`/search-history-all`);
  }

  async fullResearch(request: FullResearchRequest): Promise<FullResearchResponse> {
    return this.request<FullResearchResponse>('/full-research', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}

export const apiService = new ApiService();
export default apiService;

// Signup
export async function signup(name: string, email: string, password: string) {
  const res = await fetch('/api/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) throw new Error('Signup failed');
  return res.json();
}

// Login
export async function login(email: string, password: string) {
  const res = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json(); // { access_token, token_type }
} 