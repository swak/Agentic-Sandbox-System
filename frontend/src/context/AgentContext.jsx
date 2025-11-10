import React, { createContext, useState, useContext } from 'react';

const AgentContext = createContext();

export const useAgents = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgents must be used within AgentProvider');
  }
  return context;
};

export const AgentProvider = ({ children }) => {
  const [agents, setAgents] = useState([]);
  const [currentAgent, setCurrentAgent] = useState(null);

  const value = {
    agents,
    setAgents,
    currentAgent,
    setCurrentAgent,
  };

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
};
