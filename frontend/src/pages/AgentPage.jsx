import React from 'react';
import { useParams } from 'react-router-dom';

const AgentPage = () => {
  const { agentId } = useParams();

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Agent Chat
      </h1>

      <div className="bg-white rounded-lg shadow-md p-8">
        <p className="text-gray-600">
          Chat interface for agent {agentId}
        </p>
        <p className="text-sm text-gray-500 mt-4">
          This is a placeholder. Full chat interface will be implemented here.
        </p>
      </div>
    </div>
  );
};

export default AgentPage;
