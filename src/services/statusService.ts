import api from './api';

export interface ServiceStatus {
  status: 'connected' | 'error' | 'timeout' | 'unknown';
  message: string;
  response_time: number;
}

export interface SystemStatus {
  openrouter: ServiceStatus;
  arbeitsagentur: ServiceStatus;
  remoteok: ServiceStatus;
  thelocal: ServiceStatus;
  overall: 'healthy' | 'partial' | 'unhealthy' | 'checking' | 'error';
}

export const statusService = {
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await api.get('/api/status/health');
    return response.data;
  }
};