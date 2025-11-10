import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ChatInterface from '../components/ChatInterface';
import { agentAPI } from '../services/api';

const AgentPage = () => {
  const { agentId } = useParams();
  const [agent, setAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const data = await agentAPI.get(agentId);
        setAgent(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAgent();
  }, [agentId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-12">
          <p className="text-gray-600">Loading agent...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
          <Link to="/" className="text-blue-600 hover:underline mt-2 inline-block">
            ← Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Agent Header */}
      <div className="mb-6">
        <Link to="/" className="text-blue-600 hover:underline mb-2 inline-block">
          ← Back to Agents
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          {agent.name}
        </h1>
        <p className="text-gray-600 mt-1">
          {agent.api_provider} • {agent.model} • {agent.status}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <ChatInterface agentId={agentId} />
        </div>

        {/* Agent Info Sidebar */}
        <div className="space-y-6">
          {/* Agent Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4">Agent Details</h2>
            <dl className="space-y-2 text-sm">
              <div>
                <dt className="text-gray-600">Type</dt>
                <dd className="font-medium">{agent.type}</dd>
              </div>
              <div>
                <dt className="text-gray-600">API Provider</dt>
                <dd className="font-medium">{agent.api_provider}</dd>
              </div>
              <div>
                <dt className="text-gray-600">Model</dt>
                <dd className="font-medium">{agent.model}</dd>
              </div>
              <div>
                <dt className="text-gray-600">Status</dt>
                <dd>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      agent.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {agent.status}
                  </span>
                </dd>
              </div>
            </dl>
          </div>

          {/* System Prompt */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4">System Prompt</h2>
            <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
              {agent.system_prompt}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentPage;
