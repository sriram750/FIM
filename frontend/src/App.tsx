import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginPage } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { EndpointsPage } from './pages/Endpoints';
import { PoliciesPage } from './pages/Policies';
import { FileExplorerPage } from './pages/FileExplorer';
import { EventExplorerPage } from './pages/EventExplorer';
import { AlertsPage } from './pages/Alerts';
import { ReportsPage } from './pages/Reports';
import { AdministrationPage } from './pages/Administration';
import { NavigationTab, SystemHealthData } from './types';
import { fetchHealth } from './api/client';
import { getStoredAuth, clearAuth, AuthUser } from './api/auth';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentTab, setCurrentTab] = useState<NavigationTab>('overview');
  const [health, setHealth] = useState<SystemHealthData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize Auth state from localStorage
  useEffect(() => {
    const auth = getStoredAuth();
    if (auth.isAuthenticated && auth.user) {
      setCurrentUser(auth.user);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = (user: AuthUser) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    clearAuth();
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const loadHealth = async () => {
    setIsLoading(true);
    const data = await fetchHealth();
    setHealth(data);
    setIsLoading(false);
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadHealth();
      const interval = setInterval(loadHealth, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  // If not logged in, show Login Screen
  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <Dashboard health={health} onRefresh={loadHealth} isLoading={isLoading} />;
      case 'endpoints':
        return <EndpointsPage />;
      case 'policies':
        return <PoliciesPage />;
      case 'file-explorer':
        return <FileExplorerPage />;
      case 'event-explorer':
        return <EventExplorerPage />;
      case 'alerts':
        return <AlertsPage />;
      case 'reports':
        return <ReportsPage />;
      case 'admin':
        return <AdministrationPage />;
      default:
        return <Dashboard health={health} onRefresh={loadHealth} isLoading={isLoading} />;
    }
  };

  return (
    <div className="flex h-screen bg-[#0B0F17] text-gray-100 overflow-hidden">
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header 
          health={health} 
          user={currentUser} 
          onLogout={handleLogout} 
        />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};
