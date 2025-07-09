import { useState, useCallback } from 'react';
import { apiService, ResearchResponse, ChatResponse, SessionInfo } from '@/lib/api';

export interface ChatState {
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  researchResults: ResearchResponse | null;
  chatHistory: ChatResponse[];
  searchHistory: string[];
}

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    sessionId: null,
    isLoading: false,
    error: null,
    researchResults: null,
    chatHistory: [],
    searchHistory: [],
  });

  // Initialize or get existing session
  const initializeSession = useCallback(async (sessionId?: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const session = await apiService.createOrGetSession(sessionId);
      setState(prev => ({
        ...prev,
        sessionId: session.session_id,
        isLoading: false,
      }));
      return session;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to initialize session',
      }));
      throw error;
    }
  }, []);

  // Conduct research
  const conductResearch = useCallback(async (topic: string, numResults: number = 3) => {
    if (!state.sessionId) {
      throw new Error('No active session');
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const results = await apiService.conductResearch(topic, numResults, state.sessionId);
      
      setState(prev => ({
        ...prev,
        researchResults: results,
        searchHistory: [topic, ...prev.searchHistory.filter(s => s !== topic)],
        isLoading: false,
      }));
      
      return results;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Research failed',
      }));
      throw error;
    }
  }, [state.sessionId]);

  // Send chat message
  const sendMessage = useCallback(async (message: string) => {
    if (!state.sessionId) {
      throw new Error('No active session');
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await apiService.chatWithAria(state.sessionId, message);
      
      setState(prev => ({
        ...prev,
        chatHistory: [...prev.chatHistory, response],
        isLoading: false,
      }));
      
      return response;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message',
      }));
      throw error;
    }
  }, [state.sessionId]);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Reset state
  const reset = useCallback(() => {
    setState({
      sessionId: null,
      isLoading: false,
      error: null,
      researchResults: null,
      chatHistory: [],
      searchHistory: [],
    });
  }, []);

  return {
    ...state,
    initializeSession,
    conductResearch,
    sendMessage,
    clearError,
    reset,
  };
}; 