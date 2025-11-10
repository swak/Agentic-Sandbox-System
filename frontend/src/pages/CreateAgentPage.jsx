import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AgentForm from '../components/AgentForm';
import { agentAPI } from '../services/api';

const CreateAgentPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (formData) => {
    setIsLoading(true);

    try {
      const response = await agentAPI.create({
        name: formData.name,
        type: formData.type,
        api_provider: formData.api_provider,
        model: formData.model,
        system_prompt: formData.system_prompt,
        api_key: formData.api_key || undefined,
      });

      alert(`Agent "${response.name}" created successfully!`);
      navigate(`/agents/${response.id}`);
    } catch (error) {
      alert(`Error creating agent: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Create New Agent
      </h1>

      <AgentForm onSubmit={handleSubmit} isLoading={isLoading} />
    </div>
  );
};

export default CreateAgentPage;
