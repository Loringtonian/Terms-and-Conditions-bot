'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  Search, 
  FileText, 
  ClipboardPaste, 
  AlertCircle, 
  ChevronDown, 
  Check, 
  X, 
  Loader2, 
  Scale, 
  Gavel, 
  Shield, 
  Clock, 
  FileQuestion,
  ChevronRight,
  ExternalLink,
  Info,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle
} from 'lucide-react';

type Service = {
  id: string;
  name: string;
  displayName: string;
  category: string;
  icon?: string;
  lastAnalyzed?: string;
  riskLevel?: 'low' | 'medium' | 'high';
};

type AnalysisSection = {
  title: string;
  score: number;
  description: string;
  concerns: string[];
  recommendations?: string[];
};

type AnalysisResult = {
  id: string;
  serviceName: string;
  serviceUrl?: string;
  score: number;
  summary: string;
  sections: AnalysisSection[];
  lastUpdated: string;
  analyzedAt: string;
  documentLength?: number;
  readabilityScore?: number;
  keyPoints?: {
    title: string;
    description: string;
    impact: 'positive' | 'neutral' | 'negative';
  }[];
};

const CATEGORIES = [
  { id: 'all', name: 'All Services', icon: '📱' },
];

const MOCK_SERVICES: Service[] = [
  {
    id: 'tiktok',
    displayName: 'TikTok',
    legalName: 'TikTok Pte. Ltd.',
    category: 'Social Media',
    icon: '🎵',
    riskLevel: 'high',
    lastAnalyzed: '2023-11-15T14:30:00Z'
  },
  {
    id: 'instagram',
    displayName: 'Instagram',
    legalName: 'Instagram, LLC',
    category: 'Social Media',
    icon: '📷',
    riskLevel: 'medium',
    lastAnalyzed: '2023-11-10T09:15:00Z'
  },
  {
    id: 'netflix',
    displayName: 'Netflix',
    legalName: 'Netflix, Inc.',
    category: 'Entertainment',
    icon: '🎬',
    riskLevel: 'low',
    lastAnalyzed: '2023-11-05T16:45:00Z'
  },
  {
    id: 'spotify',
    displayName: 'Spotify',
    legalName: 'Spotify AB',
    category: 'Music',
    icon: '🎧',
    riskLevel: 'medium',
    lastAnalyzed: '2023-11-01T11:20:00Z'
  },
  {
    id: 'whatsapp',
    displayName: 'WhatsApp',
    legalName: 'WhatsApp LLC',
    category: 'Messaging',
    icon: '💬',
    riskLevel: 'medium',
    lastAnalyzed: '2023-10-28T13:10:00Z'
  },
  {
    id: 'dropbox',
    displayName: 'Dropbox',
    legalName: 'Dropbox, Inc.',
    category: 'Cloud Storage',
    icon: '📦',
    riskLevel: 'low',
    lastAnalyzed: '2023-10-25T10:05:00Z'
  },
  {
    id: 'uber',
    displayName: 'Uber',
    legalName: 'Uber Technologies, Inc.',
    category: 'Transportation',
    icon: '🚗',
    riskLevel: 'high',
    lastAnalyzed: '2023-10-20T08:30:00Z'
  },
  {
    id: 'airbnb',
    displayName: 'Airbnb',
    legalName: 'Airbnb, Inc.',
    category: 'Travel',
    icon: '🏠',
    riskLevel: 'medium',
    lastAnalyzed: '2023-10-15T14:20:00Z'
  },
  {
    id: 'linkedin',
    displayName: 'LinkedIn',
    legalName: 'LinkedIn Corporation',
    category: 'Professional',
    icon: '💼',
    riskLevel: 'medium',
    lastAnalyzed: '2023-10-10T11:45:00Z'
  },
  {
    id: 'twitter',
    displayName: 'Twitter',
    legalName: 'X Corp.',
    category: 'Social Media',
    icon: '🐦',
    riskLevel: 'high',
    lastAnalyzed: '2023-10-05T09:30:00Z'
  }
];

const MOCK_ANALYSIS: AnalysisResult = {
  id: 'analysis-1',
  serviceName: 'TikTok',
  score: 42,
  summary: 'TikTok\'s terms and conditions raise significant privacy concerns, particularly around data collection and sharing with third parties. The platform collects extensive user data, including device information, location, and browsing history, which is used for targeted advertising and may be shared with parent company ByteDance and other third parties.',
  lastUpdated: '2023-11-15T14:30:00Z',
  analyzedAt: '2023-11-15T14:35:22Z',
  keyPoints: [
    {
      title: 'Extensive Data Collection',
      description: 'Collects a wide range of personal data including biometric data, browsing history, and location information.',
      impact: 'negative'
    },
    {
      title: 'Third-Party Sharing',
      description: 'User data is shared with numerous third parties, including advertisers and business partners.',
      impact: 'negative'
    },
    {
      title: 'Content Ownership',
      description: 'Users retain ownership of their content but grant TikTok a broad license to use, modify, and distribute it.',
      impact: 'neutral'
    },
    {
      title: 'Age Restrictions',
      description: 'Has specific policies for users under 18, though enforcement is inconsistent.',
      impact: 'positive'
    }
  ],
  sections: [
    {
      title: 'Data Collection',
      description: 'TikTok collects an extensive amount of user data, including but not limited to: device information, location data, browsing history, messages, and biometric data. This data is used for personalization, advertising, and analytics purposes.',
      score: 30,
      concerns: [
        'Collects biometric data including facial recognition and voiceprints',
        'Tracks user behavior across other websites and apps',
        'Stores location data even when not using the app'
      ],
      recommendations: [
        'Review and adjust privacy settings in the app',
        'Consider using TikTok in a web browser with tracking protection',
        'Be cautious about what personal information you share in your profile'
      ]
    },
    {
      title: 'Data Sharing',
      description: 'User data is shared with numerous third parties, including advertisers, business partners, and service providers. TikTok may also share data with law enforcement when required by law.',
      score: 25,
      concerns: [
        'Shares data with parent company ByteDance and its affiliates',
        'Allows third-party advertisers to target users based on their data',
        'May share data with government agencies when required by law'
      ],
      recommendations: [
        'Regularly review connected apps and services',
        'Use a dedicated email address for TikTok',
        'Consider using a VPN for additional privacy'
      ]
    },
    {
      title: 'Content Ownership',
      description: 'While users retain ownership of their content, they grant TikTok a broad, worldwide, non-exclusive, royalty-free license to use, modify, and distribute their content without additional compensation.',
      score: 60,
      concerns: [
        'Broad license granted to TikTok to use your content',
        'Limited ability to control how your content is used by others',
        'Difficult to completely remove content from the platform'
      ],
      recommendations: [
        'Be mindful of what you post',
        'Consider watermarking your original content',
        'Regularly review and manage your content'
      ]
    },
    {
      title: 'Privacy Controls',
      description: 'TikTok provides various privacy controls that allow users to limit data collection and sharing, though some settings may be difficult to find or understand.',
      score: 55,
      concerns: [
        'Privacy settings are not always intuitive',
        'Some data collection cannot be opted out of',
        'Settings may change without clear notification'
      ],
      recommendations: [
        'Review and adjust privacy settings regularly',
        'Enable two-factor authentication',
        'Consider making your account private'
      ]
    }
  ]
};

const getRiskLevelColor = (riskLevel?: string) => {
  switch (riskLevel) {
    case 'high':
      return 'bg-red-500 text-white';
    case 'medium':
      return 'bg-yellow-500 text-white';
    case 'low':
      return 'bg-green-500 text-white';
    default:
      return 'bg-gray-500 text-white';
  }
};

const formatDate = (date: string) => {
  const dateObject = new Date(date);
  return dateObject.toLocaleDateString();
};

const ServiceCard = ({ service, onClick }: { service: Service; onClick: () => void }) => {
  const riskLevel = service.riskLevel || 'unknown';
  
  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 cursor-pointer hover:shadow-md transition-all duration-200 hover:border-primary-500/30 group"
    >
      <div className="flex items-start space-x-4">
        <div className={`flex-shrink-0 h-12 w-12 rounded-lg ${getRiskLevelColor(riskLevel)} flex items-center justify-center text-2xl`}>
          {service.icon || '📱'}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {service.displayName}
            </h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskLevelColor(riskLevel)}`}>
              {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{service.category}</p>
          {service.lastAnalyzed && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              Last analyzed: {formatDate(service.lastAnalyzed)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

const CategoryFilter = ({
  categories,
  selectedCategory,
  onSelectCategory,
}: {
  categories: { id: string; name: string; icon: string }[];
  selectedCategory: string;
  onSelectCategory: (id: string) => void;
}) => (
  <div className="flex flex-wrap gap-2 mb-6">
    {categories.map((category) => (
      <button
        key={category.id}
        onClick={() => onSelectCategory(category.id)}
        className={`px-4 py-2 rounded-full text-sm font-medium flex items-center space-x-2 transition-colors ${
          selectedCategory === category.id
            ? 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400'
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
        }`}
      >
        <span>{category.icon}</span>
        <span>{category.name}</span>
      </button>
    ))}
  </div>
);

const SearchBar = ({ 
  searchQuery, 
  setSearchQuery, 
  showDropdown, 
  setShowDropdown,
  dropdownRef,
  filteredServices,
  onServiceSelect
}: { 
  searchQuery: string; 
  setSearchQuery: (query: string) => void; 
  showDropdown: boolean; 
  setShowDropdown: (show: boolean) => void;
  dropdownRef: React.RefObject<HTMLDivElement>;
  filteredServices: Service[];
  onServiceSelect: (service: Service) => void;
}) => (
  <div className="relative w-full max-w-2xl" ref={dropdownRef}>
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
      <input
        type="text"
        placeholder="Search for apps and services..."
        className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        value={searchQuery}
        onChange={(e) => {
          setSearchQuery(e.target.value);
          setShowDropdown(true);
        }}
        onFocus={() => setShowDropdown(true)}
      />
      {searchQuery && (
        <button
          onClick={() => setSearchQuery('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>

    {showDropdown && searchQuery && (
      <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
        {filteredServices.length > 0 ? (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredServices.map((service: Service) => (
              <button
                key={service.id}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                onClick={() => {
                  onServiceSelect(service);
                  setShowDropdown(false);
                }}
              >
                <div className={`flex-shrink-0 h-8 w-8 rounded-md ${getRiskLevelColor(service.riskLevel)} flex items-center justify-center text-lg`}>
                  {service.icon || '📱'}
                </div>
                <div className="text-left">
                  <div className="font-medium text-gray-900 dark:text-white">{service.displayName}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{service.category}</div>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="px-4 py-6 text-center text-gray-500 dark:text-gray-400">
            <p>No services found</p>
            <p className="text-sm mt-1">Try a different search term or request a new analysis</p>
          </div>
        )}
      </div>
    )}
  </div>
);

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [requestedService, setRequestedService] = useState('');
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeTab, setActiveTab] = useState<'summary' | 'details'>('summary');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Handle service selection
  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    setAnalysisResult({
      ...MOCK_ANALYSIS,
      serviceName: service.displayName,
      score: Math.floor(30 + Math.random() * 60), // Random score between 30-90
    });
    setIsAnalyzing(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsAnalyzing(false);
      // Scroll to results
      document.getElementById('analysis-results')?.scrollIntoView({ behavior: 'smooth' });
    }, 1500);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Add scroll effect for header
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
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

  // Reset analysis when search query changes
  useEffect(() => {
    if (searchQuery === '') {
      setSelectedService(null);
      setAnalysisResult(null);
    }
  }, [searchQuery]);

  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    setSearchQuery('');
    // TODO: Fetch analysis for the selected service
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 1500);
  };

  const handlePasteAnalyze = () => {
    if (!pastedText.trim()) return;
    setIsAnalyzing(true);
    // TODO: Send pasted text to API for analysis
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowPasteModal(false);
    }, 1500);
  };

  const handleRequestService = () => {
    if (!requestedService.trim()) return;
    // TODO: Send service request to backend
    setShowRequestModal(false);
    setRequestedService('');
    alert(`We've received your request for ${requestedService}. We'll analyze it soon!`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-serif font-medium text-gray-900 dark:text-white">
              Terms & Conditions <span className="text-blue-600 dark:text-blue-400">eh</span>
            </h1>
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => setShowPasteModal(true)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <ClipboardPaste className="w-4 h-4 mr-2" />
                Paste T&Cs
              </button>
              <button 
                onClick={() => setShowRequestModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Request Analysis
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}

              {/* Search Bar */}
              <div className="max-w-2xl mx-auto">
                <SearchBar
                  searchQuery={searchQuery}
                  setSearchQuery={setSearchQuery}
                  showDropdown={showDropdown}
                  setShowDropdown={setShowDropdown}
                  dropdownRef={dropdownRef}
                  filteredServices={filteredServices}
                  onServiceSelect={handleServiceSelect}
                />
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-4 border border-gray-300 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="Search for an app or service..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setSelectedService(null)}
            />
          </div>

          {/* Search Results Dropdown */}
          {searchQuery && !selectedService && (
            <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-900 shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 max-h-96 overflow-auto">
              {filteredServices.length > 0 ? (
                <ul className="py-1">
                  {filteredServices.map((service) => (
                    <li key={service.id}>
                      <button
                        onClick={() => handleServiceSelect(service)}
                        className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center"
                      >
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-400 mr-3">
                          {service.displayName.charAt(0)}
                        </div>
                        <div>
                          <p className="text-gray-900 dark:text-white font-medium">
                            {service.displayName}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {service.category}
                          </p>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="px-4 py-6 text-center text-gray-500 dark:text-gray-400">
                  <AlertCircle className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p>No services found</p>
                  <button
                    onClick={() => setShowRequestModal(true)}
                    className="mt-2 text-blue-600 dark:text-blue-400 hover:underline focus:outline-none"
                  >
                    Request analysis for "{searchQuery}"
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Analysis Result */}
        {selectedService && (
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-800 transition-all duration-300">
            <div className="p-6 border-b border-gray-200 dark:border-gray-800">
              <div className="flex items-center">
                <div className="h-12 w-12 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 text-xl font-bold mr-4">
                  {selectedService.displayName.charAt(0)}
                </div>
                <div>
                  <h3 className="text-xl font-medium text-gray-900 dark:text-white">
                    {selectedService.displayName} Terms & Conditions
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Last analyzed: {new Date().toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {isAnalyzing ? (
              <div className="p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Analyzing terms and conditions...</p>
              </div>
            ) : (
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl">
                    <div className="flex items-center mb-2">
                      <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-800 flex items-center justify-center text-green-600 dark:text-green-400 mr-2">
                        ✓
                      </div>
                      <h4 className="font-medium text-green-800 dark:text-green-200">User-Friendly</h4>
                    </div>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      Clear language and reasonable data usage policies
                    </p>
                  </div>
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl">
                    <div className="flex items-center mb-2">
                      <div className="h-8 w-8 rounded-full bg-yellow-100 dark:bg-yellow-800 flex items-center justify-center text-yellow-600 dark:text-yellow-400 mr-2">
                        !
                      </div>
                      <h4 className="font-medium text-yellow-800 dark:text-yellow-200">Moderate Concerns</h4>
                    </div>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      Some clauses require attention
                    </p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl">
                    <div className="flex items-center mb-2">
                      <div className="h-8 w-8 rounded-full bg-red-100 dark:bg-red-800 flex items-center justify-center text-red-600 dark:text-red-400 mr-2">
                        ⚠️
                      </div>
                      <h4 className="font-medium text-red-800 dark:text-red-200">High Risk</h4>
                    </div>
                    <p className="text-sm text-red-700 dark:text-red-300">
                      Several concerning clauses found
                    </p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="border-l-4 border-blue-500 pl-4 py-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">Key Findings</h4>
                    <ul className="mt-2 space-y-2">
                      <li className="flex items-start">
                        <span className="text-green-500 mr-2">✓</span>
                        <span>Clear data deletion process</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-yellow-500 mr-2">⚠️</span>
                        <span>Moderate data sharing with third parties</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-red-500 mr-2">✗</span>
                        <span>Limited control over data retention</span>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Summary</h4>
                    <p className="text-gray-700 dark:text-gray-300 text-sm">
                      The terms are generally reasonable but contain some concerning clauses around data retention and third-party sharing. 
                      Pay special attention to sections 4.2 (Data Usage) and 7.3 (Dispute Resolution).
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Paste Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-900 dark:text-white">Paste Terms & Conditions</h3>
                <button 
                  onClick={() => setShowPasteModal(false)}
                  className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
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
                  {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Request Modal */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-900 dark:text-white">Request Analysis</h3>
                <button 
                  onClick={() => setShowRequestModal(false)}
                  className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
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
