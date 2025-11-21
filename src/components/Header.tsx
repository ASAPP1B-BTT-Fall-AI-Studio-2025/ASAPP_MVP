'use client';

import { User } from 'lucide-react';

interface HeaderProps {
  onProfileClick?: () => void;
}

export default function Header({ onProfileClick }: HeaderProps) {
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

          {/* Right side - Profile */}
          <div className="flex items-center space-x-4">
            {/* Profile */}
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