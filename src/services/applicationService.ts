import apiClient from './authService';
import { Job } from './jobService';
import { CV } from './cvService';

export interface Application {
  id: number;
  status: string;
  cover_letter?: string;
  adapted_cv_content?: Record<string, any>;
  notes?: string;
  user_id: number;
  job_id: number;
  cv_id: number;
  created_at: string;
  updated_at?: string;
  applied_date?: string;
  response_date?: string;
  interview_date?: string;
  job: Job;
  cv: CV;
}

export interface ApplicationCreate {
  job_id: number;
  cv_id: number;
  status?: string;
  cover_letter?: string;
  notes?: string;
}

export interface CoverLetterRequest {
  job_id: number;
  cv_id: number;
  tone?: string;
  length?: string;
  custom_points?: string[];
}

export const applicationService = {
  async getApplications(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<Application[]> {
    const response = await apiClient.get('/api/applications/', { params });
    return response.data;
  },

  async getApplication(applicationId: number): Promise<Application> {
    const response = await apiClient.get(`/api/applications/${applicationId}`);
    return response.data;
  },

  async createApplication(applicationData: ApplicationCreate): Promise<Application> {
    const response = await apiClient.post('/api/applications/', applicationData);
    return response.data;
  },

  async updateApplication(applicationId: number, updates: Partial<Application>): Promise<Application> {
    const response = await apiClient.put(`/api/applications/${applicationId}`, updates);
    return response.data;
  },

  async generateCoverLetter(applicationId: number, request: CoverLetterRequest): Promise<{ cover_letter: string }> {
    const response = await apiClient.post(
      `/api/applications/${applicationId}/cover-letter`,
      request
    );
    return response.data;
  },

  async deleteApplication(applicationId: number): Promise<void> {
    await apiClient.delete(`/api/applications/${applicationId}`);
  },
};