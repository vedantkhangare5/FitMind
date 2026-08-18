/* eslint-disable @typescript-eslint/no-explicit-any */
export class ApiError extends Error {
  public status: number;
  public code?: string;
  public details?: any;

  constructor(message: string, status: number, code?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (options.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method.toUpperCase())) {
    headers['X-FitMind-CSRF'] = '1';
  }

  const response = await fetch(url, {
    cache: 'no-store', // Prevent browser caching of authenticated data
    ...options,
    credentials: 'include',
    headers,
  });

  let data;
  const isJson = response.headers.get('content-type')?.includes('application/json');
  
  if (isJson) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    let message = 'An unknown error occurred';
    let code;
    let details;

    if (isJson && data) {
      if (data.error && data.error.message) {
        message = data.error.message;
        code = data.error.code;
        details = data.error.details;
      } else if (data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].type) {
            code = "VALIDATION_ERROR";
            details = data.detail;
        }
      } else {
        message = JSON.stringify(data);
      }
    } else {
      message = data as string || response.statusText;
    }

    throw new ApiError(message, response.status, code, details);
  }

  return data as T;
}

export const api = {
  // Auth
  login: (data: any) => fetchApi<any>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  register: (data: any) => fetchApi<any>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  logout: () => fetchApi<any>('/api/auth/logout', {
    method: 'POST',
  }),

  // Profile
  getProfile: () => fetchApi<any>('/api/profile'),
  updateProfile: (data: any) => fetchApi<any>('/api/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteProfile: () => fetchApi<any>('/api/profile', {
    method: 'DELETE',
  }),

  // Progress
  getProgress: () => fetchApi<any>('/api/progress'),
  addProgress: (data: any) => fetchApi<any>('/api/progress', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteProgress: (id: number) => fetchApi<any>(`/api/progress/${id}`, {
    method: 'DELETE',
  }),

  // Behavior
  getBehaviorSummary: () => fetchApi<any>('/api/behavior/summary'),
  getNutritionLogs: () => fetchApi<any>('/api/behavior/nutrition'),
  addNutritionLog: (data: any) => fetchApi<any>('/api/behavior/nutrition', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteNutritionLog: (date: string) => fetchApi<any>(`/api/behavior/nutrition/${date}`, {
    method: 'DELETE',
  }),
  
  getWorkoutLogs: () => fetchApi<any>('/api/behavior/workouts'),
  addWorkoutLog: (data: any) => fetchApi<any>('/api/behavior/workouts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteWorkoutLog: (id: number) => fetchApi<any>(`/api/behavior/workouts/${id}`, {
    method: 'DELETE',
  }),

  // Agent
  askAgent: (data: any) => fetchApi<any>('/api/agent/ask', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  coach: (data: any) => fetchApi<any>('/api/coach', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Calculator
  calculateFitness: (data: any) => fetchApi<any>('/api/fitness/calculate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
