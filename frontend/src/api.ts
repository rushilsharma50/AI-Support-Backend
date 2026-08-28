const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(status: number, data: any, message: string) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Clear token if unauthorized to force re-login
    localStorage.removeItem('access_token');
    if (window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
  }

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }
    throw new ApiError(response.status, errorData, errorData.detail || 'API request failed');
  }

  // 204 No Content
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  get: (endpoint: string) => fetchWithAuth(endpoint),
  post: (endpoint: string, data: any, isFormData = false) => fetchWithAuth(endpoint, {
    method: 'POST',
    body: isFormData ? data : JSON.stringify(data),
    headers: isFormData ? undefined : { 'Content-Type': 'application/json' },
  }),
  put: (endpoint: string, data: any) => fetchWithAuth(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (endpoint: string) => fetchWithAuth(endpoint, { method: 'DELETE' }),
};
