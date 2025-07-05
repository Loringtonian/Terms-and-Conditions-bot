export interface PrivacyConcern {
  clause: string;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
  quote: string;
}

export interface UnclearTerm {
  term: string;
  explanation: string;
  user_impact: string;
  questions_to_ask: string[];
}

export interface DeepAnalysis {
  unclear_terms: UnclearTerm[];
  practical_meaning: string;
  user_action_needed: string;
  severity_justification: string;
  extended_context?: string;
  online_research?: {
    search_query: string;
    top_result_url?: string;
    top_result_title?: string;
    summary?: string;
  };
}

export interface AnalysisResult {
  app_name: string;
  app_version: string | null;
  overall_score: number;
  privacy_concerns: PrivacyConcern[];
  summary: string;
  red_flags: string[];
  user_friendliness_score: number;
  data_collection_score: number;
  legal_complexity_score: number;
  terms_version: string | null;
  terms_url: string;
  analysis_date: string;
  deep_analysis?: {
    [concernIndex: number]: DeepAnalysis;
  };
}

export interface ServiceAnalysis extends AnalysisResult {
  id: string;
  lastAnalyzed: string;
  riskLevel: 'low' | 'medium' | 'high';
}
