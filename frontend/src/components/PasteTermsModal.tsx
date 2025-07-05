'use client';

import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';

interface PasteTermsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalyze: (text: string) => Promise<void>;
}

export default function PasteTermsModal({ isOpen, onClose, onAnalyze }: PasteTermsModalProps) {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please paste some terms and conditions text');
      return;
    }

    setError(null);
    setIsLoading(true);
    
    try {
      await onAnalyze(text);
      setText('');
      onClose();
    } catch (err) {
      setError('Failed to analyze the text. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-xl font-light text-slate-900">Paste Terms & Conditions</h2>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 transition-colors"
            disabled={isLoading}
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col overflow-hidden">
          <div className="p-6 flex-1 overflow-auto">
            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <label htmlFor="terms-text" className="block text-sm font-medium text-slate-700">
                Paste the full terms and conditions text below:
              </label>
              <div className="relative">
                <textarea
                  id="terms-text"
                  rows={12}
                  className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-slate-300 focus:ring focus:ring-slate-200 focus:ring-opacity-50 text-sm"
                  placeholder="Paste terms and conditions here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  disabled={isLoading}
                />
              </div>
              <p className="text-xs text-slate-500 mt-1">
                We'll analyze the text using AI to identify key privacy concerns and terms.
              </p>
            </div>
          </div>
          
          <div className="p-6 border-t border-slate-200 bg-slate-50 rounded-b-2xl">
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !text.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-xl hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 disabled:opacity-50 flex items-center justify-center min-w-[100px]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                    Analyzing...
                  </>
                ) : (
                  'Analyze Text'
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
