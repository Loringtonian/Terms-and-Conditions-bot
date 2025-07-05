import { Clock, ArrowRight } from 'lucide-react';
import { Service } from '@/types';

interface ServiceCardProps {
  service: Service;
  onClick: () => void;
}

const ServiceCard = ({ service, onClick }: ServiceCardProps) => {
  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getRiskLevelText = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'high': return 'High Risk';
      case 'medium': return 'Medium Risk';
      case 'low': return 'Low Risk';
      default: return 'Unknown Risk';
    }
  };

  return (
    <div 
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition-shadow cursor-pointer group"
    >
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 h-12 w-12 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-2xl">
              {service.icon || '📱'}
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {service.displayName}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">{service.category}</p>
            </div>
          </div>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskLevelColor(service.riskLevel)}`}>
            {getRiskLevelText(service.riskLevel)}
          </span>
        </div>
        
        {service.lastAnalyzed && (
          <div className="mt-4 flex items-center text-sm text-gray-500 dark:text-gray-400">
            <Clock className="h-4 w-4 mr-1.5" />
            <span>Analyzed {new Date(service.lastAnalyzed).toLocaleDateString()}</span>
          </div>
        )}
        
        <div className="mt-4 flex justify-end">
          <button
            type="button"
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 dark:text-primary-200 dark:bg-primary-900/30 dark:hover:bg-primary-800/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            View Analysis
            <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ServiceCard;
