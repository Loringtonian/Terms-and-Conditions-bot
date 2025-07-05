'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { Search, FileText, Gavel, Scale, AlertTriangle, CheckCircle } from 'lucide-react';

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

  // Fetch services on component mount
  useEffect(() => {
    const fetchServices = async () => {
      try {
        console.log('Attempting to fetch services from backend...');
        const response = await fetch('http://localhost:5001/services');
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
  }, []);

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
    setSelectedService(service);
    setIsLoading(true);
    setAnalysisData(null);

    try {
      const response = await fetch(`http://localhost:5001/analysis/${service.id}`);
      const data = await response.json();
      setAnalysisData(data);
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

  // State for paste terms modal
  const [isPasteModalOpen, setIsPasteModalOpen] = useState(false);

  // Handle paste terms button click
  const handlePasteTermsClick = () => {
    setIsPasteModalOpen(true);
  };

  // Get severity color based on score (1-10 scale, 1 is worst, 10 is best)
  const getScoreColor = (score: number): string => {
    if (score >= 8) return 'text-green-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-600';
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
        <div className="w-full max-w-lg mb-12">
          <div className="flex items-center justify-center space-x-6">
            <button 
              className="group relative inline-flex items-center px-8 py-4 bg-white/80 border-2 border-slate-200/60 rounded-2xl text-slate-700 font-medium hover:bg-white hover:border-slate-300 focus:outline-none focus:ring-4 focus:ring-slate-200/40 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 backdrop-blur-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-slate-100/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <FileText className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
              <span className="relative">Paste Terms</span>
            </button>
            
            <button 
              disabled={true}
              className="group relative inline-flex items-center px-8 py-4 bg-slate-900/10 border-2 border-slate-200/30 rounded-2xl text-slate-400 font-medium focus:outline-none transition-all duration-300 cursor-not-allowed"
            >
              <Scale className="h-5 w-5 mr-3" />
              <span className="relative">Request Analysis (Coming Soon)</span>
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
          <div className="w-full max-w-4xl">
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

                {/* Concerns */}
                {analysisData.concerns && analysisData.concerns.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-medium text-slate-900 mb-4">Key Concerns</h3>
                    <div className="space-y-4">
                      {analysisData.concerns.map((concern: any, index: number) => (
                        <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                          <div className="flex items-start">
                            <div className={`flex-shrink-0 h-5 w-5 rounded-full flex items-center justify-center ${
                              concern.severity === 'high' ? 'bg-red-100 text-red-600' : 
                              concern.severity === 'medium' ? 'bg-yellow-100 text-yellow-600' : 
                              'bg-blue-100 text-blue-600'
                            }`}>
                              {concern.severity === 'high' ? (
                                <AlertTriangle className="h-3.5 w-3.5" />
                              ) : concern.severity === 'medium' ? (
                                <AlertTriangle className="h-3 w-3" />
                              ) : (
                                <span className="text-xs font-medium">i</span>
                              )}
                            </div>
                            <div className="ml-3">
                              <h4 className="text-sm font-medium text-slate-900">{concern.clause}</h4>
                              <p className="mt-1 text-sm text-slate-600">{concern.explanation}</p>
                              {concern.quote && (
                                <div className="mt-2 p-3 bg-slate-50 border-l-2 border-slate-200 text-sm text-slate-600 italic">
                                  "{concern.quote}"
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Red Flags */}
                {analysisData.red_flags && analysisData.red_flags.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-slate-900 mb-4">Red Flags</h3>
                    <ul className="space-y-2">
                      {analysisData.red_flags.map((flag: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <div className="flex-shrink-0 h-5 w-5 rounded-full bg-red-100 flex items-center justify-center text-red-600">
                            <AlertTriangle className="h-3 w-3" />
                          </div>
                          <span className="ml-2 text-sm text-slate-700">{flag}</span>
                        </li>
                      ))}
                    </ul>
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
          <div className="w-full max-w-4xl">
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
          </div>
        )}
      </main>
    </div>
  );
}