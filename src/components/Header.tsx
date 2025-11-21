'use client';

import { useState } from 'react';
import { User } from 'lucide-react';

interface HeaderProps {
  onProfileClick?: () => void;
  onSettingsClick?: () => void;
}

export default function Header({ onProfileClick, onSettingsClick }: HeaderProps) {
  const [showAuthOptions, setShowAuthOptions] = useState(false);

  return (
    <header className="bg-gradient-to-r from-blue-50 to-purple-50 shadow-sm border-b border-blue-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Extractify
              </h1>
            </div>
          </div>

          {/* Right side - Profile and Authentication */}
          <div className="flex items-center space-x-4">
            {/* Authentication Options (for future implementation) */}
            <div className="relative">
              <button
                onClick={() => setShowAuthOptions(!showAuthOptions)}
                className="text-gray-500 hover:text-gray-700 text-sm font-medium"
              >
                Authentication
              </button>
              
              {showAuthOptions && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
                  <div className="py-1">
                    <div className="px-4 py-2 text-xs text-gray-500 border-b">
                      Available options:
                    </div>
                    <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      GitHub
                    </button>
                    <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Google OAuth
                    </button>
                    <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Email + Password
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile */
            <button
              onClick={onProfileClick}
              className="flex items-center space-x-2 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              title="Profile"
            >
              <User className="w-5 h-5" />
              <span className="text-sm font-medium">Profile</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}