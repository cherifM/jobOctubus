import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface ServiceStatus {
  status: 'connected' | 'error' | 'timeout' | 'unknown';
  message: string;
  response_time: number;
}

export interface SystemStatus {
  openrouter: ServiceStatus;
  arbeitsagentur: ServiceStatus;
  remoteok: ServiceStatus;
  adzuna: ServiceStatus;
  overall: 'healthy' | 'partial' | 'unhealthy' | 'checking' | 'error';
}

export const statusService = {
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await apiClient.get('/api/status/health');
    return response.data;
  }
};