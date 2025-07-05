'use client';

import { useState, useEffect } from 'react';
import { X, Loader2, FileText } from 'lucide-react';

interface TermsViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  serviceId: string;
  serviceName: string;
  highlightText?: string;
  isPastedTerms?: boolean;
  pastedTermsText?: string;
}

export default function TermsViewerModal({ 
  isOpen, 
  onClose, 
  serviceId, 
  serviceName, 
  highlightText = '',
  isPastedTerms = false,
  pastedTermsText = ''
}: TermsViewerModalProps) {
  const [termsText, setTermsText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && !isPastedTerms) {
      fetchTerms();
    } else if (isOpen && isPastedTerms && pastedTermsText) {
      setTermsText(pastedTermsText);
    }
  }, [isOpen, serviceId, isPastedTerms, pastedTermsText]);

  const fetchTerms = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5001/terms/${serviceId}`, {
        mode: 'cors',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTermsText(data.terms_text || '');
    } catch (err) {
      console.error('Error fetching terms:', err);
      setError('Failed to load terms and conditions text');
    } finally {
      setIsLoading(false);
    }
  };

  const highlightTextInContent = (content: string, searchText: string) => {
    if (!searchText.trim() || searchText.length < 5) return content;
    
    console.log('Highlighting text:', searchText);
    
    // Remove quotes if they wrap the entire text
    let cleanText = searchText.trim();
    if (cleanText.startsWith('"') && cleanText.endsWith('"')) {
      cleanText = cleanText.slice(1, -1);
    }
    
    // Skip if the text is too short to be meaningful
    if (cleanText.length < 10) return content;
    
    // Try to find substantial phrases (10+ characters) within the search text
    // Split by periods, commas, and "such as" to get meaningful chunks
    const chunks = cleanText.split(/[.,;]|such as|including|for example/).map(chunk => chunk.trim()).filter(chunk => chunk.length > 15);
    
    if (chunks.length === 0) {
      // Fall back to the full text if it's substantial
      if (cleanText.length > 20) {
        chunks.push(cleanText);
      } else {
        return content;
      }
    }
    
    console.log('Text chunks to highlight:', chunks);
    
    let result = content;
    
    // Highlight each chunk
    chunks.forEach(chunk => {
      // Escape special regex characters
      const escapedChunk = chunk.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      // Allow for some flexibility in whitespace
      const flexibleChunk = escapedChunk.replace(/\s+/g, '\\s+');
      const regex = new RegExp(`(${flexibleChunk})`, 'gi');
      result = result.replace(regex, '<mark class="bg-yellow-300 font-medium px-1 rounded">$1</mark>');
    });
    
    return result;
  };

  const processedContent = highlightText ? 
    highlightTextInContent(termsText, highlightText) : 
    termsText;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-slate-200 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center">
            <FileText className="h-6 w-6 text-slate-600 mr-3" />
            <div>
              <h2 className="text-xl font-light text-slate-900">
                {serviceName} - Terms & Conditions
              </h2>
              {highlightText && (
                <p className="text-sm text-slate-500 mt-1">
                  Highlighting: "{highlightText}"
                </p>
              )}
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <div className="flex-1 overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="animate-spin h-8 w-8 text-slate-500 mx-auto mb-4" />
                <p className="text-slate-600">Loading terms...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-red-600">
                <p className="text-lg font-medium mb-2">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          ) : (
            <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
              <div 
                className="prose prose-slate max-w-none text-sm leading-relaxed whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ 
                  __html: processedContent 
                }}
              />
            </div>
          )}
        </div>
        
        <div className="p-4 border-t border-slate-200 bg-slate-50 rounded-b-2xl flex-shrink-0">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}