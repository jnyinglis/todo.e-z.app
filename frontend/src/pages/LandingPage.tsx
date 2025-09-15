import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { type LoginCredentials, type RegisterData } from '../types/auth';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, register, googleLogin, requestMagicLink, isLoading, isAuthenticated } = useAuth();

  const [mode, setMode] = useState<'login' | 'register' | 'magic-link'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      if (mode === 'login') {
        const credentials: LoginCredentials = { email, password };
        await login(credentials);
        navigate('/dashboard');
      } else if (mode === 'register') {
        const data: RegisterData = { email, password, full_name: fullName };
        await register(data);
        setMessage('Registration successful! Please check your email for verification.');
        setMode('login');
      } else if (mode === 'magic-link') {
        await requestMagicLink(email);
        setMessage('Magic link sent to your email!');
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'An error occurred');
    }
  };

  const handleGoogleLogin = useCallback((credential: string) => {
    googleLogin(credential)
      .then(() => navigate('/dashboard'))
      .catch((err) => setError(err.response?.data?.detail || 'Google login failed'));
  }, [googleLogin, navigate, setError]);

  // Load Google Sign-In script
  React.useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: (response: { credential: string }) => handleGoogleLogin(response.credential),
        });
      }
    };

    return () => {
      document.head.removeChild(script);
    };
  }, [handleGoogleLogin]);

  if (isLoading) {
    return <div className="loading-container">Loading...</div>;
  }

  return (
    <div className="landing-page">
      <div className="auth-container">
        <h1>Welcome to Vite React FastAPI Template</h1>

        {error && <div className="error-message">{error}</div>}
        {message && <div className="success-message">{message}</div>}

        <div className="auth-modes">
          <button
            onClick={() => setMode('login')}
            className={mode === 'login' ? 'active' : ''}
          >
            Login
          </button>
          <button
            onClick={() => setMode('register')}
            className={mode === 'register' ? 'active' : ''}
          >
            Register
          </button>
          <button
            onClick={() => setMode('magic-link')}
            className={mode === 'magic-link' ? 'active' : ''}
          >
            Magic Link
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input
                type="text"
                id="fullName"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          {mode !== 'magic-link' && (
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
          )}

          <button type="submit" disabled={isLoading} className="submit-btn">
            {isLoading ? 'Loading...' :
             mode === 'login' ? 'Login' :
             mode === 'register' ? 'Register' : 'Send Magic Link'}
          </button>
        </form>

        <div className="oauth-section">
          <div className="divider">
            <span>or</span>
          </div>

          <div id="google-signin-button" className="google-btn">
            <div
              id="g_id_onload"
              data-client_id={import.meta.env.VITE_GOOGLE_CLIENT_ID}
              data-callback="handleGoogleLogin"
            ></div>
            <div
              className="g_id_signin"
              data-type="standard"
              data-size="large"
              data-theme="outline"
              data-text="sign_in_with"
              data-shape="rectangular"
              data-logo_alignment="left"
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;