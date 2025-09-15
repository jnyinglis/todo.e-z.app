import React from 'react';
import { useAuth } from '../hooks/useAuth';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.full_name || user?.email}!</span>
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="user-card">
          <h2>User Information</h2>
          <div className="user-details">
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Full Name:</strong> {user?.full_name || 'Not provided'}</p>
            <p><strong>Verified:</strong> {user?.is_verified ? 'Yes' : 'No'}</p>
            <p><strong>Member since:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}</p>
          </div>
          {user?.avatar_url && (
            <img
              src={user.avatar_url}
              alt="User avatar"
              className="user-avatar"
            />
          )}
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>Profile</h3>
            <p>Manage your profile information and settings.</p>
            <button className="card-btn">Edit Profile</button>
          </div>

          <div className="dashboard-card">
            <h3>Security</h3>
            <p>Update your password and security settings.</p>
            <button className="card-btn">Security Settings</button>
          </div>

          <div className="dashboard-card">
            <h3>Preferences</h3>
            <p>Customize your app experience.</p>
            <button className="card-btn">Preferences</button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;