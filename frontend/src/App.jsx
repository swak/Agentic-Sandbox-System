/**
 * Main App component
 * Handles routing and global state management
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AgentProvider } from './context/AgentContext';
import { NotificationProvider } from './context/NotificationContext';

// Pages
import HomePage from './pages/HomePage';
import CreateAgentPage from './pages/CreateAgentPage';
import AgentPage from './pages/AgentPage';
import AuditLogsPage from './pages/AuditLogsPage';

// Components
import Navbar from './components/Navbar';
import NotificationContainer from './components/NotificationContainer';

function App() {
  return (
    <Router>
      <NotificationProvider>
        <AgentProvider>
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <NotificationContainer />

            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/create" element={<CreateAgentPage />} />
                <Route path="/agents/:agentId" element={<AgentPage />} />
                <Route path="/audit-logs" element={<AuditLogsPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </AgentProvider>
      </NotificationProvider>
    </Router>
  );
}

export default App;
