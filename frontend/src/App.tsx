import { BrowserRouter as Router, Routes, Route, useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import apiService from './services/api';
import { SEOHead } from './components/SEOHead';
import { createWebsiteSchema } from './utils/seoSchemas';
import PWAInstallPrompt from './components/PWAInstallPrompt';
import {
  authConfig,
  isEmailPasswordEnabled,
  isGoogleEnabled,
  isAppleEnabled,
  isMagicLinkEnabled,
  getEnabledProvidersCount
} from './config/auth';
import './App.css';

interface GoogleSignInConfig {
  client_id: string;
  callback: (response: GoogleSignInResponse) => void;
}

interface GoogleSignInResponse {
  credential: string;
}

interface GoogleRenderButtonOptions {
  theme?: string;
  size?: string;
  width?: string;
}

interface AppleIDConfig {
  clientId: string;
  scope: string;
  redirectURI: string;
  state: string;
  usePopup: boolean;
}

interface AppleSignInResponse {
  authorization: {
    code: string;
    id_token: string;
  };
  user?: {
    name?: {
      firstName?: string;
      lastName?: string;
    };
    email?: string;
  };
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: GoogleSignInConfig) => void;
          renderButton: (element: Element | null, options: GoogleRenderButtonOptions) => void;
        };
      };
    };
    AppleID?: {
      auth: {
        init: (config: AppleIDConfig) => void;
        signIn: () => Promise<AppleSignInResponse>;
        renderButton: (element: Element | null, options: GoogleRenderButtonOptions) => void;
      };
    };
  }
}

function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);

  // SEO data
  const websiteSchema = createWebsiteSchema(
    'Vite React FastAPI Template',
    window.location.origin,
    'A modern full-stack template with React, FastAPI, and PostgreSQL featuring secure authentication and responsive design.'
  );
  const [showMagicLink, setShowMagicLink] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [magicToken, setMagicToken] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ email: string; full_name?: string; is_verified: boolean } | null>(null);

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuthStatus = async () => {
      if (apiService.isAuthenticated()) {
        try {
          const user = await apiService.getCurrentUser();
          setIsAuthenticated(true);
          setCurrentUser(user);
        } catch (error) {
          console.error('Failed to get current user:', error);
          apiService.logout();
        }
      }
    };

    checkAuthStatus();

    // Initialize Google Sign-In when the component mounts
    if (isGoogleEnabled() && window.google && authConfig.providers.google.clientId) {
      window.google.accounts.id.initialize({
        client_id: authConfig.providers.google.clientId,
        callback: handleGoogleSignIn,
      });
      window.google.accounts.id.renderButton(
        document.getElementById("google-signin-button"),
        { theme: "outline", size: "large", width: "100%" }
      );
    }

    // Initialize Apple Sign-In when the component mounts
    if (isAppleEnabled() && window.AppleID && authConfig.providers.apple.clientId && authConfig.providers.apple.redirectUri) {
      window.AppleID.auth.init({
        clientId: authConfig.providers.apple.clientId,
        scope: 'name email',
        redirectURI: authConfig.providers.apple.redirectUri,
        state: 'auth-state',
        usePopup: true
      });
    }

    // Listen for logout events
    const handleLogoutEvent = () => {
      setIsAuthenticated(false);
      setCurrentUser(null);
    };

    window.addEventListener('auth:logout', handleLogoutEvent);

    return () => {
      window.removeEventListener('auth:logout', handleLogoutEvent);
    };
  }, []);

  const handleGoogleSignIn = async (response: GoogleSignInResponse) => {
    try {
      const data = await apiService.googleAuth(response.credential);
      // Store tokens and update auth state
      apiService.storeTokens(data);
      const user = await apiService.getCurrentUser();
      setIsAuthenticated(true);
      setCurrentUser(user);
      alert('Google Sign-In successful!');
    } catch (error) {
      console.error('Google Sign-In Error:', error);
      alert('Google Sign-In failed!');
    }
  };

  const handleAppleSignIn = async () => {
    if (!window.AppleID) {
      alert('Apple Sign-In not available');
      return;
    }

    try {
      const response = await window.AppleID.auth.signIn();
      console.log('Apple Sign-In Response:', response);

      const data = await apiService.appleAuth({
        authorization: response.authorization,
        user: response.user
      });

      // Store tokens and update auth state
      apiService.storeTokens(data);
      const user = await apiService.getCurrentUser();
      setIsAuthenticated(true);
      setCurrentUser(user);
      alert('Apple Sign-In successful!');
    } catch (error) {
      console.error('Apple Sign-In Error:', error);
      alert('Apple Sign-In failed!');
    }
  };

  const handleMagicLinkRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    try {
      const data = await apiService.requestMagicLink(email);
      console.log('Magic Link Request Success:', data);
      alert('Magic link sent! Check the backend console for the token.');
    } catch (error) {
      console.error('Magic Link Request Error:', error);
      alert('Failed to send magic link!');
    }
  };

  const handleMagicLinkVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!magicToken) {
      alert('Please enter the magic token');
      return;
    }

    try {
      const data = await apiService.verifyMagicLink(magicToken);
      console.log('Magic Link Verify Success:', data);

      // Store tokens and update auth state
      apiService.storeTokens(data);
      const user = await apiService.getCurrentUser();
      setIsAuthenticated(true);
      setCurrentUser(user);
      setMagicToken('');
      setShowMagicLink(false);
      alert('Magic link login successful!');
    } catch (error) {
      console.error('Magic Link Verify Error:', error);
      alert('Invalid magic token!');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (isLogin) {
        const data = await apiService.login({ email, password });
        // Store tokens and update auth state
        apiService.storeTokens(data);
        const user = await apiService.getCurrentUser();
        setIsAuthenticated(true);
        setCurrentUser(user);
        alert('Logged in successfully!');
      } else {
        const userData = await apiService.register({
          email,
          password,
          full_name: fullName || undefined
        });
        console.log('Registration Success:', userData);
        alert('Registered successfully! Please sign in with your credentials.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Something went wrong!');
    }
  };

  const handleLogout = async () => {
    await apiService.logout();
  };

  if (isAuthenticated && currentUser) {
    return (
      <>
        <SEOHead
          title="Dashboard"
          description="User dashboard for authenticated users"
          jsonLD={websiteSchema}
        />
        <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
        <h1>Welcome, {currentUser.full_name || currentUser.email}!</h1>
        <p>You are successfully authenticated.</p>

        <div style={{
          padding: '1rem',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px',
          marginBottom: '2rem'
        }}>
          <p><strong>User Information:</strong></p>
          <p>Email: {currentUser.email}</p>
          <p>Full Name: {currentUser.full_name || 'Not provided'}</p>
          <p>Verified: {currentUser.is_verified ? '✅ Yes' : '❌ No'}</p>
        </div>

        <button
          onClick={handleLogout}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem',
            width: '100%'
          }}
        >
          Logout
        </button>
        </div>
      </>
    );
  }

  return (
    <>
      <SEOHead
        title={isLogin ? "Sign In" : "Sign Up"}
        description={isLogin
          ? "Sign in to your account to access the full-stack template dashboard"
          : "Create your account to get started with our full-stack template"
        }
        canonical={`${window.location.origin}${window.location.pathname}`}
        jsonLD={websiteSchema}
      />
      <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
        <PWAInstallPrompt />
        <h1>Full-Stack Template</h1>
      <p>Vite + React + FastAPI + PostgreSQL</p>

      {(isEmailPasswordEnabled() || isMagicLinkEnabled()) && (
        <div style={{ marginBottom: '1rem' }}>
          {isEmailPasswordEnabled() && (
            <>
              <button
                onClick={() => { setIsLogin(true); setShowMagicLink(false); }}
                style={{
                  marginRight: '0.5rem',
                  padding: '0.5rem 1rem',
                  backgroundColor: (isLogin && !showMagicLink) ? '#007bff' : '#f8f9fa',
                  color: (isLogin && !showMagicLink) ? 'white' : 'black',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Sign In
              </button>
              {authConfig.providers.emailPassword.allowRegistration && (
                <button
                  onClick={() => { setIsLogin(false); setShowMagicLink(false); }}
                  style={{
                    marginRight: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: (!isLogin && !showMagicLink) ? '#007bff' : '#f8f9fa',
                    color: (!isLogin && !showMagicLink) ? 'white' : 'black',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Register
                </button>
              )}
            </>
          )}
          {isMagicLinkEnabled() && (
            <button
              onClick={() => setShowMagicLink(true)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: showMagicLink ? '#007bff' : '#f8f9fa',
                color: showMagicLink ? 'white' : 'black',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Magic Link
            </button>
          )}
        </div>
      )}

      {showMagicLink && isMagicLinkEnabled() ? (
        <div>
          <form onSubmit={handleMagicLinkRequest} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
            <div>
              <label>Email:</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email to receive magic link"
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
              />
            </div>
            <button
              type="submit"
              style={{
                padding: '0.75rem',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
            >
              Send Magic Link
            </button>
          </form>

          <form onSubmit={handleMagicLinkVerify} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label>Magic Token (from backend console):</label>
              <input
                type="text"
                value={magicToken}
                onChange={(e) => setMagicToken(e.target.value)}
                required
                placeholder="Paste the token from backend logs"
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
              />
            </div>
            <button
              type="submit"
              style={{
                padding: '0.75rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
            >
              Verify Magic Link
            </button>
          </form>
        </div>
      ) : isEmailPasswordEnabled() ? (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {!isLogin && authConfig.providers.emailPassword.allowRegistration && (
            <div>
              <label>Full Name:</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
              />
            </div>
          )}
          <div>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>
          <button
            type="submit"
            style={{
              padding: '0.75rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            {isLogin ? 'Sign In' : 'Register'}
          </button>
        </form>
      ) : (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px',
          color: '#666'
        }}>
          <p>No authentication methods are currently enabled.</p>
          <p>Please check your environment configuration.</p>
        </div>
      )}

      {getEnabledProvidersCount() > 1 && (
        <div style={{ margin: '1rem 0', textAlign: 'center', color: '#666' }}>
          <hr style={{ margin: '1rem 0' }} />
          <span>OR</span>
          <hr style={{ margin: '1rem 0' }} />
        </div>
      )}

      {isGoogleEnabled() && (
        <>
          <div id="google-signin-button" style={{ marginBottom: '1rem' }}></div>
          {!authConfig.providers.google.clientId && (
            <p style={{ fontSize: '0.8rem', color: '#dc3545', textAlign: 'center' }}>
              Note: Google Sign-In requires client ID configuration
            </p>
          )}
        </>
      )}

      {isAppleEnabled() && (
        <>
          <button
            onClick={handleAppleSignIn}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#000000',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 256 315"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M213.803 167.03c.442 47.58 41.74 63.413 42.197 63.615c-.35 1.116-6.599 22.563-21.757 44.716c-13.104 19.153-26.705 38.235-48.13 38.63c-21.05.388-27.82-12.483-51.888-12.483c-24.061 0-31.582 12.088-51.51 12.871c-20.68.783-36.428-20.71-49.64-39.793c-27-39.033-47.633-110.3-19.928-158.406c13.763-23.89 38.36-39.017 65.056-39.405c20.307-.387 39.475 13.662 51.889 13.662c12.406 0 35.699-16.895 60.186-14.414c10.25.427 39.026 4.14 57.503 31.186c-1.49.923-34.335 20.044-33.978 59.822M174.24 50.199c10.98-13.29 18.369-31.79 16.353-50.199c-15.826.636-34.962 10.546-46.314 23.828c-10.173 11.763-19.082 30.589-16.678 48.633c17.64 1.365 35.66-8.964 46.64-22.262"/>
            </svg>
            Sign in with Apple
          </button>
          {!authConfig.providers.apple.clientId && (
            <p style={{ fontSize: '0.8rem', color: '#dc3545', textAlign: 'center', marginTop: '-0.5rem', marginBottom: '1rem' }}>
              Note: Apple Sign-In requires client ID configuration
            </p>
          )}
        </>
      )}

      {getEnabledProvidersCount() > 0 && (
        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <p><strong>Available Authentication Methods:</strong></p>
          {isEmailPasswordEnabled() && <p>• Email/Password authentication</p>}
          {isMagicLinkEnabled() && <p>• Magic Link passwordless authentication</p>}
          {isGoogleEnabled() && <p>• Google OAuth Sign-In</p>}
          {isAppleEnabled() && <p>• Apple Sign-In</p>}
          <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
            Check browser console for API responses
          </p>
        </div>
      )}
      </div>
    </>
  );
}

function MagicLinkVerify() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error' | 'expired'>('verifying');
  const [message, setMessage] = useState('');

  // SEO data
  const websiteSchema = createWebsiteSchema(
    'Vite React FastAPI Template',
    window.location.origin,
    'A modern full-stack template with React, FastAPI, and PostgreSQL featuring secure authentication and responsive design.'
  );

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      setMessage('No token provided in URL');
      return;
    }

    const verifyToken = async () => {
      try {
        const data = await apiService.verifyMagicLink(token);
        console.log('Magic Link Auto-Verify Success:', data);
        setStatus('success');
        setMessage('Successfully authenticated via magic link!');
        // Store tokens
        apiService.storeTokens(data);
      } catch (error) {
        console.error('Magic Link Verify Error:', error);
        setStatus('error');
        setMessage('Network error during verification');
      }
    };

    verifyToken();
  }, [searchParams]);

  const getStatusColor = () => {
    switch (status) {
      case 'success': return '#28a745';
      case 'error': return '#dc3545';
      case 'expired': return '#fd7e14';
      default: return '#007bff';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'verifying': return '⏳';
      case 'success': return '✅';
      case 'error': return '❌';
      case 'expired': return '⏰';
    }
  };

  return (
    <>
      <SEOHead
        title="Magic Link Verification"
        description="Verify your magic link to complete authentication"
        canonical={`${window.location.origin}${window.location.pathname}`}
        jsonLD={websiteSchema}
        robots="noindex, nofollow"
      />
      <div style={{ maxWidth: '400px', margin: '2rem auto', padding: '2rem', textAlign: 'center' }}>
      <h1>Magic Link Verification</h1>

      <div style={{
        padding: '2rem',
        borderRadius: '8px',
        backgroundColor: '#f8f9fa',
        border: `2px solid ${getStatusColor()}`,
        marginBottom: '2rem'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          {getStatusIcon()}
        </div>
        <h2 style={{ color: getStatusColor(), marginBottom: '1rem' }}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </h2>
        <p>{message || 'Verifying your magic link...'}</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <p><strong>Token:</strong> {searchParams.get('token')?.substring(0, 20)}...</p>
      </div>

      <button
        onClick={() => window.location.href = '/'}
        style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '1rem'
        }}
      >
        {status === 'success' ? 'Continue to App' : 'Back to Login'}
      </button>
      </div>
    </>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LoginForm />} />
          <Route path="/auth/verify" element={<MagicLinkVerify />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
