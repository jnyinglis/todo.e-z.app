import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';

type LoginCredentials = {
  email: string;
  password: string;
};

type RegisterData = {
  email: string;
  password: string;
  full_name?: string;
};

type User = {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
};

type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: Error) => void;
  }> = [];

  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Include cookies in requests
    });

    // Add request interceptor to include auth token (fallback to localStorage for backward compatibility)
    this.api.interceptors.request.use((config) => {
      const tokens = this.getStoredTokens();
      if (tokens?.access_token) {
        config.headers.Authorization = `Bearer ${tokens.access_token}`;
      }
      return config;
    });

    // Add response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return this.api(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          const tokens = this.getStoredTokens();
          if (!tokens?.refresh_token) {
            this.clearTokens();
            // Emit logout event for auth state management
            window.dispatchEvent(new CustomEvent('auth:logout'));
            return Promise.reject(error);
          }

          try {
            const newTokens = await this.refreshToken(tokens.refresh_token);
            this.storeTokens(newTokens);

            // Process all queued requests with new token
            this.failedQueue.forEach(({ resolve }) => {
              resolve(newTokens.access_token);
            });
            this.failedQueue = [];

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and logout
            this.clearTokens();
            this.failedQueue.forEach(({ reject }) => {
              reject(refreshError instanceof Error ? refreshError : new Error(String(refreshError)));
            });
            this.failedQueue = [];
            window.dispatchEvent(new CustomEvent('auth:logout'));
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post(
      '/api/auth/login/email',
      credentials
    );
    return response.data;
  }

  async register(data: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post(
      '/api/auth/register/email',
      data
    );
    return response.data;
  }

  async requestMagicLink(email: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.api.post(
      '/api/auth/magic-link/request',
      { email }
    );
    return response.data;
  }

  async verifyMagicLink(token: string): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post(
      '/api/auth/magic-link/verify',
      { token }
    );
    return response.data;
  }

  async googleAuth(credential: string): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post(
      '/api/auth/google',
      { credential }
    );
    return response.data;
  }

  async appleAuth(authData: { authorization: { code: string; id_token: string }; user?: { name?: { firstName?: string; lastName?: string }; email?: string } }): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post(
      '/api/auth/apple',
      authData
    );
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post(
      '/api/auth/refresh',
      { refresh_token: refreshToken }
    );
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/api/users/me');
    return response.data;
  }

  // Token management
  storeTokens(tokens: AuthTokens): void {
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  }

  getStoredTokens(): AuthTokens | null {
    const stored = localStorage.getItem('auth_tokens');
    return stored ? JSON.parse(stored) : null;
  }

  clearTokens(): void {
    localStorage.removeItem('auth_tokens');
  }

  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint to clear httpOnly cookies
      await this.api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout API call failed:', error);
    }

    // Clear any localStorage tokens (fallback)
    this.clearTokens();

    // Emit logout event for components to listen
    window.dispatchEvent(new CustomEvent('auth:logout'));

    // Redirect to login page
    window.location.href = '/';
  }

  isAuthenticated(): boolean {
    // With httpOnly cookies, we can't check token directly
    // This method now primarily serves as a fallback for localStorage tokens
    const tokens = this.getStoredTokens();
    return !!tokens?.access_token;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; service: string }> {
    const response = await this.api.get('/api/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;