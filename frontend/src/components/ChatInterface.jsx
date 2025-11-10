import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';

const ChatInterface = ({ agentId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString(),
      },
    ]);

    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(agentId, userMessage);

      // Add agent response to chat
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: response.response,
          timestamp: new Date().toISOString(),
          tokens_used: response.tokens_used,
          response_time_ms: response.response_time_ms,
          rag_context: response.rag_context,
        },
      ]);
    } catch (error) {
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          role: 'error',
          content: `Error: ${error.message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-md">
      {/* Chat Header */}
      <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
        <h2 className="text-xl font-semibold">Chat</h2>
        <p className="text-sm text-blue-100">Agent ID: {agentId.slice(0, 8)}...</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No messages yet. Start chatting!</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {/* Metadata */}
                <div className="mt-2 text-xs opacity-75">
                  {message.tokens_used && (
                    <span className="mr-3">
                      Tokens: {message.tokens_used}
                    </span>
                  )}
                  {message.response_time_ms && (
                    <span>
                      Time: {message.response_time_ms}ms
                    </span>
                  )}
                </div>

                {/* RAG Context (if available) */}
                {message.rag_context && message.rag_context.length > 0 && (
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer font-semibold">
                      RAG Context ({message.rag_context.length} documents)
                    </summary>
                    <div className="mt-2 space-y-1 pl-2">
                      {message.rag_context.map((doc, i) => (
                        <div
                          key={i}
                          className="p-2 bg-white bg-opacity-50 rounded"
                        >
                          {doc.substring(0, 100)}...
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce delay-100">●</div>
                <div className="animate-bounce delay-200">●</div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-gray-200 p-4"
      >
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
