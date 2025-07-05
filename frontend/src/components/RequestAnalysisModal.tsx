'use client';

import { useState, useEffect } from 'react';
import { X, Loader2, Search } from 'lucide-react';

interface RequestAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (serviceName: string, knownUrl?: string) => Promise<void>;
  isProcessing: boolean;
}

export default function RequestAnalysisModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  isProcessing 
}: RequestAnalysisModalProps) {
  const [serviceName, setServiceName] = useState('');
  const [knownUrl, setKnownUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen && !isProcessing) {
        event.preventDefault();
        event.stopPropagation();
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape, true);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape, true);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, isProcessing]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!serviceName.trim()) {
      setError('Please enter a service name');
      return;
    }

    setError(null);
    
    try {
      await onSubmit(serviceName.trim(), knownUrl.trim() || undefined);
      setServiceName('');
      setKnownUrl('');
    } catch (err) {
      setError('Failed to submit request. Please try again.');
      console.error('Request error:', err);
    }
  };

  const handleClose = () => {
    if (!isProcessing) {
      setServiceName('');
      setKnownUrl('');
      setError(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl">
        <div className="p-6 border-b border-slate-200 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-light text-slate-900">Request New Analysis</h2>
            <p className="text-sm text-slate-500 mt-1">
              We'll scrape and analyze the terms for any service
            </p>
          </div>
          <button 
            onClick={handleClose}
            className="text-slate-400 hover:text-slate-700 transition-colors"
            disabled={isProcessing}
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {isProcessing && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <Loader2 className="animate-spin h-5 w-5 text-blue-600 mr-3" />
                <div>
                  <p className="text-blue-800 font-medium">Processing your request...</p>
                  <p className="text-blue-600 text-sm">
                    We're searching for and analyzing the terms and conditions with AI. 
                    This usually takes 30-60 seconds.
                  </p>
                </div>
              </div>
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="service-name" className="block text-sm font-medium text-slate-700 mb-2">
                Service Name *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  id="service-name"
                  type="text"
                  className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 text-sm"
                  placeholder="e.g., Discord, Slack, Zoom, TikTok..."
                  value={serviceName}
                  onChange={(e) => setServiceName(e.target.value)}
                  disabled={isProcessing}
                  required
                />
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Enter the name of any app, website, or service
              </p>
            </div>

            <div>
              <label htmlFor="known-url" className="block text-sm font-medium text-slate-700 mb-2">
                Terms URL (Optional)
              </label>
              <input
                id="known-url"
                type="url"
                className="block w-full px-3 py-3 border border-slate-200 rounded-xl focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 text-sm"
                placeholder="https://example.com/terms"
                value={knownUrl}
                onChange={(e) => setKnownUrl(e.target.value)}
                disabled={isProcessing}
              />
              <p className="text-xs text-slate-500 mt-1">
                If you know the direct link to their terms, include it here for faster processing
              </p>
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-slate-200">
            <button
              type="button"
              onClick={handleClose}
              disabled={isProcessing}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isProcessing || !serviceName.trim()}
              className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 flex items-center justify-center min-w-[120px]"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Processing...
                </>
              ) : (
                'Start Analysis'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}