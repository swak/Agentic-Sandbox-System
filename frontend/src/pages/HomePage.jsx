import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
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
        <h2 className="text-2xl font-semibold mb-4">Your Agents</h2>
        <p className="text-gray-500">
          No agents created yet. Click "Create New Agent" to get started.
        </p>
      </div>
    </div>
  );
};

export default HomePage;
