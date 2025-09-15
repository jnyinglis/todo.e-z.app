import React from 'react';
import { usePWA } from '../utils/pwa';

interface PWAInstallPromptProps {
  className?: string;
  style?: React.CSSProperties;
}

export function PWAInstallPrompt({ className, style }: PWAInstallPromptProps) {
  const { isInstallable, isInstalled, updateAvailable, isOnline, installApp, updateApp } = usePWA();

  // Don't show anything if already installed
  if (isInstalled) {
    return null;
  }

  return (
    <div className={className} style={style}>
      {/* Install prompt */}
      {isInstallable && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#e3f2fd',
          border: '1px solid #2196f3',
          borderRadius: '8px',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1976d2' }}>
              📱 Install App
            </h4>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>
              Install this app on your device for a better experience
            </p>
          </div>
          <button
            onClick={installApp}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              whiteSpace: 'nowrap'
            }}
          >
            Install
          </button>
        </div>
      )}

      {/* Update available prompt */}
      {updateAvailable && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fff3e0',
          border: '1px solid #ff9800',
          borderRadius: '8px',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#f57c00' }}>
              🔄 Update Available
            </h4>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>
              A new version is available. Update now for the latest features.
            </p>
          </div>
          <button
            onClick={updateApp}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#ff9800',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              whiteSpace: 'nowrap'
            }}
          >
            Update
          </button>
        </div>
      )}

      {/* Offline indicator */}
      {!isOnline && (
        <div style={{
          padding: '0.75rem',
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '8px',
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          <span style={{ color: '#d32f2f', fontSize: '0.9rem' }}>
            📶 You're offline - Some features may be limited
          </span>
        </div>
      )}
    </div>
  );
}

export default PWAInstallPrompt;