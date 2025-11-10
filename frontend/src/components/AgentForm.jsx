/**
 * AgentForm Component
 * Form for creating and editing agents
 */

import React, { useState } from 'react';

const PROMPT_TEMPLATES = {
  friendly_support: {
    name: 'Friendly Customer Support',
    prompt: 'You are a friendly and helpful customer support agent for an online store. Help customers with orders, returns, and product questions. Be concise and professional.',
  },
  technical_support: {
    name: 'Technical Support',
    prompt: 'You are a technical support specialist. Help users troubleshoot issues, provide step-by-step instructions, and explain technical concepts clearly.',
  },
  sales_assistant: {
    name: 'Sales Assistant',
    prompt: 'You are a knowledgeable sales assistant. Help customers find products that meet their needs, answer questions about features, and provide recommendations.',
  },
  custom: {
    name: 'Custom Prompt',
    prompt: '',
  },
};

const AgentForm = ({ initialData = {}, onSubmit, isLoading = false }) => {
  const [formData, setFormData] = useState({
    name: initialData.name || '',
    type: initialData.type || 'chat',
    api_provider: initialData.api_provider || 'openai',
    model: initialData.model || 'gpt-4',
    system_prompt: initialData.system_prompt || '',
    api_key: '',
  });

  const [selectedTemplate, setSelectedTemplate] = useState('custom');
  const [knowledgeBaseFile, setKnowledgeBaseFile] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleTemplateChange = (e) => {
    const template = e.target.value;
    setSelectedTemplate(template);

    if (template !== 'custom') {
      setFormData((prev) => ({
        ...prev,
        system_prompt: PROMPT_TEMPLATES[template].prompt,
      }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (1MB max)
      if (file.size > 1024 * 1024) {
        alert('File size must be less than 1MB');
        return;
      }
      setKnowledgeBaseFile(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      alert('Please enter an agent name');
      return;
    }

    if (!formData.system_prompt.trim()) {
      alert('Please enter a system prompt or select a template');
      return;
    }

    onSubmit({
      ...formData,
      knowledgeBaseFile,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
      {/* Agent Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Agent Name *
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="e.g., Customer Support Bot"
          required
        />
      </div>

      {/* API Provider */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          API Provider *
        </label>
        <select
          name="api_provider"
          value={formData.api_provider}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic (Claude)</option>
        </select>
      </div>

      {/* Model */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Model *
        </label>
        <select
          name="model"
          value={formData.model}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {formData.api_provider === 'openai' ? (
            <>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </>
          ) : (
            <>
              <option value="claude-3-opus">Claude 3 Opus</option>
              <option value="claude-3-sonnet">Claude 3 Sonnet</option>
              <option value="claude-3-haiku">Claude 3 Haiku</option>
            </>
          )}
        </select>
      </div>

      {/* Prompt Template */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prompt Template
        </label>
        <select
          value={selectedTemplate}
          onChange={handleTemplateChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {Object.entries(PROMPT_TEMPLATES).map(([key, template]) => (
            <option key={key} value={key}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      {/* System Prompt */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          System Prompt *
        </label>
        <textarea
          name="system_prompt"
          value={formData.system_prompt}
          onChange={handleChange}
          rows={6}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          placeholder="Enter custom instructions for your agent..."
          required
        />
        <p className="mt-1 text-sm text-gray-500">
          This defines how your agent behaves and responds to users.
        </p>
      </div>

      {/* API Key (Optional) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          API Key (Optional)
        </label>
        <input
          type="password"
          name="api_key"
          value={formData.api_key}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Leave blank to use environment variable"
        />
        <p className="mt-1 text-sm text-gray-500">
          Optional: Provide a specific API key for this agent.
        </p>
      </div>

      {/* Knowledge Base Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Knowledge Base (Optional)
        </label>
        <input
          type="file"
          accept=".txt,.json,.pdf,.docx"
          onChange={handleFileChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="mt-1 text-sm text-gray-500">
          Upload a file (TXT, JSON, PDF, DOCX) for RAG. Max size: 1MB.
        </p>
        {knowledgeBaseFile && (
          <p className="mt-2 text-sm text-green-600">
            Selected: {knowledgeBaseFile.name} ({(knowledgeBaseFile.size / 1024).toFixed(2)} KB)
          </p>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Agent'}
        </button>
      </div>
    </form>
  );
};

export default AgentForm;
