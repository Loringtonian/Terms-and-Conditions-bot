import { AnalysisResult } from '@/types/analysis';
import { AlertTriangle, Info, Shield, ShieldAlert, ShieldCheck, Search, HelpCircle, ExternalLink } from 'lucide-react';

interface AnalysisResultProps {
  analysis: AnalysisResult;
}

const getSeverityIcon = (severity: 'low' | 'medium' | 'high') => {
  switch (severity) {
    case 'high':
      return <ShieldAlert className="h-5 w-5 text-red-500" />;
    case 'medium':
      return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    case 'low':
      return <ShieldCheck className="h-5 w-5 text-green-500" />;
    default:
      return <Shield className="h-5 w-5 text-gray-500" />;
  }
};

const getSeverityColor = (severity: 'low' | 'medium' | 'high') => {
  switch (severity) {
    case 'high':
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
  }
};

export const AnalysisResult = ({ analysis }: AnalysisResultProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 7) return 'text-green-600 dark:text-green-400';
    if (score >= 4) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {analysis.app_name}
            </h1>
            {analysis.terms_url && (
              <a
                href={analysis.terms_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline dark:text-blue-400"
              >
                View Original Terms
              </a>
            )}
          </div>
          <div className="mt-4 md:mt-0">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gray-100 dark:bg-gray-700">
              <span className={`text-2xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                {analysis.overall_score.toFixed(1)}
              </span>
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-300">Overall Score</span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Summary</h2>
        <p className="text-gray-700 dark:text-gray-300">{analysis.summary}</p>
      </div>

      {/* Red Flags */}
      {analysis.red_flags && analysis.red_flags.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-red-200 dark:border-red-900/50 p-6">
          <h2 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Potential Red Flags
          </h2>
          <ul className="space-y-3">
            {analysis.red_flags.map((flag, index) => (
              <li key={index} className="flex items-start">
                <span className="text-red-500 mr-2 mt-0.5">•</span>
                <span className="text-gray-700 dark:text-gray-300">{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Privacy Concerns */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Privacy Concerns</h2>
        
        {analysis.privacy_concerns.map((concern, index) => {
          const hasDeepAnalysis = analysis.deep_analysis && analysis.deep_analysis[index];
          const deepAnalysis = hasDeepAnalysis ? analysis.deep_analysis[index] : null;
          
          return (
            <div 
              key={index} 
              className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className={`p-4 ${getSeverityColor(concern.severity)} flex items-center`}>
                {getSeverityIcon(concern.severity)}
                <h3 className="ml-2 font-medium">{concern.clause}</h3>
                {hasDeepAnalysis && (
                  <span className="ml-2 inline-flex items-center text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                    <Search className="h-3 w-3 mr-1" />
                    Deep Analysis Available
                  </span>
                )}
                <span className="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full bg-white/30 dark:bg-black/30">
                  {concern.severity.charAt(0).toUpperCase() + concern.severity.slice(1)} Risk
                </span>
              </div>
              
              <div className="p-6">
                <p className="text-gray-700 dark:text-gray-300 mb-4">{concern.explanation}</p>
                
                <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border-l-4 border-gray-300 dark:border-gray-600">
                  <p className="text-sm italic text-gray-600 dark:text-gray-400">
                    "{concern.quote}"
                  </p>
                </div>

                {/* Deep Analysis Section */}
                {hasDeepAnalysis && deepAnalysis && (
                  <div className="mt-6 border-t border-gray-200 dark:border-gray-700 pt-6">
                    <div className="flex items-center mb-4">
                      <Search className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-2" />
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white">Deep Analysis</h4>
                    </div>

                    {/* Practical Meaning */}
                    {deepAnalysis.practical_meaning && (
                      <div className="mb-6">
                        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center">
                          <Info className="h-4 w-4 mr-1" />
                          What This Actually Means
                        </h5>
                        <p className="text-gray-600 dark:text-gray-400 text-sm bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                          {deepAnalysis.practical_meaning}
                        </p>
                      </div>
                    )}

                    {/* Unclear Terms */}
                    {deepAnalysis.unclear_terms && deepAnalysis.unclear_terms.length > 0 && (
                      <div className="mb-6">
                        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                          <HelpCircle className="h-4 w-4 mr-1" />
                          Unclear Legal Terms Explained
                        </h5>
                        <div className="space-y-4">
                          {deepAnalysis.unclear_terms.map((term, termIndex) => (
                            <div key={termIndex} className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-900/50">
                              <h6 className="font-medium text-gray-900 dark:text-white text-sm mb-2">
                                "{term.term}"
                              </h6>
                              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                                {term.explanation}
                              </p>
                              <div className="text-sm">
                                <span className="font-medium text-gray-600 dark:text-gray-400">Impact: </span>
                                <span className="text-gray-600 dark:text-gray-400">{term.user_impact}</span>
                              </div>
                              {term.questions_to_ask && term.questions_to_ask.length > 0 && (
                                <div className="mt-3">
                                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 block">
                                    Questions to ask:
                                  </span>
                                  <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                                    {term.questions_to_ask.map((question, qIndex) => (
                                      <li key={qIndex} className="flex items-start">
                                        <span className="text-gray-400 mr-1 mt-0.5">•</span>
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

                    {/* User Action Needed */}
                    {deepAnalysis.user_action_needed && (
                      <div className="mb-6">
                        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center">
                          <AlertTriangle className="h-4 w-4 mr-1" />
                          Recommended Actions
                        </h5>
                        <p className="text-gray-600 dark:text-gray-400 text-sm bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
                          {deepAnalysis.user_action_needed}
                        </p>
                      </div>
                    )}

                    {/* Online Research */}
                    {deepAnalysis.online_research && deepAnalysis.online_research.top_result_url && (
                      <div className="mb-4">
                        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center">
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Additional Research
                        </h5>
                        <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                          <a 
                            href={deepAnalysis.online_research.top_result_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline dark:text-blue-400 flex items-center"
                          >
                            {deepAnalysis.online_research.top_result_title || 'Related Information'}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                          {deepAnalysis.online_research.summary && (
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {deepAnalysis.online_research.summary}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">User Friendliness</h3>
          <p className={`text-3xl font-bold ${getScoreColor(analysis.user_friendliness_score)}`}>
            {analysis.user_friendliness_score.toFixed(1)}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">/ 10.0</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Data Collection</h3>
          <p className={`text-3xl font-bold ${getScoreColor(10 - analysis.data_collection_score)}`}>
            {(10 - analysis.data_collection_score).toFixed(1)}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">/ 10.0 (lower is better)</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Legal Complexity</h3>
          <p className={`text-3xl font-bold ${getScoreColor(10 - analysis.legal_complexity_score)}`}>
            {(10 - analysis.legal_complexity_score).toFixed(1)}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">/ 10.0 (lower is better)</p>
        </div>
      </div>

      {/* Analysis Metadata */}
      <div className="text-sm text-gray-500 dark:text-gray-400 text-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <p>Analysis performed on {new Date(analysis.analysis_date).toLocaleDateString()}</p>
        <p className="mt-1">
          <span className="inline-flex items-center">
            <Info className="h-4 w-4 mr-1" />
            This analysis is for informational purposes only and does not constitute legal advice.
          </span>
        </p>
      </div>
    </div>
  );
};

export default AnalysisResult;
