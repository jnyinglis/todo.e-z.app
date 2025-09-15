import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { verifyMagicLink } = useAuth();
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    const token = searchParams.get('token');

    if (token) {
      verifyMagicLink(token)
        .then(() => {
          navigate('/dashboard');
        })
        .catch((err) => {
          setError(err.response?.data?.detail || 'Verification failed');
          setIsVerifying(false);
        });
    } else {
      setError('No verification token provided');
      setIsVerifying(false);
    }
  }, [searchParams, verifyMagicLink, navigate]);

  if (isVerifying) {
    return (
      <div className="auth-callback">
        <div className="loading-container">
          <div className="loading-spinner">Verifying...</div>
          <p>Please wait while we verify your authentication.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-callback">
      <div className="error-container">
        <h2>Authentication Failed</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')} className="back-btn">
          Back to Login
        </button>
      </div>
    </div>
  );
};

export default AuthCallback;