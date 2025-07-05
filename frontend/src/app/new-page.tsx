'use client';

import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import { Search, Gavel, X, Check, Clock, ArrowRight, FileText, FileSearch, AlertTriangle, Info } from 'lucide-react';

// Components
import { SearchBar } from './components/SearchBar';
import { CategoryFilter } from './components/CategoryFilter';
import ServiceCard from './components/ServiceCard';
import { AnalysisResult as AnalysisResultComponent } from './components/AnalysisResult';
import Modal from './components/Modal';

// Types
import type { Service, Category } from '@/types';
import type { AnalysisResult } from '@/types/analysis';

// Mock data
const MOCK_SERVICES: Service[] = [
  {
    id: 'netflix-neighborhood',
    name: 'Netflix in Your Neighbourhood',
    displayName: 'Netflix in Your Neighbourhood',
    category: 'Entertainment',
    icon: '🎬',
    riskLevel: 'medium',
    lastAnalyzed: '2025-07-05T00:00:00Z',
    hasAnalysis: true
  },
  {
    id: 'tiktok',
    name: 'tiktok',
    displayName: 'TikTok',
    category: 'Social Media',
    icon: '🎵',
    riskLevel: 'high',
    lastAnalyzed: '2023-11-15T14:30:00Z',
    hasAnalysis: false
  },
  {
    id: 'instagram',
    name: 'instagram',
    displayName: 'Instagram',
    category: 'Social Media',
    icon: '📷',
    riskLevel: 'medium',
    lastAnalyzed: '2023-11-10T09:15:00Z',
    hasAnalysis: false
  }
];

const CATEGORIES: Category[] = [
  { id: 'all', name: 'All Services', icon: '📋', count: MOCK_SERVICES.length },
  { 
    id: 'social', 
    name: 'Social Media', 
    icon: '👥', 
    count: MOCK_SERVICES.filter(s => s.category === 'Social Media').length 
  },
  { 
    id: 'entertainment', 
    name: 'Entertainment', 
    icon: '🎬', 
    count: MOCK_SERVICES.filter(s => s.category === 'Entertainment').length 
  }
];

// Netflix analysis data
const NETFLIX_ANALYSIS: AnalysisResult = {
  app_name: 'Netflix in Your Neighbourhood',
  app_version: null,
  overall_score: 7.5,
  privacy_concerns: [
    {
      clause: 'Collection of geolocation data and device identifiers',
      severity: 'medium',
      explanation: 'The terms mention the collection of geolocation data and device identifiers, which could potentially be invasive if not strictly necessary for the app\'s functionality.',
      quote: 'Identifiers (such as IP address, identifiers from the devices you use to connect, characteristics about the networks you use when you connect to our Experience) and Geolocation data (such as IP address or GPS coordinates).'
    },
    {
      clause: 'Broad rights to use name and likeness',
      severity: 'high',
      explanation: 'The terms grant Netflix an irrevocable, perpetual, worldwide, non-exclusive right to use users\' likeness, name, and other personal attributes for a wide range of purposes, including advertising and promotion.',
      quote: 'By interacting with this Experience, you grant the Netflix entity...the irrevocable, perpetual, worldwide, non-exclusive right to record, depict, and/or portray you and use...your actual or simulated likeness, name, photograph, voice, actions, etc.'
    }
  ],
  summary: 'The Netflix in Your Neighbourhood terms are generally clear and user-friendly, but raise some privacy concerns, particularly regarding the collection of geolocation data, the use of personal likeness, and broad data-sharing practices.',
  red_flags: [
    'Broad rights to use personal likeness without compensation',
    'Extensive data collection, including geolocation and device identifiers',
    'Limited user control over tracking technologies on mobile devices',
    'Broad data-sharing practices with Netflix affiliates and third-party providers'
  ],
  user_friendliness_score: 7.0,
  data_collection_score: 6.0,
  legal_complexity_score: 8.0,
  terms_version: null,
  terms_url: 'https://www.netflixinyourneighbourhood.ca/privacy/',
  analysis_date: '2025-07-05'
};

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [requestedService, setRequestedService] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Handle click outside dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Filter services based on search query and category
  const filteredServices = MOCK_SERVICES.filter(service => {
    const matchesSearch = 
      service.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.category.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = 
      selectedCategory === 'all' || 
      service.category.toLowerCase().includes(selectedCategory.toLowerCase());
    
    return matchesSearch && matchesCategory;
  });

  // Handle service selection
  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    setSearchQuery('');
    setShowDropdown(false);
    
    if (service.id === 'netflix-neighborhood') {
      setAnalysisResult(NETFLIX_ANALYSIS);
    } else {
      setAnalysisResult(null);
      setIsAnalyzing(true);
      
      // Simulate API call for other services
      setTimeout(() => {
        setIsAnalyzing(false);
        // In a real app, we would set the analysis result here
      }, 1500);
    }
  };

  // Handle paste and analyze
  const handlePasteAnalyze = () => {
    if (!pastedText.trim()) return;
    
    setShowPasteModal(false);
    setIsAnalyzing(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsAnalyzing(false);
      setPastedText('');
    }, 2000);
  };

  // Handle service request
  const handleRequestService = () => {
    if (!requestedService.trim()) return;
    
    // In a real app, this would send a request to your backend
    alert(`Thank you for requesting analysis of ${requestedService}. We'll notify you when it's ready!`);
    setRequestedService('');
    setShowRequestModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Head>
        <title>Terms and Conditions Analyzer</title>
        <meta name="description" content="Analyze terms and conditions of popular services" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Gavel className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Terms and Conditions <span className="text-primary-600 dark:text-primary-400">Analyzer</span>
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              <button
                onClick={() => setShowPasteModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 dark:text-primary-200 dark:bg-primary-900/30 dark:hover:bg-primary-800/50"
              >
                <FileText className="h-4 w-4 mr-2" />
                Paste Terms
              </button>
              <button
                onClick={() => setShowRequestModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                <FileSearch className="h-4 w-4 mr-2" />
                Request Analysis
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <div className="relative" ref={dropdownRef}>
            <SearchBar
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              showDropdown={showDropdown}
              setShowDropdown={setShowDropdown}
              dropdownRef={dropdownRef}
              filteredServices={filteredServices}
              onServiceSelect={handleServiceSelect}
            />
          </div>

          <CategoryFilter
            categories={CATEGORIES}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        </div>

        {/* Analysis Section */}
        {isAnalyzing ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
            <p className="text-gray-600 dark:text-gray-300">Analyzing terms and conditions...</p>
          </div>
        ) : analysisResult ? (
          <div id="analysis-results" className="space-y-8">
            <AnalysisResultComponent analysis={analysisResult} />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredServices.map((service) => (
              <ServiceCard 
                key={service.id} 
                service={service} 
                onClick={() => handleServiceSelect(service)} 
              />
            ))}
          </div>
        )}
      </main>

      {/* Paste Terms Modal */}
      <Modal isOpen={showPasteModal} onClose={() => setShowPasteModal(false)}>
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Paste Terms & Conditions</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Paste the terms and conditions text you'd like to analyze below.
          </p>
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            className="w-full h-64 p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="Paste terms and conditions text here..."
          />
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setShowPasteModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handlePasteAnalyze}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              disabled={!pastedText.trim()}
            >
              Analyze
            </button>
          </div>
        </div>
      </Modal>

      {/* Request Analysis Modal */}
      <Modal isOpen={showRequestModal} onClose={() => setShowRequestModal(false)}>
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Request Service Analysis</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Enter the name of the service you'd like us to analyze. We'll notify you when it's ready.
          </p>
          <input
            type="text"
            value={requestedService}
            onChange={(e) => setRequestedService(e.target.value)}
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="e.g., Netflix, Instagram, etc."
          />
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setShowRequestModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleRequestService}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              disabled={!requestedService.trim()}
            >
              Request Analysis
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
