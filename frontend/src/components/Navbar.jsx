import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-gray-900">
            Agentic Sandbox
          </Link>

          <div className="flex space-x-6">
            <Link
              to="/"
              className="text-gray-600 hover:text-gray-900 transition"
            >
              Home
            </Link>
            <Link
              to="/create"
              className="text-gray-600 hover:text-gray-900 transition"
            >
              Create Agent
            </Link>
            <Link
              to="/audit-logs"
              className="text-gray-600 hover:text-gray-900 transition"
            >
              Audit Logs
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
