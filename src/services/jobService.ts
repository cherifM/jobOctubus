import apiClient from './authService';

export interface Job {
  id: number;
  external_id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string;
  salary_range?: string;
  job_type: string;
  remote_option: boolean;
  posted_date: string;
  deadline?: string;
  source: string;
  url: string;
  skills_required: string[];
  experience_level: string;
  match_score?: number;
  created_at: string;
}

export interface JobSearchRequest {
  query: string;
  location?: string;
  remote_only?: boolean;
  experience_level?: string;
  job_type?: string;
  salary_min?: number;
  max_results?: number;
}

export const jobService = {
  async searchJobs(searchRequest: JobSearchRequest): Promise<Job[]> {
    const response = await apiClient.post('/api/jobs/search', searchRequest);
    return response.data;
  },

  async getJobs(params?: {
    skip?: number;
    limit?: number;
    location?: string;
    company?: string;
  }): Promise<Job[]> {
    const response = await apiClient.get('/api/jobs/', { params });
    return response.data;
  },

  async getJob(jobId: number): Promise<Job> {
    const response = await apiClient.get(`/api/jobs/${jobId}`);
    return response.data;
  },

  async createJob(jobData: Omit<Job, 'id' | 'created_at'>): Promise<Job> {
    const response = await apiClient.post('/api/jobs/', jobData);
    return response.data;
  },

  async updateJob(jobId: number, updates: Partial<Job>): Promise<Job> {
    const response = await apiClient.put(`/api/jobs/${jobId}`, updates);
    return response.data;
  },

  async deleteJob(jobId: number): Promise<void> {
    await apiClient.delete(`/api/jobs/${jobId}`);
  },
};