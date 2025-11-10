import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { agentAPI } from '../services/api';

const HomePage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const data = await agentAPI.list();
      setAgents(data.agents || []);
    } catch (err) {
      setError(err.message);
      console.error('Error loading agents:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Agentic Sandbox System
        </h1>
        <p className="text-lg text-gray-600">
          Create, configure, and test AI agents with ease
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8 mb-8">
        <h2 className="text-2xl font-semibold mb-4">Get Started</h2>
        <p className="text-gray-600 mb-6">
          Create your first AI agent to start chatting with intelligent assistants
          powered by OpenAI or Anthropic.
        </p>
        <Link
          to="/create"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Create New Agent
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-semibold mb-6">Your Agents</h2>

        {loading ? (
          <p className="text-gray-500">Loading agents...</p>
        ) : error ? (
          <div className="text-red-600">
            <p>Error loading agents: {error}</p>
            <button
              onClick={loadAgents}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : agents.length === 0 ? (
          <p className="text-gray-500">
            No agents created yet. Click "Create New Agent" to get started.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <Link
                key={agent.id}
                to={`/agents/${agent.id}`}
                className="block p-6 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition"
              >
                <div className="mb-3">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {agent.name}
                  </h3>
                  <span
                    className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                      agent.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <div>
                    <span className="font-semibold">Type:</span> {agent.type}
                  </div>
                  <div>
                    <span className="font-semibold">Model:</span> {agent.model}
                  </div>
                  <div>
                    <span className="font-semibold">Provider:</span>{' '}
                    {agent.api_provider}
                  </div>
                </div>

                {agent.system_prompt && (
                  <p className="mt-4 text-sm text-gray-500 line-clamp-2">
                    {agent.system_prompt}
                  </p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
