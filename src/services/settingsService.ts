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

export interface JobSearchService {
  enabled: boolean;
  name: string;
  description: string;
  requires_api_key: boolean;
  has_api_key?: boolean;
}

export interface JobSearchServicesResponse {
  services: {
    [key: string]: JobSearchService;
  };
}

class SettingsService {
  async getJobSearchServices(): Promise<JobSearchServicesResponse> {
    const response = await apiClient.get('/api/settings/job-search-services');
    return response.data;
  }
}

export const settingsService = new SettingsService();