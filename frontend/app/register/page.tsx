'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import RegisterForm from '@/components/auth/RegisterForm'
import Image from 'next/image'

export default function RegisterPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (user) {
    return null // Will redirect to dashboard
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Column - Background Image */}
      <div 
        className="hidden lg:flex lg:w-1/2 relative bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 0)), url('/signup.png')`
        }}
      >
        {/* <div className="flex items-center justify-center w-full p-12">
          <div className="text-center text-white">
            <h1 className="text-4xl font-bold mb-4">
              Welcome to Quflux
            </h1>
            <p className="text-xl opacity-90 max-w-md">
              Streamline your social media management with AI-powered content creation
            </p>
          </div>
        </div> */}
      </div>

      {/* Right Column - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-white px-6 py-12">
        <div className="w-full max-w-md">
          <RegisterForm onSuccess={() => router.push('/dashboard')} />
        </div>
      </div>
    </div>
  )
}