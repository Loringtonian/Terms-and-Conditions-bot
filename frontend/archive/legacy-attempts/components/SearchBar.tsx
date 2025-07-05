import { Search, X } from 'lucide-react';
import { Service } from '../types';

interface SearchBarProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  showDropdown: boolean;
  setShowDropdown: (show: boolean) => void;
  dropdownRef: React.RefObject<HTMLDivElement>;
  filteredServices: Service[];
  onServiceSelect: (service: Service) => void;
}

export const SearchBar = ({
  searchQuery,
  setSearchQuery,
  showDropdown,
  setShowDropdown,
  dropdownRef,
  filteredServices,
  onServiceSelect
}: SearchBarProps) => {
  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'high': return 'bg-red-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  return (
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
              {filteredServices.map((service) => (
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
};

export default SearchBar;
