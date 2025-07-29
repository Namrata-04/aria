import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Send, 
  FileText, 
  Lightbulb, 
  BookOpen, 
  Link as LinkIcon, 
  MessageSquare,
  History,
  Save,
  ArrowLeft,
  Search,
  AlertCircle,
  Trash2,
  ClipboardCopy,
  Copy,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import { apiService, ResearchResponse, SaveResearchRequest } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui/dialog';
import { toast } from '@/hooks/use-toast';
import { extractKeywords } from '@/lib/utils';

// Helper function to linkify URLs in text
function linkify(text: string) {
  // Remove [Link] or [link] (case-insensitive) from the text
  const cleaned = text.replace(/\[link\]/gi, '');
  const urlRegex = /(https?:\/\/[^\s)]+)/g;
  const parts = cleaned.split(urlRegex);
  return parts.map((part, i) => {
    if (urlRegex.test(part)) {
      return (
        <a
          key={i}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline break-all"
        >
          {part}
        </a>
      );
    }
    return part;
  });
}

const ChatNew = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [researchResults, setResearchResults] = useState<ResearchResponse | null>(null);
  const summaryRef = useRef<HTMLDivElement>(null);
  const insightsRef = useRef<HTMLDivElement>(null);
  const notesRef = useRef<HTMLDivElement>(null);
  const referencesRef = useRef<HTMLDivElement>(null);
  const questionsRef = useRef<HTMLDivElement>(null);
  const [recentSearches, setRecentSearches] = useState<{query: string, timestamp: number}[]>(() => {
    const stored = localStorage.getItem('aria_recent_searches');
    if (!stored) return [];
    try {
      const arr = JSON.parse(stored);
      if (arr.length && typeof arr[0] === 'string') {
        return arr.map((q: string) => ({ query: q, timestamp: Date.now() }));
      } else {
        return arr;
      }
    } catch {
      return [];
    }
  });
  const [showHistory, setShowHistory] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [savedData, setSavedData] = useState<any>({});
  const [chatMessages, setChatMessages] = useState<{role: 'user' | 'ai', content: string}[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [copiedMsgIdx, setCopiedMsgIdx] = useState<number | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [isShowingSavedResults, setIsShowingSavedResults] = useState(false);
  const [savedResearchResults, setSavedResearchResults] = useState<any>(null);
  const [expandedSections, setExpandedSections] = useState<{[label: string]: boolean}>({});
  const [showResearchTabs, setShowResearchTabs] = useState(true);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const res = await apiService.createOrGetSession();
        setSessionId(res.session_id);
      } catch (e) {
        setError('Failed to initialize session');
      }
    };
    initSession();
  }, []);

  // Restore localStorage for recentSearches
  useEffect(() => {
    const stored = localStorage.getItem('aria_recent_searches');
    if (!stored) return setRecentSearches([]);
    try {
      const arr = JSON.parse(stored);
      if (arr.length && typeof arr[0] === 'string') {
        setRecentSearches(arr.map((q: string) => ({ query: q, timestamp: Date.now() })));
      } else {
        setRecentSearches(arr);
      }
    } catch {
      setRecentSearches([]);
    }
  }, [showHistory]);

  // Load saved research from MongoDB when dialog is opened
  useEffect(() => {
    if (showSaved) {
      loadSavedResearch();
    }
  }, [showSaved]);

  const loadSavedResearch = async () => {
    try {
      const response = await apiService.getAllSavedResearch();
      const savedDataMap: any = {};
      // Group by query and section_name
      response.saved_research.forEach(item => {
        if (!savedDataMap[item.query]) {
          savedDataMap[item.query] = {};
        }
        savedDataMap[item.query][item.section_name] = {
          content: item.content,
          saved_at: item.saved_at
        };
      });
      setSavedData(savedDataMap);
      console.log('Loaded all saved research:', savedDataMap);
    } catch (error) {
      console.error('Failed to load all saved research:', error);
      toast({
        title: 'Error',
        description: 'Failed to load all saved research',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteSaved = async (queryToDelete: string) => {
    if (!sessionId) return;
    try {
      await apiService.deleteSavedResearch(sessionId, queryToDelete);
      setSavedData((prev: any) => {
        const newData = { ...prev };
        delete newData[queryToDelete];
        return newData;
      });
      toast({
        title: 'Deleted!',
        description: 'Saved research deleted successfully',
      });
    } catch (error) {
      console.error('Failed to delete:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete',
        variant: 'destructive',
      });
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;
    setIsLoading(true);
    setError(null);
    setResearchResults(null);
    // Update recent searches in localStorage
    setRecentSearches(prev => {
      const now = Date.now();
      const filtered = prev.filter(item => item.query !== input.trim());
      const updated = [{ query: input.trim(), timestamp: now }, ...filtered].slice(0, 10);
      localStorage.setItem('aria_recent_searches', JSON.stringify(updated));
      return updated;
    });
    try {
      const res = await apiService.conductResearch(input, 3, sessionId);
      setResearchResults(res);
      setInput('');
    } catch (e: any) {
      setError(e.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !sessionId) return;
    if (showResearchTabs) setShowResearchTabs(false); // Hide research tabs on first chat
    const userMsg = { role: 'user' as const, content: chatInput.trim() };
    setChatMessages(prev => [...prev, userMsg]);
    const msgForAI = chatInput.trim();
    setChatInput('');
    setIsChatLoading(true);
    try {
      const res = await apiService.chatWithAria(sessionId, msgForAI, [...chatMessages, userMsg]);
      setChatMessages(prev => [...prev, { role: 'ai' as const, content: res.response }]);
    } catch (err: any) {
      setChatMessages(prev => [...prev, { role: 'ai' as const, content: 'Sorry, there was an error getting a response.' }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Helper to group searches by time
  function groupSearches(searches: {query: string, timestamp: number}[]) {
    const groups: { [label: string]: {query: string, timestamp: number}[] } = {};
    const now = new Date();
    searches.forEach(item => {
      const date = new Date(item.timestamp);
      const diffMs = now.getTime() - date.getTime();
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      let label = '';
      if (diffDays === 0 && now.getDate() === date.getDate()) label = 'Today';
      else if (diffDays === 1 || (diffDays === 0 && now.getDate() !== date.getDate())) label = 'Yesterday';
      else if (diffDays < 7) label = 'Last Week';
      else if (diffDays < 30) label = 'Last Month';
      else label = 'Older';
      if (!groups[label]) groups[label] = [];
      groups[label].push(item);
    });
    return groups;
  }

  // Add this helper for animated dots
  const TypingDots = () => (
    <span className="inline-flex">
      <span className="animate-bounce" style={{ animationDelay: '0ms' }}>.</span>
      <span className="animate-bounce" style={{ animationDelay: '150ms' }}>.</span>
      <span className="animate-bounce" style={{ animationDelay: '300ms' }}>.</span>
    </span>
  );

  // Restore handleCopy and handleSave for research result tabs
  const handleCopy = (ref: React.RefObject<HTMLDivElement>) => {
    if (ref.current) {
      const text = ref.current.innerText;
      navigator.clipboard.writeText(text);
      toast({
        title: 'Copied!',
        description: (
          <span className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="4" fill="#99f6e4"/><path d="M8 12h8M8 16h4" stroke="#14b8a6" strokeWidth="1.5" strokeLinecap="round"/></svg>
            Content copied to clipboard.
          </span>
        ),
      });
    }
  };

  const handleSave = async (section: string, content: string) => {
    if (!input && !researchResults) return;
    const query = input || (recentSearches && recentSearches[0]?.query) || '';
    if (!query || !sessionId) return;

    try {
      const saveRequest = {
        session_id: sessionId,
        query: query,
        section_name: section,
        content: content
      };

      await apiService.saveResearchSection(saveRequest);
      // Update local state for dialog
      setSavedData((prev: any) => ({
        ...prev,
        [query]: {
          ...prev[query],
          [section]: { content, saved_at: new Date().toISOString() }
        }
      }));
      toast({
        title: 'Saved!',
        description: (
          <span className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="12" fill="#fef3c7"/><path d="M7 13l3 3 7-7" stroke="#f59e42" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            {section} saved successfully.
          </span>
        ),
      });
    } catch (error) {
      console.error('Failed to save:', error);
      toast({
        title: 'Error',
        description: 'Failed to save',
        variant: 'destructive',
      });
    }
  };

  const handleSearchHistoryClick = async (query: string) => {
    setInput(query);
    setIsLoading(true);
    setError(null);
    setResearchResults(null);
    setIsShowingSavedResults(false);
    
    try {
      // First, check if we have saved research for this query
      const savedResponse = await apiService.getAllSavedResearch();
      const savedForQuery = savedResponse.saved_research.filter(
        (item: any) => item.query === query
      );
      
      if (savedForQuery.length > 0) {
        // Display saved results
        const savedData = savedForQuery.reduce((acc: any, item: any) => {
          if (!acc[item.section_name]) {
            acc[item.section_name] = item.content;
          }
          return acc;
        }, {});
        
        setSavedResearchResults({
          topic: query,
          summary: savedData.Summary || savedData.summary || '',
          notes: savedData.Notes || '',
          key_insights: savedData.KeyInsights || savedData.key_insights || '',
          suggestions: savedData.Suggestions ? savedData.Suggestions.split('\n').filter((s: string) => s.trim()) : [],
          reflecting_questions: savedData.ReflectingQuestions ? savedData.ReflectingQuestions.split('\n').filter((s: string) => s.trim()) : [],
          sources: savedData.References ? savedData.References.split('\n').map((link: string) => ({ link: link.trim() })) : []
        });
        setIsShowingSavedResults(true);
      } else {
        // No saved results, conduct new research
        const res = await apiService.conductResearch(query, 3, sessionId!);
        setResearchResults(res);
        setIsShowingSavedResults(false);
      }
    } catch (e: any) {
      setError(e.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-teal-50">
      {/* Navigation */}
      <nav className="border-b border-amber-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/home" className="flex items-center space-x-2">
              <ArrowLeft className="w-5 h-5 text-gray-600" />
              <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">ARIA</span>
            </Link>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={() => setShowHistory(true)}>
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSaved(true)}
                className="flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Saved</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>
      {/* Fixed Recent Searches Sidebar */}
      <div className="fixed top-16 left-0 h-[calc(100vh-4rem)] w-72 bg-white border-r border-amber-100 shadow-sm z-30 hidden lg:flex flex-col">
        <div className="p-4 flex-1 overflow-y-auto max-h-[calc(100vh-6rem)]">
          <div className="flex items-center text-lg font-semibold mb-4">
            <History className="w-5 h-5 mr-2 text-teal-600" />
            Recent Searches
          </div>
          {recentSearches.length > 0 ? (
            Object.entries(groupSearches(recentSearches.slice(0, 30))).map(([label, items]) => (
              <div key={label}>
                <button
                  className="flex items-center text-xs font-semibold text-teal-700 mb-1 mt-2 focus:outline-none"
                  onClick={() => setExpandedSections(prev => ({ ...prev, [label]: !prev[label] }))}
                  type="button"
                >
                  {expandedSections[label] !== false ? (
                    <ChevronDown className="w-4 h-4 mr-1 transition-transform" style={{ transform: 'rotate(0deg)' }} />
                  ) : (
                    <ChevronRight className="w-4 h-4 mr-1 transition-transform" style={{ transform: 'rotate(0deg)' }} />
                  )}
                  {label}
                </button>
                {expandedSections[label] !== false && (
                  <div>
                    {items.map((item, idx) => (
                      <button
                        key={item.query + item.timestamp}
                        className="w-full text-left px-3 py-2 rounded hover:bg-teal-50 transition truncate border border-teal-100 mb-1"
                        onClick={() => handleSearchHistoryClick(item.query)}
                        title={item.query}
                      >
                        <Search className="w-4 h-4 mr-2 inline-block text-teal-600" />
                        <span className="align-middle">{item.query}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center text-gray-400 text-sm py-6">
              <svg width="56" height="56" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="28" cy="28" r="28" fill="#99f6e4" fillOpacity="0.18" />
                <rect x="16" y="24" width="24" height="12" rx="4" fill="#2dd4bf" fillOpacity="0.18" />
                <rect x="20" y="28" width="16" height="4" rx="2" fill="#14b8a6" fillOpacity="0.25" />
                <circle cx="28" cy="32" r="2" fill="#2dd4bf" />
              </svg>
              <span className="mt-2">No recent searches</span>
            </div>
          )}
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:ml-72">
        <div className="grid grid-cols-1 gap-8">
          {/* Main Content (no sidebar column) */}
          <div className="lg:col-span-4">
            {/* Ask ARIA anything label */}
            <div className="mb-2">
              <span className="text-lg font-semibold text-teal-700">Ask ARIA anything!</span>
            </div>
            {/* Input Bar */}
            <form onSubmit={handleSend} className="flex gap-4 mb-8">
              <Input
                placeholder="Type your question..."
                value={input}
                onChange={e => setInput(e.target.value)}
                className="flex-1 h-12 text-lg border-teal-200 focus:border-teal-400"
                disabled={isLoading}
              />
              <Button
                type="submit"
                disabled={isLoading || !input.trim() || !sessionId}
                className="h-12 px-6 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </form>
            {/* Topic and Chat with ARIA Button Row (just above summary/results) */}
            {(researchResults || (savedResearchResults && isShowingSavedResults)) && !isLoading && (
              <div className="mb-4 flex items-center justify-between">
                {/* Topic Display (left) */}
                <div className="flex-1">
                  <span className="text-lg font-semibold text-teal-700">
                    {researchResults?.topic || input || ''}
                  </span>
                </div>
                {/* Chat with ARIA Button (right) */}
                <Button
                  variant="outline"
                  className="text-teal-700 border-teal-400 hover:bg-teal-50"
                  onClick={() => setShowChat((prev) => !prev)}
                >
                  <MessageSquare className="w-5 h-5 mr-2 text-teal-600" />
                  {showChat ? 'Topic' : 'Chat with ARIA'}
                </Button>
              </div>
            )}
            {/* Loading State */}
            {isLoading && (
              <Card className="border-amber-100 mb-8">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Brain className="w-8 h-8 text-teal-600 animate-pulse" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Processing your request...</h3>
                  <p className="text-gray-600">ARIA is gathering information and generating insights</p>
                </CardContent>
              </Card>
            )}
            {/* Chat Section (now toggled by button) */}
            {(researchResults || (savedResearchResults && isShowingSavedResults)) && !isLoading && showChat && (
              <Card className="border-teal-200 mb-8">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-teal-600" />
                    Chat about this Search
                  </CardTitle>
                  {!showResearchTabs && (
                    <Button size="sm" variant="outline" onClick={() => setShowResearchTabs(true)} className="text-teal-700 border-teal-400 hover:bg-teal-50">
                      <ArrowLeft className="w-4 h-4 mr-1 text-teal-700" /> Topic
                    </Button>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col gap-4 max-h-[500px] overflow-y-auto mb-4 bg-green-50 rounded p-3">
                    {chatMessages.length === 0 && (
                      <div className="text-gray-400 text-center">Start a conversation about this search query!</div>
                    )}
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}> 
                        <div className={`relative rounded-lg max-w-xl ${msg.role === 'user' ? 'bg-teal-200 text-right px-4 py-2 text-base' : 'bg-white text-left border border-green-200 px-5 py-3 text-base md:text-lg'}`}
                        >
                          {msg.role === 'ai'
                            ? msg.content
                                .split(/\n\n+/)
                                .map((para, i) => {
                                  const clean = para
                                    .replace(/^#+\s*/, '')
                                    .replace(/^[-*]\s*/, '')
                                    .replace(/[*_]{1,2}/g, '')
                                    .trim();
                                  return clean ? <p key={i} className="mb-2 last:mb-0">{clean}</p> : null;
                                })
                            : <span>{msg.content}</span>}
                          {copiedMsgIdx === idx && (
                            <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                              Copied!
                            </div>
                          )}
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(msg.content);
                              setCopiedMsgIdx(idx);
                              setTimeout(() => setCopiedMsgIdx(null), 2000);
                            }}
                            className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-100 rounded"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                    {isChatLoading && (
                      <div className="flex justify-start">
                        <div className="bg-white border border-green-200 rounded-lg px-5 py-3 text-base text-gray-500 font-medium">
                          ARIA is typing...
                        </div>
                      </div>
                    )}
                  </div>
                  <form onSubmit={handleChatSend} className="flex gap-2">
                    <Input
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask ARIA about this research..."
                      className="flex-1"
                      disabled={isChatLoading}
                    />
                    <Button type="submit" disabled={isChatLoading || !chatInput.trim()}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}
            {/* Results Section (tabs) - only show if chat is not open */}
            {(researchResults || (savedResearchResults && isShowingSavedResults)) && !isLoading && !showChat && (
              <div className="mb-8">
                {(() => {
                  const results = researchResults || savedResearchResults;
                  return (
                    <Tabs value={activeTab} onValueChange={setActiveTab} defaultValue="summary" className="w-full">
                      <div className="flex items-center mb-4">
                        <TabsList className="flex-1">
                          <TabsTrigger value="summary">
                            <FileText className="w-5 h-5 mr-2 text-teal-600" /> Summary
                          </TabsTrigger>
                          <TabsTrigger value="insights">
                            <Lightbulb className="w-5 h-5 mr-2 text-amber-600" /> Key Insights
                          </TabsTrigger>
                          <TabsTrigger value="reflecting">
                            <MessageSquare className="w-5 h-5 mr-2 text-purple-600" /> Reflecting Questions
                          </TabsTrigger>
                          <TabsTrigger value="suggestions">
                            <BookOpen className="w-5 h-5 mr-2 text-green-600" /> Suggestions
                          </TabsTrigger>
                          <TabsTrigger value="notes">
                            <BookOpen className="w-5 h-5 mr-2 text-yellow-600" /> Notes
                          </TabsTrigger>
                          <TabsTrigger value="references">
                            <LinkIcon className="w-5 h-5 mr-2 text-cyan-600" /> References
                          </TabsTrigger>
                          {/* Place Report tab after References */}
                          <TabsTrigger value="report">
                            <FileText className="w-5 h-5 mr-2 text-blue-600" /> Report
                          </TabsTrigger>
                        </TabsList>
                      </div>
                        <TabsContent value="summary">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <FileText className="w-5 h-5 text-teal-600" />
                                Summary
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(summaryRef)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('Summary', results.summary)}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div ref={summaryRef} className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {results.summary
                                  .split(/\n\n+/)
                                  .map((para, idx) => {
                                    const clean = para
                                      .replace(/^#+\s*/, '')
                                      .replace(/^[-*]\s*/, '')
                                      .replace(/[*_]{1,2}/g, '')
                                      .trim();
                                    return clean ? <p key={idx} className="mb-4 last:mb-0">{clean}</p> : null;
                                  })}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="insights">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <Lightbulb className="w-5 h-5 text-teal-600" />
                                Key Insights
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(insightsRef)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('KeyInsights', results.key_insights)}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div ref={insightsRef} className="space-y-4">
                                {(() => {
                                  // Group lines: heading (numbered or bold) + following lines (dashed/sub-points) as one paragraph
                                  const lines = results.key_insights.split('\n');
                                  const groups = [];
                                  let current = '';
                                  for (let i = 0; i < lines.length; i++) {
                                    let line = lines[i].replace(/^#+\s*/, '').replace(/^[-*]\s*/, '').replace(/[*_]{1,2}/g, '').trim();
                                    if (!line) continue;
                                    // If line looks like a heading (starts with number and dot, or is bold), start new group
                                    if (/^\d+\./.test(line) || (/^[A-Z]/.test(line) && !current)) {
                                      if (current) groups.push(current.trim());
                                      current = line;
                                    } else {
                                      // Otherwise, append to current group
                                      current += ' ' + line;
                                    }
                                  }
                                  if (current) groups.push(current.trim());
                                  return groups.map((para, idx) => (
                                    <div key={idx} className="bg-teal-50 rounded-lg px-4 py-3 text-gray-800 shadow-sm">
                                      {para}
                                    </div>
                                  ));
                                })()}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="reflecting">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <MessageSquare className="w-5 h-5 text-purple-600" />
                                Reflecting Questions
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleSave('ReflectingQuestions', results.reflecting_questions.join('\n'))}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                {results.reflecting_questions && results.reflecting_questions.length > 0 ? (
                                  results.reflecting_questions.map((q, idx) => (
                                    <button
                                      key={idx}
                                      className="block w-full text-left p-3 rounded-lg border border-purple-100 bg-purple-50 hover:bg-purple-100 transition cursor-pointer text-gray-800"
                                      onClick={() => {
                                        setInput(q);
                                        setTimeout(() => {
                                          document.querySelector('form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                                        }, 0);
                                      }}
                                    >
                                      {q}
                                    </button>
                                  ))
                                ) : (
                                  <div className="text-gray-500">No reflecting questions generated.</div>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="suggestions">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <BookOpen className="w-5 h-5 text-green-600" />
                                Suggestions
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(questionsRef)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('Suggestions', results.suggestions.join('\n'))}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div ref={questionsRef} className="space-y-3">
                                {results.suggestions.slice(0, 5).map((suggestion, index) => (
                                  <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                                    <MessageSquare className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                                    <p className="text-gray-700">{suggestion}</p>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="notes">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <BookOpen className="w-5 h-5 text-yellow-600" />
                                Notes
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(notesRef)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('Notes', results.notes)}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div ref={notesRef} className="space-y-4">
                                {results.notes
                                  .split(/\n\n+/)
                                  .map((para, idx) => {
                                    const clean = para
                                      .replace(/^#+\s*/, '')
                                      .replace(/^[-*]\s*/, '')
                                      .replace(/[*_]{1,2}/g, '')
                                      .trim();
                                    return clean ? (
                                      <div key={idx} className="bg-amber-50 rounded-lg px-4 py-3 text-gray-800 shadow-sm">
                                        {clean}
                                      </div>
                                    ) : null;
                                  })}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="references">
                          <Card className="border-amber-100">
                            <CardHeader className="flex flex-row items-center justify-between">
                              <CardTitle className="flex items-center gap-2">
                                <LinkIcon className="w-5 h-5 text-cyan-600" />
                                Reference Links
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(referencesRef)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('References', results.sources.map(s => s.link).join('\n'))}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div ref={referencesRef} className="space-y-3">
                                {results.sources.slice(0, 5).map((source, index) => (
                                  <div key={index} className="flex items-center gap-2">
                                    <LinkIcon className="w-4 h-4 text-cyan-400" />
                                    <a
                                      href={source.link}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-cyan-600 hover:text-cyan-800 underline break-all"
                                    >
                                      {source.link}
                                    </a>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                        <TabsContent value="report">
                          <Card className="border-blue-100">
                            <CardHeader>
                              <CardTitle className="flex items-center gap-2">
                                <FileText className="w-5 h-5 text-blue-600" />
                                Report
                              </CardTitle>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" onClick={() => handleCopy(results.report)}>Copy</Button>
                                <Button size="sm" variant="outline" onClick={() => handleSave('Report', results.report)}>Save</Button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {results.report
                                  ? results.report.split(/\n\n+/).map((para, idx) => {
                                      // Highlight headings in blue and remove hashes
                                      const headingMatch = para.match(/^\s*#+\s*(.+)$/);
                                      if (headingMatch) {
                                        return (
                                          <div key={idx} className="mb-4 last:mb-0">
                                            <span className="block font-bold text-blue-700 text-lg">{headingMatch[1].trim()}</span>
                                          </div>
                                        );
                                      }
                                      return <p key={idx} className="mb-4 last:mb-0">{linkify(para.trim())}</p>;
                                    })
                                  : <span className="text-gray-400">No report generated.</span>}
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                      </Tabs>
                    );
                  })()}
                </div>
            )}
            {/* No Results State */}
            {!researchResults && !isLoading && !error && (
              <Card className="border-amber-100">
                <CardContent className="p-8 text-center flex flex-col items-center justify-center">
                  <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" className="mb-4">
                    <circle cx="40" cy="40" r="40" fill="#fef3c7" fillOpacity="0.5" />
                    <rect x="24" y="36" width="32" height="16" rx="6" fill="#2dd4bf" fillOpacity="0.18" />
                    <rect x="32" y="44" width="16" height="4" rx="2" fill="#f59e42" fillOpacity="0.25" />
                    <circle cx="40" cy="52" r="3" fill="#f59e42" />
                  </svg>
                  <h3 className="text-lg font-semibold mb-2">Ready to research?</h3>
                  <p className="text-gray-600">Enter a topic above to start your research journey with ARIA</p>
                </CardContent>
              </Card>
            )}
            {error && <div className="text-red-500 mt-2">{error}</div>}
          </div>
        </div>
      </div>
      {/* History Modal */}
      <Dialog open={showHistory} onOpenChange={setShowHistory}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Search History</DialogTitle>
            <DialogClose asChild>
              <Button variant="ghost" className="absolute top-2 right-2">Close</Button>
            </DialogClose>
          </DialogHeader>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {recentSearches.length > 0 ? (
              recentSearches.map((search, idx) => (
                <button
                  key={idx}
                  className="w-full text-left px-3 py-2 rounded hover:bg-teal-50 transition truncate border border-teal-100"
                  onClick={() => {
                    handleSearchHistoryClick(search.query);
                    setShowHistory(false);
                  }}
                  title={search.query}
                >
                  <Search className="w-4 h-4 mr-2 inline-block text-teal-600" />
                  <span className="align-middle">{search.query}</span>
                </button>
              ))
            ) : (
              <div className="text-gray-400 text-sm">No search history</div>
            )}
          </div>
        </DialogContent>
      </Dialog>
      {/* Saved Modal */}
      <Dialog open={showSaved} onOpenChange={setShowSaved}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Saved Research</DialogTitle>
            <DialogClose asChild>
              <Button variant="ghost" className="absolute top-2 right-2">Close</Button>
            </DialogClose>
          </DialogHeader>
          <div className="space-y-6 max-h-[70vh] overflow-y-auto">
            {Object.keys(savedData).length === 0 && (
              <div className="text-gray-400 text-center">No saved research yet.</div>
            )}
            {Object.entries(savedData).map(([query, sections]: any, idx) => (
              <div key={idx} className="bg-amber-50 rounded-lg p-4 shadow">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold text-lg text-teal-700">{query}</div>
                  <button
                    className="text-red-500 hover:text-red-700 p-1 rounded"
                    title="Delete saved item"
                    onClick={() => handleDeleteSaved(query)}
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
                <div className="space-y-2">
                  {Object.entries(sections).map(([sectionName, sectionData]: [string, any]) => (
                    <div key={sectionName} className="text-sm mb-2">
                      <span className="font-medium text-blue-600">{sectionName}:</span>
                      <div className="text-gray-600 whitespace-pre-line break-words">{sectionData.content}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatNew; 