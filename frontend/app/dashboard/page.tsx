'use client'

import { useAuth } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome to your Dashboard, {user?.first_name || user?.email}!
              </h1>
              <p className="text-gray-600 mb-6">
                This is your social media management hub. Here you can create posts, 
                schedule content, and manage your social media accounts.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Create Post
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Compose and schedule your social media posts
                  </p>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Get Started
                  </button>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Connect Accounts
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Link your social media platforms
                  </p>
                  <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    Connect
                  </button>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    View Analytics
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Track your post performance
                  </p>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                    View Stats
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}