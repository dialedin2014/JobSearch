"""API client service for frontend."""

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 60000, // 60 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for adding auth token
    this.client.interceptors.request.use(
      (config) => {
        // TODO: Add JWT token from local storage or context
        // const token = localStorage.getItem('auth_token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error status
          console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
        } else {
          // Error in request configuration
          console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic GET request
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  // Generic POST request
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  // Generic PUT request
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  // Generic DELETE request
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }

  // Upload file with progress tracking
  async uploadFile<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });

    return response.data;
  }

  /**
   * Poll resume parsing status until completed or timeout.
   * @param resumeId Resume ID to check
   * @param intervalMs Polling interval in milliseconds (default: 2000)
   * @param timeoutMs Timeout in milliseconds (default: 60000)
   * @returns true if parsing succeeded, false otherwise
   */
  async pollResumeStatus(
    resumeId: string,
    intervalMs: number = 2000,
    timeoutMs: number = 60000
  ): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      try {
        const response = await this.get<any>(`/api/v1/resumes/${resumeId}/status`);
        
        if (response.status === 'parsed_success') {
          return true;
        } else if (response.status === 'parsing_failed') {
          return false;
        }
        
        // Still parsing, wait before next check
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      } catch (error) {
        console.error('Error polling resume status:', error);
        return false;
      }
    }

    // Timeout
    console.warn('Resume parsing status check timed out');
    return false;
  }

  /**
   * Poll ally deduction analysis status until completed or timeout.
   * @param analysisId Analysis ID to check
   * @param intervalMs Polling interval in milliseconds (default: 2000)
   * @param timeoutMs Timeout in milliseconds (default: 120000)
   * @returns Analysis results if succeeded, null otherwise
   */
  async pollAnalysisStatus(
    analysisId: string,
    intervalMs: number = 2000,
    timeoutMs: number = 120000
  ): Promise<any | null> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      try {
        const statusResponse = await this.get<any>(`/api/v1/ally-deduction/${analysisId}/status`);
        
        if (statusResponse.status === 'completed') {
          // Fetch full results
          const resultsResponse = await this.get<any>(`/api/v1/ally-deduction/${analysisId}/results`);
          return resultsResponse;
        } else if (statusResponse.status === 'failed') {
          console.error('Analysis failed:', statusResponse);
          return null;
        }
        
        // Still processing, wait before next check
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      } catch (error) {
        console.error('Error polling analysis status:', error);
        return null;
      }
    }

    // Timeout
    console.warn('Analysis status check timed out');
    return null;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
