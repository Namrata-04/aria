import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Search, Brain, FileText, BookOpen, MessageSquare, History, CircleUser } from 'lucide-react';
import LaptopUI from '../components/LaptopUI';

const Index = () => {
  const [showAbout, setShowAbout] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  // Check login state on mount
  useEffect(() => {
    setLoggedIn(!!localStorage.getItem('aria_logged_in'));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('aria_logged_in');
    window.location.href = '/login';
  };

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-teal-50">
      <nav className="border-b border-amber-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">ARIA</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <button 
                onClick={() => scrollToSection('about')}
                className="text-gray-600 hover:text-teal-600 font-medium transition-colors"
              >
                About Us
              </button>
              <button 
                onClick={() => scrollToSection('features')}
                className="text-gray-600 hover:text-teal-600 font-medium transition-colors"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('faqs')}
                className="text-gray-600 hover:text-teal-600 font-medium transition-colors"
              >
                FAQs
              </button>
            </div>
            
            <div className="flex items-center space-x-4 relative">
              <Link to="/chat">
                <Button className="bg-gradient-to-r from-teal-500 to-teal-600 text-white hover:from-teal-600 hover:to-teal-700 px-4 py-2 text-base font-semibold shadow">
                  Get Started
                </Button>
              </Link>
              {loggedIn ? (
                <div className="relative">
                  <button
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center border border-teal-200 focus:outline-none shadow"
                    onClick={() => setShowProfileMenu((v) => !v)}
                    aria-label="Profile menu"
                  >
                    <CircleUser className="w-7 h-7 text-white" />
                  </button>
                  {showProfileMenu && (
                    <div className="absolute right-0 mt-2 w-40 bg-white border border-teal-100 rounded-lg shadow-lg z-50">
                      <button
                        className="w-full text-left px-4 py-2 text-gray-700 hover:bg-teal-50 rounded-t-lg"
                        onClick={handleLogout}
                      >
                        Log out
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <Link to="/chat">
                    <Button className="bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700">
                      Start Research
                    </Button>
                  </Link>
                  <Link to="/chat-mongodb">
                    <Button variant="outline" className="border-green-200 text-green-700 hover:bg-green-50">
                      Storage Version
                    </Button>
                  </Link>
                  <Link to="/login">
                    <Button variant="outline" className="border-teal-200 text-teal-700 hover:bg-teal-50">Login</Button>
                  </Link>
                  <Link to="/signup">
                    <Button variant="outline" className="border-amber-200 text-amber-700 hover:bg-amber-50">Sign Up</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-10 left-10 w-72 h-72 bg-teal-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
            <div className="absolute top-10 right-10 w-72 h-72 bg-amber-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-2000"></div>
            <div className="absolute bottom-10 left-1/2 w-72 h-72 bg-teal-100 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-4000"></div>
          </div>
          
          <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6">
            Your Personal
            <span className="block bg-gradient-to-r from-teal-600 to-teal-800 bg-clip-text text-transparent">
              Research Assistant
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            ARIA transforms your research with AI-powered summaries, insights, and personalized reports. 
            Ask any question and get comprehensive answers with references and follow-up suggestions.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/chat">
              <Button size="lg" className="bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 px-8 py-4 text-lg">
                <Search className="w-5 h-5 mr-2" />
                Start Researching
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-teal-200 text-teal-700 hover:bg-teal-50 px-8 py-4 text-lg" onClick={() => scrollToSection('faqs')}>
              Learn More
            </Button>
          </div>
        </div>
      </section>

      {/* Laptop Chat Mockup */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <LaptopUI />
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="px-4 sm:px-6 lg:px-8 py-20 bg-gradient-to-r from-teal-50 to-amber-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">About ARIA</h2>
          <p className="text-lg text-gray-600 mb-8 leading-relaxed">
            ARIA (Adaptive Research Intelligence Assistant) is your personal AI-powered research companion designed to revolutionize how you discover, understand, and organize information. Built with cutting-edge technology, ARIA combines the power of advanced language models with real-time web search capabilities to provide you with comprehensive, accurate, and contextual research results.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left">
            <div className="bg-white/60 backdrop-blur-sm border border-teal-100 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-teal-800 mb-3">Our Mission</h3>
              <p className="text-gray-600">
                To democratize access to intelligent research tools, making complex information accessible and actionable for students, professionals, and curious minds worldwide.
              </p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm border border-teal-100 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-teal-800 mb-3">Our Vision</h3>
              <p className="text-gray-600">
                A world where anyone can instantly access, understand, and build upon the collective knowledge of humanity through intelligent AI assistance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything you need for intelligent research
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              ARIA provides comprehensive research tools powered by advanced AI to help you discover, understand, and organize information.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <FileText className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Smart Summaries</h3>
                <p className="text-gray-600">Get concise, comprehensive summaries of complex topics with key points highlighted.</p>
              </CardContent>
            </Card>
            
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <Brain className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Key Insights</h3>
                <p className="text-gray-600">Discover important patterns, trends, and insights from your research queries.</p>
              </CardContent>
            </Card>
            
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <BookOpen className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Organized Notes</h3>
                <p className="text-gray-600">Automatically organized notes with references for easy review and citation.</p>
              </CardContent>
            </Card>
            
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <MessageSquare className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Reflecting Questions</h3>
                <p className="text-gray-600">Get thought-provoking questions to deepen your understanding of any topic.</p>
              </CardContent>
            </Card>
            
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <History className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Search History</h3>
                <p className="text-gray-600">Keep track of all your research with organized search history and quick access.</p>
              </CardContent>
            </Card>
            
            <Card className="group hover:shadow-lg transition-all duration-300 border-amber-100 hover:border-teal-200">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                  <Search className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Math & Algorithms</h3>
                <p className="text-gray-600">Solve complex mathematical problems and understand algorithms with detailed explanations.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-20 bg-gradient-to-r from-teal-600 to-teal-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to revolutionize your research?
          </h2>
          <p className="text-teal-100 text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of researchers, students, and professionals who use ARIA to accelerate their learning and discovery.
          </p>
          <Link to="/chat">
            <Button size="lg" className="bg-white text-teal-600 hover:bg-gray-50 px-8 py-4 text-lg font-semibold">
              Start Your Research Journey
            </Button>
          </Link>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faqs" className="px-4 sm:px-6 lg:px-8 py-20 bg-gradient-to-br from-amber-50 via-white to-white border-t border-amber-100">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-teal-800 mb-6">Frequently Asked Questions</h2>
          <p className="text-lg text-gray-700 mb-10">Answers to some of the most common questions about ARIA.</p>
        </div>
        <div className="max-w-3xl mx-auto">
          <div className="space-y-4">
            {/* FAQ 1 */}
            <details className="group border border-teal-100 rounded-lg p-4 bg-teal-50 shadow-sm">
              <summary className="flex items-center justify-between cursor-pointer text-base font-normal text-gray-800 group-open:text-teal-700">
                What is ARIA and how does it work?
                <span className="ml-2 text-teal-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 text-gray-700 text-left">
                ARIA (Adaptive Research Intelligence Assistant) is an AI-powered tool that helps you research any topic by providing summaries, insights, citations, and more. Just ask a question, and ARIA will analyze sources to give you comprehensive answers.
              </div>
            </details>
            {/* FAQ 2 */}
            <details className="group border border-teal-100 rounded-lg p-4 bg-teal-50 shadow-sm">
              <summary className="flex items-center justify-between cursor-pointer text-base font-normal text-gray-800 group-open:text-teal-700">
                Is my data private and secure?
                <span className="ml-2 text-teal-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 text-gray-700 text-left">
                Yes! Your research data is stored securely and never shared with third parties. We use best practices to ensure your privacy and data protection.
              </div>
            </details>
            {/* FAQ 3 */}
            <details className="group border border-teal-100 rounded-lg p-4 bg-teal-50 shadow-sm">
              <summary className="flex items-center justify-between cursor-pointer text-base font-normal text-gray-800 group-open:text-teal-700">
                Can I use ARIA for academic research?
                <span className="ml-2 text-teal-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 text-gray-700 text-left">
                Absolutely! ARIA is designed for students, researchers, and professionals. It provides citations and references to help you with academic work.
              </div>
            </details>
            {/* FAQ 4 */}
            <details className="group border border-teal-100 rounded-lg p-4 bg-teal-50 shadow-sm">
              <summary className="flex items-center justify-between cursor-pointer text-base font-normal text-gray-800 group-open:text-teal-700">
                Is ARIA free to use?
                <span className="ml-2 text-teal-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 text-gray-700 text-left">
                ARIA is currently free to use during our beta period. In the future, we may introduce premium features for advanced research needs.
              </div>
            </details>
            {/* FAQ 5 */}
            <details className="group border border-teal-100 rounded-lg p-4 bg-teal-50 shadow-sm">
              <summary className="flex items-center justify-between cursor-pointer text-base font-normal text-gray-800 group-open:text-teal-700">
                How do I get started with ARIA?
                <span className="ml-2 text-teal-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 text-gray-700 text-left">
                Simply click "Start Researching" at the top of the page, or sign up for an account to save your research and access more features.
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-br from-teal-600 to-teal-800 text-white mt-12 shadow-inner">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo and Name */}
          <div className="flex items-center space-x-3 mb-4 md:mb-0">
            <div className="w-10 h-10 bg-gradient-to-br from-teal-400 to-teal-700 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-wide">ARIA</span>
          </div>
          {/* Navigation Links */}
          <nav className="flex flex-wrap gap-8 text-lg font-medium items-center">
            <a href="#about" className="hover:text-amber-200 transition-colors">About</a>
            <a href="#features" className="hover:text-amber-200 transition-colors">Features</a>
            <a href="#faqs" className="hover:text-amber-200 transition-colors">FAQs</a>
            <a href="mailto:hello@aria.com" className="hover:text-amber-200 transition-colors">Contact</a>
            <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" className="ml-4 hover:text-amber-200 transition-colors" aria-label="GitHub">
              <svg className="w-6 h-6 inline" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.484 2 12.021c0 4.428 2.865 8.184 6.839 9.504.5.092.682-.217.682-.482 0-.237-.009-.868-.014-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.004.07 1.532 1.032 1.532 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.339-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.295 2.748-1.025 2.748-1.025.546 1.378.202 2.397.1 2.65.64.7 1.028 1.595 1.028 2.688 0 3.847-2.338 4.695-4.566 4.944.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.749 0 .267.18.578.688.48C19.138 20.2 22 16.447 22 12.021 22 6.484 17.523 2 12 2z"/></svg>
            </a>
            <a href="mailto:hello@aria.com" className="ml-2 hover:text-amber-200 transition-colors" aria-label="Mail">
              <svg className="w-6 h-6 inline" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 2v.01L12 13 4 6.01V6h16zM4 20v-9.99l7.99 7.99c.39.39 1.02.39 1.41 0L20 10.01V20H4z"/></svg>
            </a>
          </nav>
          {/* Copyright */}
          <div className="text-sm text-teal-100 mt-6 md:mt-0 text-center md:text-right w-full md:w-auto">
            &copy; {new Date().getFullYear()} ARIA. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
