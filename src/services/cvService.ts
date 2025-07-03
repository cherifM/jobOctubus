import apiClient from './authService';

export interface CV {
  id: number;
  title: string;
  language: string;
  content: Record<string, any>;
  skills: string[];
  experience: any[];
  education: any[];
  personal_info: Record<string, any>;
  is_base_cv: boolean;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CVCreate {
  title: string;
  language: string;
  content: Record<string, any>;
  skills: string[];
  experience: any[];
  education: any[];
  personal_info: Record<string, any>;
  is_base_cv?: boolean;
}

export interface CVAdaptationRequest {
  cv_id: number;
  job_id: number;
  focus_areas?: string[];
}

export const cvService = {
  async getCVs(params?: {
    skip?: number;
    limit?: number;
  }): Promise<CV[]> {
    const response = await apiClient.get('/api/cvs/', { params });
    return response.data;
  },

  async getCV(cvId: number): Promise<CV> {
    const response = await apiClient.get(`/api/cvs/${cvId}`);
    return response.data;
  },

  async createCV(cvData: CVCreate): Promise<CV> {
    const response = await apiClient.post('/api/cvs/', cvData);
    return response.data;
  },

  async uploadCV(file: File, title: string, language: string = 'en'): Promise<CV> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('language', language);

    const response = await apiClient.post('/api/cvs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async updateCV(cvId: number, updates: Partial<CV>): Promise<CV> {
    const response = await apiClient.put(`/api/cvs/${cvId}`, updates);
    return response.data;
  },

  async adaptCV(adaptationRequest: CVAdaptationRequest): Promise<CV> {
    const response = await apiClient.post(
      `/api/cvs/${adaptationRequest.cv_id}/adapt`,
      adaptationRequest
    );
    return response.data;
  },

  async deleteCV(cvId: number): Promise<void> {
    await apiClient.delete(`/api/cvs/${cvId}`);
  },

  async initializeFromWebsite(): Promise<CV[]> {
    const response = await apiClient.post('/api/cvs/initialize-from-website');
    return response.data;
  },
};