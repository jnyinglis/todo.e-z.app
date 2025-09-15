import React, { useEffect, useState, type ReactNode } from 'react';
import { type AuthState, type LoginCredentials, type RegisterData, type User } from '../types/auth';
import { AuthContext, type AuthContextType } from './AuthContextDef';

type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};
import { apiService } from '../services/api';


interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    tokens: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Initialize auth state from stored tokens
  useEffect(() => {
    const initializeAuth = async () => {
      const storedTokens = apiService.getStoredTokens();

      if (storedTokens) {
        try {
          const user = await apiService.getCurrentUser();
          setState({
            user,
            tokens: storedTokens,
            isLoading: false,
            isAuthenticated: true,
          });
        } catch {
          // Token is invalid, clear it
          apiService.clearTokens();
          setState({
            user: null,
            tokens: null,
            isLoading: false,
            isAuthenticated: false,
          });
        }
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
        }));
      }
    };

    initializeAuth();
  }, []);

  const updateAuthState = (tokens: AuthTokens, user: User) => {
    apiService.storeTokens(tokens);
    setState({
      user,
      tokens,
      isLoading: false,
      isAuthenticated: true,
    });
  };

  const login = async (credentials: LoginCredentials): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const tokens = await apiService.login(credentials);
      const user = await apiService.getCurrentUser();
      updateAuthState(tokens, user);
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const register = async (data: RegisterData): Promise<User> => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const user = await apiService.register(data);
      setState(prev => ({ ...prev, isLoading: false }));
      return user;
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const googleLogin = async (credential: string): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const tokens = await apiService.googleAuth(credential);
      const user = await apiService.getCurrentUser();
      updateAuthState(tokens, user);
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const requestMagicLink = async (email: string): Promise<void> => {
    await apiService.requestMagicLink(email);
  };

  const verifyMagicLink = async (token: string): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const tokens = await apiService.verifyMagicLink(token);
      const user = await apiService.getCurrentUser();
      updateAuthState(tokens, user);
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const logout = (): void => {
    apiService.clearTokens();
    setState({
      user: null,
      tokens: null,
      isLoading: false,
      isAuthenticated: false,
    });
  };

  const refreshUser = async (): Promise<void> => {
    if (state.isAuthenticated && state.tokens) {
      try {
        const user = await apiService.getCurrentUser();
        setState(prev => ({ ...prev, user }));
      } catch (error) {
        console.error('Failed to refresh user:', error);
      }
    }
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    googleLogin,
    requestMagicLink,
    verifyMagicLink,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

