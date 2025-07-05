export interface Service {
  id: string;
  displayName: string;
  legalName: string;
  category: string;
  icon?: string;
  riskLevel?: 'low' | 'medium' | 'high';
  lastAnalyzed?: string;
}

export interface AnalysisResult {
  id: string;
  serviceName: string;
  score: number;
  summary: string;
  lastUpdated: string;
  analyzedAt: string;
  keyPoints: {
    title: string;
    description: string;
    impact: 'positive' | 'neutral' | 'negative';
  }[];
  sections: {
    title: string;
    description: string;
    score: number;
    concerns: string[];
    recommendations: string[];
  }[];
}

export interface Category {
  id: string;
  name: string;
  count: number;
  icon: string;
}

export interface SearchBarProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  showDropdown: boolean;
  setShowDropdown: (show: boolean) => void;
  dropdownRef: React.RefObject<HTMLDivElement>;
  filteredServices: Service[];
  onServiceSelect: (service: Service) => void;
}
