import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const { login } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-white p-8 rounded shadow max-w-sm w-full">
        <h2 className="text-xl font-semibold mb-4">Login</h2>
        <button
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
          onClick={login}
        >
          Sign in (dev)
        </button>
      </div>
    </div>
  );
};

export default Login;


