import React, { useState, useEffect } from 'react';
import { Search, FileText, Brain, Zap, Clock, BookOpen } from 'lucide-react';

const LaptopUI = () => {
  const [currentDemo, setCurrentDemo] = useState(0);
  const [typingText, setTypingText] = useState('');
  
  const demoTexts = [
    "Analyzing quantum computing research papers...",
    "Generating insights from climate data studies...",
    "Summarizing machine learning breakthroughs...",
    "Finding patterns in medical research..."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDemo((prev) => (prev + 1) % demoTexts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const text = demoTexts[currentDemo];
    let index = 0;
    setTypingText('');
    
    const typeInterval = setInterval(() => {
      if (index < text.length) {
        setTypingText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(typeInterval);
      }
    }, 50);
    
    return () => clearInterval(typeInterval);
  }, [currentDemo]);

  return (
    <div className="relative">
      {/* Laptop Base */}
      <div className="relative mx-auto" style={{ width: '800px', height: '500px' }}>
        {/* Laptop Screen */}
        <div className="relative bg-gray-900 rounded-t-2xl p-6 shadow-2xl" style={{ width: '800px', height: '450px' }}>
          {/* Screen Bezel */}
          <div className="absolute inset-2 bg-black rounded-xl overflow-hidden">
            {/* Operating System Interface */}
            <div className="h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
              
              {/* Desktop Background with Animated Particles */}
              <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-br from-teal-900/20 to-emerald-900/20"></div>
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute w-1 h-1 bg-teal-400/30 rounded-full animate-pulse"
                    style={{
                      left: `${Math.random() * 100}%`,
                      top: `${Math.random() * 100}%`,
                      animationDelay: `${Math.random() * 2}s`,
                      animationDuration: `${2 + Math.random() * 3}s`
                    }}
                  />
                ))}
              </div>

              {/* AI Assistant Window */}
              <div className="absolute inset-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl overflow-hidden">
                {/* Window Header */}
                <div className="bg-gradient-to-r from-teal-500 to-emerald-600 px-4 py-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-1">
                      <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                    </div>
                    <span className="text-white font-medium">ARIA Research Assistant</span>
                  </div>
                  <Brain className="w-5 h-5 text-white" />
                </div>

                {/* Chat Interface */}
                <div className="p-6 h-full flex flex-col">
                  <div className="flex-1 space-y-4 mb-4">
                    {/* AI Message */}
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <Brain className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-md">
                        <p className="text-sm text-gray-700">
                          I'm ready to help you with your research! Ask me anything about any topic, and I'll provide comprehensive summaries, insights, and citations.
                        </p>
                      </div>
                    </div>

                    {/* User Message */}
                    <div className="flex items-start space-x-3 justify-end">
                      <div className="bg-gradient-to-r from-teal-500 to-emerald-600 rounded-2xl rounded-tr-sm px-4 py-3 max-w-md">
                        <p className="text-sm text-white">
                          Can you help me understand the latest developments in quantum computing?
                        </p>
                      </div>
                      <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-xs text-gray-600">You</span>
                      </div>
                    </div>

                    {/* AI Typing Response */}
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <Brain className="w-4 h-4 text-white animate-pulse" />
                      </div>
                      <div className="bg-gray-50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-md">
                        <p className="text-sm text-gray-700 min-h-[20px]">
                          {typingText}
                          <span className="animate-pulse">|</span>
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Input Area */}
                  <div className="flex items-center space-x-3 bg-gray-50 rounded-xl px-4 py-3">
                    <Search className="w-5 h-5 text-gray-400" />
                    <div className="flex-1 text-sm text-gray-500">Ask me anything about your research...</div>
                    <Zap className="w-5 h-5 text-teal-500" />
                  </div>
                </div>
              </div>

              {/* Floating Feature Icons */}
              <div className="absolute bottom-4 left-4 flex space-x-2">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-white" />
                </div>
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Laptop Base */}
        <div className="bg-gray-300 rounded-b-3xl h-12 relative shadow-lg">
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-16 h-2 bg-gray-400 rounded-full"></div>
        </div>
      </div>
    </div>
  );
};

export default LaptopUI; 