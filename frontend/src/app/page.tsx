'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { Search, FileText, Gavel, Scale, AlertTriangle, CheckCircle } from 'lucide-react';
import PasteTermsModal from '@/components/PasteTermsModal';
import RequestAnalysisModal from '@/components/RequestAnalysisModal';
import TermsViewerModal from '@/components/TermsViewerModal';

interface Service {
  id: string;
  name: string;
  displayName: string;
  category: string;
  icon: string;
  riskLevel: string;
  lastAnalyzed: string;
  hasAnalysis: boolean;
  hasTerms: boolean;
}

interface Analysis {
  id: string;
  serviceName: string;
  score: number;
  summary: string;
  total_high_severity_concerns: number;
  user_friendliness_score: number;
  data_collection_score: number;
  legal_complexity_score: number;
  concerns: Array<{
    clause: string;
    severity: string;
    explanation: string;
    quote: string;
    clarity_analysis?: any;
  }>;
  recommendations: string[];
  red_flags: string[];
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [services, setServices] = useState<Service[]>([]);
  const [filteredServices, setFilteredServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [analysisData, setAnalysisData] = useState<Analysis | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [showDeepAnalysis, setShowDeepAnalysis] = useState(false);
  const [selectedConcern, setSelectedConcern] = useState<any>(null);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestInProgress, setRequestInProgress] = useState(false);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [isPasteModalOpen, setIsPasteModalOpen] = useState(false);
  const [showTermsViewer, setShowTermsViewer] = useState(false);
  const [termsViewerData, setTermsViewerData] = useState<{
    serviceId: string;
    serviceName: string;
    highlightText: string;
    isPastedTerms: boolean;
    pastedTermsText: string;
  }>({
    serviceId: '',
    serviceName: '',
    highlightText: '',
    isPastedTerms: false,
    pastedTermsText: ''
  });
  const [pastedTermsText, setPastedTermsText] = useState('');
  const [topBottomServices, setTopBottomServices] = useState<{
    top_services: any[];
    bottom_services: any[];
    total_analyzed: number;
  } | null>(null);

  // Fetch services on component mount
  useEffect(() => {
    const fetchServices = async () => {
      try {
        console.log('Attempting to fetch services from backend...');
        const response = await fetch('http://localhost:5001/services', {
          mode: 'cors',
          credentials: 'include'
        });
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        setServices(data.services || []);
        console.log('Services set:', data.services?.length || 0);
      } catch (error) {
        console.error('Error fetching services:', error);
        console.error('Full error details:', error);
      }
    };

    fetchServices();
    fetchTopBottomServices();
  }, []);

  // Fetch top and bottom services
  const fetchTopBottomServices = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/top-bottom-services', {
        mode: 'cors',
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setTopBottomServices(data);
      }
    } catch (error) {
      console.error('Error fetching top/bottom services:', error);
    }
  };

  // Filter services based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredServices([]);
      setShowResults(false);
      return;
    }

    const filtered = services.filter(service =>
      service.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.category.toLowerCase().includes(searchQuery.toLowerCase())
    );

    setFilteredServices(filtered);
    setShowResults(true);
  }, [searchQuery, services]);

  // Handle service selection
  const handleServiceClick = async (service: Service) => {
    console.log('Service clicked:', service);
    setSelectedService(service);
    setIsLoading(true);
    setAnalysisData(null);
    setShowResults(false); // Hide search results
    setSearchQuery(''); // Clear search

    try {
      console.log(`Fetching analysis for: ${service.id}`);
      const response = await fetch(`http://localhost:5001/analysis/${service.id}`, {
        mode: 'cors',
        credentials: 'include'
      });
      console.log('Analysis response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Analysis data received:', data);
      setAnalysisData(data);
      
      // Scroll to results after a brief delay to ensure rendering
      setTimeout(() => {
        const analysisSection = document.querySelector('[data-analysis-results]');
        if (analysisSection) {
          analysisSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
      
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setSelectedService(null);
    setAnalysisData(null);
  };

  // Handle back to search
  const handleBackToSearch = () => {
    setSelectedService(null);
    setAnalysisData(null);
    setShowResults(false);
  };


  // Handle paste terms button click
  const handlePasteTermsClick = () => {
    setIsPasteModalOpen(true);
  };

  // Handle analyze pasted text
  const handleAnalyzePastedText = async (text: string) => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5001/api/analyze/text', {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          app_name: 'Pasted Terms'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const analysis = await response.json();
      setAnalysisData(analysis);
      setPastedTermsText(text); // Store the pasted terms for later viewing
      setSelectedService({
        id: 'pasted',
        name: 'Pasted Terms',
        displayName: 'Pasted Terms',
        category: 'Custom',
        icon: '📄',
        riskLevel: 'unknown',
        lastAnalyzed: new Date().toISOString(),
        hasAnalysis: true,
        hasTerms: true
      });
    } catch (error) {
      console.error('Error analyzing pasted text:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Get severity color based on score (1-10 scale, 1 is worst, 10 is best)
  const getScoreColor = (score: number): string => {
    if (score >= 8) return 'text-green-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get severity emoji and text for high risk items
  const getSeverityDisplay = (severity: string, isHighRisk: boolean = false) => {
    if (severity === 'high' || isHighRisk) {
      return {
        emoji: '🚨🛑',
        text: 'HIGH RISK',
        className: 'bg-red-100 text-red-800 border-red-200'
      };
    }
    if (severity === 'medium') {
      return {
        emoji: '⚠️',
        text: 'MEDIUM RISK',
        className: 'bg-yellow-100 text-yellow-800 border-yellow-200'
      };
    }
    return {
      emoji: 'ℹ️',
      text: 'LOW RISK',
      className: 'bg-blue-100 text-blue-800 border-blue-200'
    };
  };

  // Handle deep analysis modal
  const handleLearnMore = (concern: any) => {
    setSelectedConcern(concern);
    setShowDeepAnalysis(true);
  };

  // Handle showing terms with highlighted clause
  const handleShowTermsWithClause = (concern: any) => {
    if (!selectedService) return;
    
    const isPasted = selectedService.id === 'pasted';
    
    setTermsViewerData({
      serviceId: selectedService.id,
      serviceName: selectedService.displayName,
      highlightText: concern.quote || concern.clause,
      isPastedTerms: isPasted,
      pastedTermsText: isPasted ? pastedTermsText : ''
    });
    setShowTermsViewer(true);
  };

  const handleCloseDeepAnalysis = () => {
    setShowDeepAnalysis(false);
    setSelectedConcern(null);
  };

  // Handle request analysis button
  const handleRequestAnalysisClick = () => {
    setShowRequestModal(true);
  };

  // Handle new service analysis request
  const handleSubmitNewRequest = async (serviceName: string, knownUrl?: string) => {
    try {
      setRequestInProgress(true);
      
      const response = await fetch('http://localhost:5001/api/request-analysis', {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_name: serviceName,
          known_url: knownUrl || undefined
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRequestId(data.request_id);
      
      // Start polling for status
      pollRequestStatus(data.request_id);
      
    } catch (error) {
      console.error('Error submitting request:', error);
      setRequestInProgress(false);
      throw error;
    }
  };

  // Poll for request status
  const pollRequestStatus = async (reqId: string) => {
    try {
      const response = await fetch(`http://localhost:5001/api/request-status/${reqId}`, {
        mode: 'cors',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'completed') {
        // Analysis complete, show results
        setAnalysisData(data.result);
        setSelectedService({
          id: 'new-request',
          name: data.service_name,
          displayName: data.service_name,
          category: 'Requested',
          icon: '🆕',
          riskLevel: 'unknown',
          lastAnalyzed: new Date().toISOString(),
          hasAnalysis: true,
          hasTerms: true
        });
        setRequestInProgress(false);
        setShowRequestModal(false);
        setRequestId(null);
      } else if (data.status === 'failed') {
        setRequestInProgress(false);
        setRequestId(null);
        throw new Error(data.error || 'Analysis failed');
      } else {
        // Still processing, poll again in 5 seconds
        setTimeout(() => pollRequestStatus(reqId), 5000);
      }
      
    } catch (error) {
      console.error('Error polling status:', error);
      setRequestInProgress(false);
      setRequestId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Centered Logo and Title Header */}
      <header className="w-full border-b border-slate-200 bg-white/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-8 py-8 text-center">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="relative w-48 h-24">
              <Image 
                src="/images/logo.png" 
                alt="Terms & Conditions eh Logo"
                fill
                style={{ objectFit: 'contain' }}
                priority
              />
            </div>
          </div>
          
          {/* Title */}
          <div>
            <h1 className="text-4xl font-extralight tracking-tight text-slate-900">
              Terms & Conditions <span className="italic font-light text-slate-600">eh</span>
            </h1>
            <p className="text-slate-600 text-lg font-light max-w-2xl mx-auto leading-relaxed mt-2">
              Decode the legal complexity. Understand what you're really agreeing to.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="w-full flex flex-col items-center px-8 py-16">
        {/* Hero Search Section */}
        <div className="w-full max-w-3xl mb-16">
          <div className="bg-white/70 backdrop-blur-xl rounded-3xl border border-slate-200/50 shadow-2xl shadow-slate-200/20 p-12">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-light text-slate-900 mb-3">
                Analyze Any Service
              </h2>
              <p className="text-slate-600 font-light">
                Search for popular apps and services to see their privacy risks
              </p>
            </div>
            
            <div className="relative">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                  <Search className="h-6 w-6 text-slate-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-16 pr-6 py-6 border-2 border-slate-200/60 rounded-2xl bg-white/90 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-4 focus:ring-slate-200/40 focus:border-slate-300 text-lg font-light shadow-lg transition-all duration-300 hover:shadow-xl"
                  placeholder="Netflix, Spotify, Instagram, Facebook..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
              </div>
              
              {/* Search Results Dropdown */}
              {searchQuery && showResults && filteredServices.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl border border-slate-200 shadow-xl z-50 max-h-60 overflow-y-auto">
                  {filteredServices.map((service) => (
                    <div
                      key={service.id}
                      onClick={() => handleServiceClick(service)}
                      className="flex items-center px-6 py-4 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-b-0"
                    >
                      <div className="text-2xl mr-4">{service.icon}</div>
                      <div className="flex-1">
                        <div className="font-medium text-slate-900">{service.displayName}</div>
                        <div className="text-sm text-slate-500">{service.category}</div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${
                          service.riskLevel === 'low' ? 'text-green-600' :
                          service.riskLevel === 'medium' ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {service.riskLevel} risk
                        </div>
                        <CheckCircle className="h-4 w-4 text-green-500 mt-1" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* No Results Message */}
              {searchQuery && showResults && filteredServices.length === 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl border border-slate-200 shadow-xl z-50 p-6 text-center">
                  <div className="text-slate-500">
                    No services found matching "{searchQuery}"
                  </div>
                  <div className="text-sm text-slate-400 mt-1">
                    Try searching for: Netflix, YouTube, Instagram, TikTok, or Facebook
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Elegant Secondary Actions */}
        <div className={`w-full max-w-lg mb-12 transition-all duration-300 ${
          (searchQuery && showResults && (filteredServices.length > 0 || filteredServices.length === 0)) 
            ? 'mt-20' : 'mt-0'
        }`}>
          <div className="flex items-center justify-center space-x-6">
            <button 
              onClick={handlePasteTermsClick}
              className="group relative inline-flex items-center px-8 py-4 bg-white/80 border-2 border-slate-200/60 rounded-2xl text-slate-700 font-medium hover:bg-white hover:border-slate-300 focus:outline-none focus:ring-4 focus:ring-slate-200/40 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 backdrop-blur-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-slate-100/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <FileText className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
              <span className="relative">Paste Terms</span>
            </button>
            
            <button 
              onClick={handleRequestAnalysisClick}
              disabled={requestInProgress}
              className="group relative inline-flex items-center px-8 py-4 bg-blue-600/90 border-2 border-blue-500/60 rounded-2xl text-white font-medium hover:bg-blue-700 hover:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-200/40 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 backdrop-blur-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              {requestInProgress ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  <span className="relative">Processing...</span>
                </>
              ) : (
                <>
                  <Scale className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
                  <span className="relative">Request Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-500 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading analysis...</p>
          </div>
        )}

        {/* Search Results */}
      {showResults && !selectedService && !isLoading && (
        <div className="w-full max-w-4xl">
          <div className="bg-white/70 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl overflow-hidden">
            <div className="px-8 py-6 border-b border-slate-200/50 bg-slate-50/50">
              <h3 className="text-xl font-light text-slate-900">
                Search Results
              </h3>
              <p className="mt-1 text-sm text-slate-500">
                Found {filteredServices.length} services matching "{searchQuery}"
              </p>
              </div>
              <div className="p-8">
                {filteredServices.length === 0 ? (
                  <div className="text-center text-slate-500">
                    No services found matching your search. Try searching for popular apps like Netflix, YouTube, or Instagram.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredServices.map((service) => (
                      <div
                        key={service.id}
                        onClick={() => handleServiceClick(service)}
                        className="cursor-pointer p-4 bg-white/80 rounded-xl border border-slate-200/50 hover:border-slate-300 hover:shadow-lg transition-all duration-300 group"
                      >
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="text-2xl">{service.icon}</div>
                          <div>
                            <h4 className="font-medium text-slate-900 group-hover:text-slate-700">
                              {service.displayName}
                            </h4>
                            <p className="text-sm text-slate-500">{service.category}</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-400">
                            {service.hasAnalysis ? 'Analysis available' : 'No analysis'}
                          </span>
                          {service.hasAnalysis && (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisData && selectedService && !isLoading && (
          <div className="w-full max-w-4xl" data-analysis-results>
            <div className="bg-white/70 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl overflow-hidden">
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-light text-slate-900">{analysisData.serviceName}</h2>
                    <div className="flex items-center mt-2">
                      <div className={`text-3xl font-bold ${getScoreColor(analysisData.score)}`}>
                        {analysisData.score.toFixed(1)}
                      </div>
                      <span className="ml-2 text-slate-500">/ 10</span>
                    </div>
                  </div>
                  <div className="flex space-x-4">
                    <div className="text-center">
                      <div className="text-sm text-slate-500">User Friendly</div>
                      <div className={`font-medium ${getScoreColor(analysisData.user_friendliness_score)}`}>
                        {analysisData.user_friendliness_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-slate-500">Data Privacy</div>
                      <div className={`font-medium ${getScoreColor(analysisData.data_collection_score)}`}>
                        {analysisData.data_collection_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-slate-500">Legal Clarity</div>
                      <div className={`font-medium ${getScoreColor(analysisData.legal_complexity_score)}`}>
                        {analysisData.legal_complexity_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <div className="mb-8">
                  <h3 className="text-lg font-medium text-slate-900 mb-2">Summary</h3>
                  <p className="text-slate-700">{analysisData.summary}</p>
                </div>

                {/* Red Flags - Show first as they are highest priority */}
                {analysisData.red_flags && analysisData.red_flags.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-medium text-slate-900 mb-4">🚨 High Risk Flags</h3>
                    <div className="space-y-4">
                      {analysisData.red_flags.map((flag: string, index: number) => {
                        // Try to match red flag to an existing concern for more details
                        const matchedConcern = analysisData.concerns?.find((concern: any) => 
                          concern.clause.toLowerCase().includes(flag.toLowerCase().split(' ').slice(0, 3).join(' ')) ||
                          flag.toLowerCase().includes(concern.clause.toLowerCase().split(' ').slice(0, 3).join(' ')) ||
                          (concern.explanation && concern.explanation.toLowerCase().includes(flag.toLowerCase().split(' ').slice(0, 2).join(' ')))
                        );

                        return (
                          <div key={index} className="p-4 rounded-lg border-2 bg-red-50 border-red-200">
                            <div className="flex items-start justify-between">
                              <div className="flex items-start flex-1">
                                <div className="flex-shrink-0 px-2 py-1 rounded-full text-xs font-bold border-2 bg-red-100 text-red-800 border-red-200">
                                  <span className="mr-1">🚨🛑</span>
                                  HIGH RISK
                                </div>
                                <div className="ml-4 flex-1">
                                  <h4 className="text-sm font-medium text-slate-900">{flag}</h4>
                                  {matchedConcern && (
                                    <>
                                      <p className="mt-1 text-sm text-slate-600">{matchedConcern.explanation}</p>
                                      {matchedConcern.quote && (
                                        <div className="mt-2 p-3 bg-white/70 border-l-4 border-slate-300 text-sm text-slate-600 italic">
                                          "{matchedConcern.quote}"
                                        </div>
                                      )}
                                    </>
                                  )}
                                </div>
                              </div>
                              
                              <div className="ml-4 flex flex-col space-y-2">
                                {/* View in Terms button - only show if service has terms */}
                                {selectedService?.hasTerms && (
                                  <button
                                    onClick={() => handleShowTermsWithClause({ 
                                      clause: flag, 
                                      quote: matchedConcern?.quote || flag 
                                    })}
                                    className="px-3 py-1 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center"
                                  >
                                    <FileText className="h-3 w-3 mr-1" />
                                    View in Terms
                                  </button>
                                )}
                                
                                {/* Learn More button if matched concern has deep analysis */}
                                {matchedConcern && matchedConcern.clarity_analysis && (
                                  <button
                                    onClick={() => handleLearnMore(matchedConcern)}
                                    className="px-3 py-1 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center"
                                  >
                                    <span className="mr-1">🔍</span>
                                    Learn More
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Concerns */}
                {analysisData.concerns && analysisData.concerns.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-medium text-slate-900 mb-4">Additional Concerns</h3>
                    <div className="space-y-4">
                      {analysisData.concerns
                        .filter((concern: any) => {
                          // Filter out high-risk concerns that are already shown as red flags
                          if (concern.severity === 'high' && analysisData.red_flags) {
                            return !analysisData.red_flags.some((flag: string) => 
                              flag.toLowerCase().includes(concern.clause.toLowerCase().split(' ').slice(0, 3).join(' ')) ||
                              concern.clause.toLowerCase().includes(flag.toLowerCase().split(' ').slice(0, 3).join(' '))
                            );
                          }
                          return true; // Show all medium and low risk concerns
                        })
                        .map((concern: any, index: number) => {
                        const severityDisplay = getSeverityDisplay(concern.severity);
                        const isHighRisk = concern.severity === 'high';
                        
                        return (
                          <div key={index} className={`p-4 rounded-lg border-2 ${
                            isHighRisk ? 'bg-red-50 border-red-200' : 
                            concern.severity === 'medium' ? 'bg-yellow-50 border-yellow-200' : 
                            'bg-blue-50 border-blue-200'
                          }`}>
                            <div className="flex items-start justify-between">
                              <div className="flex items-start flex-1">
                                <div className={`flex-shrink-0 px-2 py-1 rounded-full text-xs font-bold border-2 ${severityDisplay.className}`}>
                                  <span className="mr-1">{severityDisplay.emoji}</span>
                                  {severityDisplay.text}
                                </div>
                                <div className="ml-4 flex-1">
                                  <h4 className="text-sm font-medium text-slate-900">{concern.clause}</h4>
                                  <p className="mt-1 text-sm text-slate-600">{concern.explanation}</p>
                                  {concern.quote && (
                                    <div className="mt-2 p-3 bg-white/70 border-l-4 border-slate-300 text-sm text-slate-600 italic">
                                      "{concern.quote}"
                                    </div>
                                  )}
                                </div>
                              </div>
                              
                              <div className="ml-4 flex flex-col space-y-2">
                                {/* View in Terms button for all concerns - only show if service has terms */}
                                {selectedService?.hasTerms && (
                                  <button
                                    onClick={() => handleShowTermsWithClause(concern)}
                                    className="px-3 py-1 bg-slate-600 text-white text-xs font-medium rounded-lg hover:bg-slate-700 transition-colors duration-200 flex items-center"
                                  >
                                    <FileText className="h-3 w-3 mr-1" />
                                    View in Terms
                                  </button>
                                )}
                                
                                {/* Learn More button for high risk items with deep analysis */}
                                {isHighRisk && concern.clarity_analysis && (
                                  <button
                                    onClick={() => handleLearnMore(concern)}
                                    className="px-3 py-1 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center"
                                  >
                                    <span className="mr-1">🔍</span>
                                    Learn More
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                {/* Back to Search */}
                <div className="pt-6 border-t border-slate-200/50 mt-8">
                  <button
                    onClick={handleBackToSearch}
                    className="text-slate-600 hover:text-slate-900 text-sm font-medium transition-colors flex items-center"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Back to search results
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Default state - no search */}
        {!showResults && !selectedService && !isLoading && (
          <div className="w-full max-w-4xl space-y-8">
            {/* Ready to Analyze Card */}
            <div className="bg-white/70 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl overflow-hidden">
              <div className="px-8 py-6 border-b border-slate-200/50 bg-slate-50/50">
                <h3 className="text-xl font-light text-slate-900">
                  Ready to Analyze
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Search for a service above to see detailed privacy analysis
                </p>
              </div>
              <div className="p-8">
                <div className="text-center text-slate-500">
                  <Scale className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-lg font-light mb-2">We've analyzed {services.length} popular services</p>
                  <p className="text-sm">Try searching for Netflix, YouTube, Instagram, TikTok, or Facebook</p>
                </div>
              </div>
            </div>

            {/* Best vs Worst Services Comparison */}
            {topBottomServices && (
              <div className="bg-white/70 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl overflow-hidden">
                <div className="px-8 py-6 border-b border-slate-200/50 bg-slate-50/50">
                  <h3 className="text-xl font-light text-slate-900">
                    Best vs Worst Privacy Practices
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Compare the top and bottom rated services from our analysis of {topBottomServices.total_analyzed} apps
                  </p>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Worst Services (Left) */}
                    <div className="space-y-4">
                      <div className="flex items-center mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">🚨</span>
                          <h4 className="text-lg font-semibold text-red-600">Highest Risk</h4>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {topBottomServices.bottom_services.map((service: any, index: number) => (
                          <div
                            key={service.id}
                            onClick={() => handleServiceClick({
                              id: service.id,
                              name: service.displayName,
                              displayName: service.displayName,
                              category: service.category,
                              icon: service.icon,
                              riskLevel: service.risk_level,
                              lastAnalyzed: new Date().toISOString(),
                              hasAnalysis: true,
                              hasTerms: true
                            })}
                            className="cursor-pointer p-4 bg-red-50 border-2 border-red-200 rounded-xl hover:border-red-300 hover:shadow-md transition-all duration-300 group"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="text-2xl">{service.icon}</div>
                                <div>
                                  <h5 className="font-medium text-slate-900 group-hover:text-red-700">
                                    {service.displayName}
                                  </h5>
                                  <p className="text-sm text-slate-500">{service.category}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-2xl font-bold text-red-600">
                                  {service.overall_score.toFixed(1)}/10
                                </div>
                                <div className="flex items-center space-x-1 text-xs text-red-600">
                                  <span>🛑</span>
                                  <span className="font-medium">{service.red_flags_count} flags</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Best Services (Right) */}
                    <div className="space-y-4">
                      <div className="flex items-center mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">✅</span>
                          <h4 className="text-lg font-semibold text-green-600">Best Practices</h4>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {topBottomServices.top_services.map((service: any, index: number) => (
                          <div
                            key={service.id}
                            onClick={() => handleServiceClick({
                              id: service.id,
                              name: service.displayName,
                              displayName: service.displayName,
                              category: service.category,
                              icon: service.icon,
                              riskLevel: service.risk_level,
                              lastAnalyzed: new Date().toISOString(),
                              hasAnalysis: true,
                              hasTerms: true
                            })}
                            className="cursor-pointer p-4 bg-green-50 border-2 border-green-200 rounded-xl hover:border-green-300 hover:shadow-md transition-all duration-300 group"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="text-2xl">{service.icon}</div>
                                <div>
                                  <h5 className="font-medium text-slate-900 group-hover:text-green-700">
                                    {service.displayName}
                                  </h5>
                                  <p className="text-sm text-slate-500">{service.category}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-2xl font-bold text-green-600">
                                  {service.overall_score.toFixed(1)}/10
                                </div>
                                <div className="flex items-center space-x-1 text-xs text-green-600">
                                  <span>✅</span>
                                  <span className="font-medium">{service.red_flags_count} flags</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Deep Analysis Modal */}
      {showDeepAnalysis && selectedConcern && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200 bg-red-50">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-red-800 flex items-center">
                  <span className="mr-3">🚨🛑</span>
                  HIGH RISK - Deep Analysis
                </h2>
                <button
                  onClick={handleCloseDeepAnalysis}
                  className="text-slate-400 hover:text-slate-600 text-2xl"
                >
                  ×
                </button>
              </div>
              <h3 className="text-lg font-medium text-slate-900 mt-2">
                {selectedConcern.clause}
              </h3>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Practical Meaning */}
              {selectedConcern.clarity_analysis?.practical_meaning && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                    <span className="mr-2">💡</span>
                    What This Really Means
                  </h4>
                  <p className="text-blue-800 text-sm leading-relaxed">
                    {selectedConcern.clarity_analysis.practical_meaning}
                  </p>
                </div>
              )}

              {/* Unclear Terms */}
              {selectedConcern.clarity_analysis?.unclear_terms && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-900 mb-3 flex items-center">
                    <span className="mr-2">❓</span>
                    Confusing Terms Explained
                  </h4>
                  <div className="space-y-4">
                    {selectedConcern.clarity_analysis.unclear_terms.map((term: any, index: number) => (
                      <div key={index} className="bg-white p-3 rounded border">
                        <h5 className="font-medium text-slate-900 mb-1">"{term.term}"</h5>
                        <p className="text-sm text-slate-600 mb-2">{term.explanation}</p>
                        
                        {term.user_impact && (
                          <div className="bg-orange-50 border-l-4 border-orange-400 p-2 mb-2">
                            <p className="text-sm text-orange-800">
                              <strong>Impact on You:</strong> {term.user_impact}
                            </p>
                          </div>
                        )}
                        
                        {term.questions_to_ask && term.questions_to_ask.length > 0 && (
                          <div className="bg-slate-50 p-2 rounded">
                            <p className="text-xs font-medium text-slate-700 mb-1">Questions to Ask:</p>
                            <ul className="text-xs text-slate-600 space-y-1">
                              {term.questions_to_ask.map((question: string, qIndex: number) => (
                                <li key={qIndex} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  {question}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Needed */}
              {selectedConcern.clarity_analysis?.user_action_needed && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-900 mb-2 flex items-center">
                    <span className="mr-2">✅</span>
                    What You Should Do
                  </h4>
                  <p className="text-green-800 text-sm leading-relaxed">
                    {selectedConcern.clarity_analysis.user_action_needed}
                  </p>
                </div>
              )}

              {/* Severity Justification */}
              {selectedConcern.clarity_analysis?.severity_justification && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h4 className="font-semibold text-red-900 mb-2 flex items-center">
                    <span className="mr-2">⚠️</span>
                    Why This is High Risk
                  </h4>
                  <p className="text-red-800 text-sm leading-relaxed">
                    {selectedConcern.clarity_analysis.severity_justification}
                  </p>
                </div>
              )}

              {/* Original Quote */}
              {selectedConcern.quote && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <h4 className="font-semibold text-slate-900 mb-2 flex items-center">
                    <span className="mr-2">📄</span>
                    Original Terms Text
                  </h4>
                  <blockquote className="text-sm text-slate-700 italic border-l-4 border-slate-400 pl-4">
                    "{selectedConcern.quote}"
                  </blockquote>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Paste Terms Modal */}
      <PasteTermsModal
        isOpen={isPasteModalOpen}
        onClose={() => setIsPasteModalOpen(false)}
        onAnalyze={handleAnalyzePastedText}
      />

      {/* Request Analysis Modal */}
      <RequestAnalysisModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        onSubmit={handleSubmitNewRequest}
        isProcessing={requestInProgress}
      />

      {/* Terms Viewer Modal */}
      <TermsViewerModal
        isOpen={showTermsViewer}
        onClose={() => setShowTermsViewer(false)}
        serviceId={termsViewerData.serviceId}
        serviceName={termsViewerData.serviceName}
        highlightText={termsViewerData.highlightText}
        isPastedTerms={termsViewerData.isPastedTerms}
        pastedTermsText={termsViewerData.pastedTermsText}
      />
    </div>
  );
}