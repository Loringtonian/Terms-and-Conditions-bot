'use client';

import { useState } from 'react';
import { FileText, Search, Loader2 } from 'lucide-react';

// Types
type AnalysisResult = {
  id: string;
  app_name: string;
  app_version: string | null;
  overall_score: number;
  privacy_concerns: Array<{
    clause: string;
    severity: 'low' | 'medium' | 'high';
    explanation: string;
    quote: string;
  }>;
  summary: string;
  red_flags: string[];
  user_friendliness_score: number;
  data_collection_score: number;
  legal_complexity_score: number;
  terms_version: string | null;
  terms_url: string;
  analysis_date: string;
};

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/analyze?service=${encodeURIComponent(searchQuery)}`);
      // const data = await response.json();
      // setAnalysisResult(data);
      
      // Simulating API call
      setTimeout(() => {
        setAnalysisResult({
          id: '1',
          app_name: searchQuery,
          app_version: '1.0.0',
          overall_score: 7.5,
          privacy_concerns: [
            {
              clause: 'Data Collection',
              severity: 'high',
              explanation: 'Collects extensive user data',
              quote: 'We collect information about...'
            }
          ],
          summary: 'This is a placeholder analysis result.',
          red_flags: ['Extensive data collection', 'Vague terms'],
          user_friendliness_score: 6.0,
          data_collection_score: 8.5,
          legal_complexity_score: 7.0,
          terms_version: '1.0',
          terms_url: 'https://example.com/terms',
          analysis_date: new Date().toISOString()
        });
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error analyzing terms:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Terms and Conditions Analyzer
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter a service name..."
              className="flex-1 p-2 border border-gray-300 rounded"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !searchQuery.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
              {isLoading ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
        </div>

        {isLoading && (
          <div className="mt-8 text-center">
            <Loader2 className="w-8 h-8 mx-auto animate-spin text-blue-600" />
            <p className="mt-2 text-gray-600">Analyzing terms and conditions...</p>
          </div>
        )}

        {analysisResult && (
          <div className="mt-8 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">
              Analysis for {analysisResult.app_name}
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium">Overall Score</h3>
                <div className="w-full bg-gray-200 rounded-full h-4 mt-1">
                  <div 
                    className="bg-blue-600 h-4 rounded-full" 
                    style={{ width: `${analysisResult.overall_score * 10}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {analysisResult.overall_score.toFixed(1)}/10
                </p>
              </div>

              <div>
                <h3 className="font-medium">Summary</h3>
                <p className="text-gray-700">{analysisResult.summary}</p>
              </div>

              {analysisResult.privacy_concerns.length > 0 && (
                <div>
                  <h3 className="font-medium">Privacy Concerns</h3>
                  <ul className="list-disc pl-5 space-y-2 mt-1">
                    {analysisResult.privacy_concerns.map((concern, index) => (
                      <li key={index} className="text-gray-700">
                        <span className="font-medium">{concern.clause}:</span>{' '}
                        {concern.explanation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <h3 className="font-medium">Red Flags</h3>
                <ul className="list-disc pl-5 space-y-1 mt-1">
                  {analysisResult.red_flags.map((flag, index) => (
                    <li key={index} className="text-red-600">{flag}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
