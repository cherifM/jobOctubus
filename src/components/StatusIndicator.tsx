import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { statusService, SystemStatus, ServiceStatus } from '../services/statusService';

const StatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    checkStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const statusData = await statusService.getSystemStatus();
      setStatus(statusData);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (serviceStatus: ServiceStatus) => {
    switch (serviceStatus.status) {
      case 'connected':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircleIcon className="w-4 h-4 text-red-500" />;
      case 'timeout':
        return <ClockIcon className="w-4 h-4 text-yellow-500" />;
      default:
        return <ExclamationTriangleIcon className="w-4 h-4 text-gray-400" />;
    }
  };

  const getOverallStatusColor = (overall: string) => {
    switch (overall) {
      case 'healthy':
        return 'bg-green-500';
      case 'partial':
        return 'bg-yellow-500';
      case 'unhealthy':
        return 'bg-red-500';
      case 'checking':
        return 'bg-blue-500 animate-pulse';
      default:
        return 'bg-gray-400';
    }
  };

  const getOverallStatusText = (overall: string) => {
    switch (overall) {
      case 'healthy':
        return 'All services operational';
      case 'partial':
        return 'Some services unavailable';
      case 'unhealthy':
        return 'Services unavailable';
      case 'checking':
        return 'Checking services...';
      default:
        return 'Status unknown';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
        <span>Checking services...</span>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
        <span>Status unavailable</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center space-x-2 text-sm hover:bg-gray-50 px-2 py-1 rounded transition-colors"
      >
        <div className={`w-2 h-2 rounded-full ${getOverallStatusColor(status.overall)}`}></div>
        <span className="text-gray-700">{getOverallStatusText(status.overall)}</span>
      </button>

      {expanded && (
        <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 min-w-[280px] z-50">
          <h3 className="font-medium text-gray-900 mb-2">Service Status</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.openrouter)}
                <span className="text-sm text-gray-700">OpenRouter AI</span>
              </div>
              <span className="text-xs text-gray-500">{status.openrouter.response_time}ms</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.arbeitsagentur)}
                <span className="text-sm text-gray-700">Arbeitsagentur</span>
              </div>
              <span className="text-xs text-gray-500">{status.arbeitsagentur.response_time}ms</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.remoteok)}
                <span className="text-sm text-gray-700">RemoteOK</span>
              </div>
              <span className="text-xs text-gray-500">{status.remoteok.response_time}ms</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.adzuna)}
                <span className="text-sm text-gray-700">Adzuna (Germany)</span>
              </div>
              <span className="text-xs text-gray-500">{status.adzuna.response_time}ms</span>
            </div>
          </div>
          
          <div className="mt-3 pt-2 border-t border-gray-100">
            <button
              onClick={checkStatus}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Refresh status
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusIndicator;