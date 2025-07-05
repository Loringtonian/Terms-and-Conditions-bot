'use client';

import { useState, useRef, useEffect } from 'react';
import { Search, FileText, Gavel, Scale, Shield, Clock, AlertTriangle, Check, X } from 'lucide-react';

// Types
type Service = {
  id: string;
  name: string;
  displayName: string;
  category: string;
  icon: string;
  riskLevel: 'low' | 'medium' | 'high';
  lastAnalyzed: string;
};

type AnalysisResult = {
  id: string;
  serviceName: string;
  score: number;
  summary: string;
  concerns: Concern[];
  recommendations: string[];
  red_flags?: string[];
  user_friendliness_score?: number;
  data_collection_score?: number;
  legal_complexity_score?: number;
  total_high_severity_concerns?: number;
};

type Concern = {
  clause: string;
  severity: 'high' | 'medium' | 'low';
  explanation: string;
  quote?: string;
  clarity_analysis?: {
    unclear_terms: UnclearTerm[];
    practical_meaning: string;
    user_action_needed: string;
    severity_justification: string;
  };
};

type UnclearTerm = {
  term: string;
  explanation: string;
  user_impact: string;
  questions_to_ask: string[];
};

// API configuration
const API_BASE_URL = 'http://localhost:5001';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestedService, setRequestedService] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [services, setServices] = useState<Service[]>([]);
  const [servicesLoading, setServicesLoading] = useState(true);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Load services on component mount
  useEffect(() => {
    const loadServices = async () => {
      try {
        setServicesLoading(true);
        const response = await fetch(`${API_BASE_URL}/services`);
        const data = await response.json();
        setServices(data.services || []);
      } catch (error) {
        console.error('Error loading services:', error);
      } finally {
        setServicesLoading(false);
      }
    };
    
    loadServices();
  }, []);

  // Filter services based on search query and category
  const filteredServices = services.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        service.displayName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Handle service selection
  const handleServiceSelect = async (service: Service) => {
    setSelectedService(service);
    setSearchQuery(service.displayName);
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/analysis/${service.id}`);
      const analysisData = await response.json();
      setAnalysis(analysisData);
    } catch (error) {
      console.error('Error loading analysis:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle paste analysis
  const handlePasteAnalyze = () => {
    if (!pastedText.trim()) return;
    setIsLoading(true);
    setShowPasteModal(false);
    // In a real app, this would send the pasted text to your backend for analysis
    setTimeout(() => {
      setAnalysis({
        ...MOCK_ANALYSIS,
        serviceName: 'Pasted Terms',
        score: 6.0,
        summary: 'Analysis of pasted terms and conditions.'
      });
      setIsLoading(false);
    }, 1500);
  };

  // Handle service request
  const handleRequestService = () => {
    if (!requestedService.trim()) return;
    // In a real app, this would send a request to your backend
    alert(`Request submitted for: ${requestedService}`);
    setShowRequestModal(false);
    setRequestedService('');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          searchInputRef.current && !searchInputRef.current.contains(event.target as Node)) {
        setSearchQuery(selectedService?.displayName || '');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [selectedService]);

  // Categories for filtering
  const categories = [
    { id: 'all', name: 'All Services', icon: '🌐' },
    { id: 'Social', name: 'Social Media', icon: '💬' },
    { id: 'Entertainment', name: 'Entertainment', icon: '🎮' },
    { id: 'Productivity', name: 'Productivity', icon: '📊' },
    { id: 'Finance', name: 'Finance', icon: '💰' },
    { id: 'Shopping', name: 'Shopping', icon: '🛒' },
  ];

  // Get risk level color and emoji
  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const getSeverityEmoji = (severity: string) => {
    switch (severity) {
      case 'high': return '🚨';
      case 'medium': return '⚠️';
      case 'low': return '🟡';
      default: return '❓';
    }
  };

  const getScoreEmoji = (score: number) => {
    if (score >= 8) return '✅';
    if (score >= 6) return '⚠️';
    return '🚨';
  };

  const getOverallThreatLevel = (analysis: AnalysisResult) => {
    const highSeverityCount = analysis.total_high_severity_concerns || 0;
    if (highSeverityCount >= 3) return { level: 'Critical', emoji: '🚨', color: 'text-red-600' };
    if (highSeverityCount >= 2) return { level: 'High Risk', emoji: '⚠️', color: 'text-orange-600' };
    if (highSeverityCount >= 1) return { level: 'Moderate Risk', emoji: '⚠️', color: 'text-yellow-600' };
    return { level: 'Low Risk', emoji: '✅', color: 'text-green-600' };
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Elegant Header */}
      <header className="w-full border-b border-slate-200/60 dark:border-slate-800/60 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-8 py-16 text-center">
          <div className="flex items-center justify-center space-x-4 mb-6">
            <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded-2xl shadow-lg">
              <Gavel className="h-8 w-8 text-slate-700 dark:text-slate-300" />
            </div>
            <h1 className="text-4xl md:text-5xl font-extralight tracking-tight text-slate-900 dark:text-white">
              Terms & Conditions <span className="italic font-light text-slate-600 dark:text-slate-400">eh</span>
            </h1>
          </div>
          <p className="text-slate-600 dark:text-slate-400 text-lg font-light max-w-2xl mx-auto leading-relaxed">
            Decode the legal complexity. Understand what you're really agreeing to.
          </p>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="w-full flex flex-col items-center px-8 py-16">
        {/* Hero Search Section */}
        <div className="w-full max-w-3xl mb-16">
          <div className="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl rounded-3xl border border-slate-200/50 dark:border-slate-800/50 shadow-2xl shadow-slate-200/20 dark:shadow-slate-950/40 p-12">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-light text-slate-900 dark:text-white mb-3">
                Analyze Any Service
              </h2>
              <p className="text-slate-600 dark:text-slate-400 font-light">
                Search for popular apps and services to see their privacy risks
              </p>
            </div>
            
            <div className="relative" ref={dropdownRef}>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                  <Search className="h-6 w-6 text-slate-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-16 pr-6 py-6 border-2 border-slate-200/60 dark:border-slate-700/60 rounded-2xl bg-white/90 dark:bg-slate-800/90 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-4 focus:ring-slate-200/40 dark:focus:ring-slate-700/40 focus:border-slate-300 dark:focus:border-slate-600 text-lg font-light shadow-lg transition-all duration-300 hover:shadow-xl"
                  placeholder="Netflix, Spotify, Instagram, Facebook..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setSelectedService(null);
                    setAnalysis(null);
                  }}
                  onFocus={() => setSelectedService(null)}
                  ref={searchInputRef}
                />
              </div>

              {/* Elegant Search Results Dropdown */}
              {searchQuery && !selectedService && !servicesLoading && filteredServices.length > 0 && (
                <div className="absolute z-20 mt-4 w-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl shadow-2xl rounded-2xl border border-slate-200/60 dark:border-slate-800/60 max-h-96 overflow-auto">
                  <ul className="py-3">
                    {filteredServices.map((service) => (
                      <li key={service.id}>
                        <button
                          onClick={() => handleServiceSelect(service)}
                          className="w-full text-left px-6 py-4 hover:bg-slate-50/80 dark:hover:bg-slate-800/80 flex items-center border-b border-slate-100/60 dark:border-slate-800/60 last:border-b-0 transition-all duration-200 group"
                        >
                          <span className="text-2xl mr-4 group-hover:scale-110 transition-transform duration-200">{service.icon}</span>
                          <div>
                            <div className="font-medium text-slate-900 dark:text-white text-base">
                              {service.displayName}
                            </div>
                            <div className="text-sm text-slate-500 dark:text-slate-400 font-light">
                              {service.category}
                            </div>
                          </div>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Loading services */}
              {servicesLoading && (
                <div className="absolute z-20 mt-4 w-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl shadow-2xl rounded-2xl border border-slate-200/60 dark:border-slate-800/60 p-6">
                  <div className="text-center text-slate-500 dark:text-slate-400 font-light">
                    Loading services...
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Elegant Secondary Actions */}
        <div className="w-full max-w-lg mb-12">
          <div className="flex items-center justify-center space-x-6">
            <button
              onClick={() => setShowPasteModal(true)}
              className="group relative inline-flex items-center px-8 py-4 bg-white/80 dark:bg-slate-800/80 border-2 border-slate-200/60 dark:border-slate-700/60 rounded-2xl text-slate-700 dark:text-slate-300 font-medium hover:bg-white dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 focus:outline-none focus:ring-4 focus:ring-slate-200/40 dark:focus:ring-slate-700/40 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 backdrop-blur-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-slate-100/20 to-transparent dark:from-slate-700/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <FileText className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
              <span className="relative">Paste Terms</span>
            </button>
            <button
              onClick={() => setShowRequestModal(true)}
              className="group relative inline-flex items-center px-8 py-4 bg-slate-900/90 dark:bg-slate-700/90 border-2 border-slate-900 dark:border-slate-600 rounded-2xl text-white font-medium hover:bg-slate-800 dark:hover:bg-slate-600 focus:outline-none focus:ring-4 focus:ring-slate-900/20 dark:focus:ring-slate-600/40 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 backdrop-blur-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <Scale className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
              <span className="relative">Request Analysis</span>
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Analyzing terms and conditions...</p>
          </div>
        )}

        {/* Analysis Results */}
        {analysis && !isLoading && (
          <div className="w-full max-w-4xl space-y-6">
            {/* Overview Card */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-800 overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      Analysis for {analysis.serviceName}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Last analyzed: {formatDate(new Date().toISOString())}
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      analysis.score >= 7 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                      analysis.score >= 4 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500' :
                      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }`}>
                      {getScoreEmoji(analysis.score)} {analysis.score}/10
                    </div>
                  </div>
                </div>
              </div>

              {/* Threat Level Alert */}
              {(() => {
                const threatLevel = getOverallThreatLevel(analysis);
                return (
                  <div className={`px-6 py-4 border-b border-gray-200 dark:border-gray-800 ${
                    threatLevel.level === 'Critical' ? 'bg-red-50 dark:bg-red-900/20' :
                    threatLevel.level === 'High Risk' ? 'bg-orange-50 dark:bg-orange-900/20' :
                    threatLevel.level === 'Moderate Risk' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
                    'bg-green-50 dark:bg-green-900/20'
                  }`}>
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{threatLevel.emoji}</span>
                      <div>
                        <h4 className={`font-medium ${threatLevel.color}`}>
                          {threatLevel.level}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {analysis.total_high_severity_concerns} high-severity concerns identified
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Quick Stats */}
              <div className="px-6 py-4 grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analysis.user_friendliness_score || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">User Friendliness</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analysis.data_collection_score || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Data Protection</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analysis.legal_complexity_score || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Legal Clarity</div>
                </div>
              </div>
            </div>

            {/* Red Flags */}
            {analysis.red_flags && analysis.red_flags.length > 0 && (
              <div className="bg-white dark:bg-gray-900 rounded-lg border border-red-100 dark:border-red-900/30 overflow-hidden">
                <div className="px-6 py-4 bg-red-50 dark:bg-red-900/10 border-b border-red-100 dark:border-red-900/30">
                  <h4 className="text-sm font-medium text-red-700 dark:text-red-400 uppercase tracking-wider flex items-center">
                    🚩 Major Red Flags
                  </h4>
                </div>
                <div className="p-6">
                  <ul className="space-y-3">
                    {analysis.red_flags.map((flag, index) => (
                      <li key={index} className="flex items-start border-b border-gray-50 dark:border-gray-800 last:border-b-0 pb-2 last:pb-0">
                        <span className="text-red-500 mr-3 mt-0.5">🚩</span>
                        <span className="text-gray-700 dark:text-gray-300 font-medium">{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Summary */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-800 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800/30 border-b border-gray-100 dark:border-gray-800">
                <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  📋 Executive Summary
                </h4>
              </div>
              <div className="p-6">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{analysis.summary}</p>
              </div>
            </div>

            {/* Detailed Concerns */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-800 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800/30 border-b border-gray-100 dark:border-gray-800">
                <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  🔍 Detailed Analysis
                </h4>
              </div>
              <div className="divide-y divide-gray-50 dark:divide-gray-800">
                {analysis.concerns.map((concern, index) => (
                  <div key={index} className="p-6">
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl flex-shrink-0 mt-1">
                        {getSeverityEmoji(concern.severity)}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h5 className="font-medium text-gray-900 dark:text-white">
                            {concern.clause}
                          </h5>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskLevelColor(concern.severity)}`}>
                            {concern.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
                          {concern.explanation}
                        </p>
                        {concern.quote && (
                          <blockquote className="border-l-2 border-gray-200 dark:border-gray-700 pl-4 italic text-gray-600 dark:text-gray-400 text-sm bg-gray-50 dark:bg-gray-800/30 p-3 rounded-r">
                            "{concern.quote}"
                          </blockquote>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-green-100 dark:border-green-900/30 overflow-hidden">
              <div className="px-6 py-4 bg-green-50 dark:bg-green-900/10 border-b border-green-100 dark:border-green-900/30">
                <h4 className="text-sm font-medium text-green-700 dark:text-green-400 uppercase tracking-wider">
                  💡 Recommendations
                </h4>
              </div>
              <div className="p-6">
                <ul className="space-y-3">
                  {analysis.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start border-b border-gray-50 dark:border-gray-800 last:border-b-0 pb-2 last:pb-0">
                      <span className="text-green-500 mr-3 mt-0.5 text-lg">✅</span>
                      <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Paste Terms Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-900 dark:text-white">Paste Terms & Conditions</h3>
                <button 
                  onClick={() => setShowPasteModal(false)}
                  className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                >
                  <span className="sr-only">Close</span>
                  <X className="h-6 w-6" />
                </button>
              </div>
              <div className="mt-4">
                <label htmlFor="pasted-text" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste the terms and conditions text below
                </label>
                <textarea
                  id="pasted-text"
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Paste the full text of the terms and conditions here..."
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                />
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  onClick={() => setShowPasteModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!pastedText.trim()}
                  onClick={handlePasteAnalyze}
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Request Analysis Modal */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-900 dark:text-white">Request Analysis</h3>
                <button 
                  onClick={() => setShowRequestModal(false)}
                  className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                >
                  <span className="sr-only">Close</span>
                  <X className="h-6 w-6" />
                </button>
              </div>
              <div className="mt-4">
                <label htmlFor="service-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Which service's terms would you like us to analyze?
                </label>
                <input
                  type="text"
                  id="service-name"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Facebook, Google, etc."
                  value={requestedService}
                  onChange={(e) => setRequestedService(e.target.value)}
                />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  We'll analyze the terms and notify you when they're ready.
                </p>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  onClick={() => setShowRequestModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!requestedService.trim()}
                  onClick={handleRequestService}
                >
                  Request
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
