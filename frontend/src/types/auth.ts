export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthState {
  user: User | null;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  } | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}