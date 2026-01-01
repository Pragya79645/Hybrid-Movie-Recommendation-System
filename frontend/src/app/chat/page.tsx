'use client';

import React, { useState, useEffect } from 'react';
import ChatBox from '@/components/ChatBox';
import Link from 'next/link';
import { getUserId } from '@/services/api';

export default function ChatPage() {
  const [userId, setUserId] = useState<string>('');

  // Initialize user ID on component mount
  useEffect(() => {
    const id = getUserId();
    setUserId(id);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                💬 Chat with Movie Assistant
              </h1>
              <p className="text-gray-600 mt-1">
                Ask questions and get personalized recommendations
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200">
                <span className="text-sm font-medium text-gray-700">
                  User ID:
                </span>
                <span className="text-sm text-gray-900 font-mono">
                  {userId || 'Loading...'}
                </span>
              </div>
              <Link
                href="/search"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                🔍 Search Movies
              </Link>
              <Link
                href="/"
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                🏠 Home
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <main className="flex-1 flex flex-col max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg flex-1 flex flex-col overflow-hidden">
          <ChatBox userId={userId} />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600">
            Powered by RAG and AI technology
          </p>
        </div>
      </footer>
    </div>
  );
}
