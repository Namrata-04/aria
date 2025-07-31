const API_BASE_URL = "https://aria-production-ea4a.up.railway.app"

export const api = {
  async createSession() {
    const response = await fetch(`${API_BASE_URL}/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSession(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async chat(sessionId: string, message: string, researchTopic?: string) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        research_topic: researchTopic,
      }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async research(sessionId: string, topic: string, numResults: number = 2) {
    const response = await fetch(`${API_BASE_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: topic,
        num_results: numResults,
      }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },
}

// Create a compatible apiService for backward compatibility
export const apiService = {
  async createOrGetSession() {
    return api.createSession()
  },
  
  async conductResearch(topic: string, numResults: number = 3, sessionId?: string) {
    return api.research(sessionId || 'default', topic, numResults)
  },
  
  async chatWithAria(sessionId: string, message: string, history?: any[], researchTopic?: string) {
    return api.chat(sessionId, message, researchTopic)
  },
  
  async getAllSavedResearch() {
    return { saved_research: [], total: 0 }
  },
  
  async deleteSavedResearch(sessionId: string, query: string) {
    return { message: "Deleted" }
  },
  
  async saveResearchSection(request: any) {
    return { message: "Saved" }
  }
}

// Export types for compatibility
export interface ResearchResponse {
  session_id: string;
  topic: string;
  timestamp: string;
  summary: string;
  notes: string;
  key_insights: string;
  sources: any[];
  suggestions: string[];
  reflecting_questions: string[];
}

export interface SaveResearchRequest {
  session_id: string;
  query: string;
  section_name: string;
  content: string;
} 