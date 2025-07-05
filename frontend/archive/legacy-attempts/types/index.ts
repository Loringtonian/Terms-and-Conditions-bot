export interface Service {
  id: string;
  name: string;
  displayName: string;
  category: string;
  icon: string;
  riskLevel: 'low' | 'medium' | 'high';
  lastAnalyzed: string;
  hasAnalysis?: boolean;
  legalName?: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
  count: number;
}

export interface AnalysisSection {
  title: string;
  description: string;
  score: number;
  concerns: string[];
  recommendations: string[];
}
