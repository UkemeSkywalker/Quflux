'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { api } from '@/lib/api'
import { User, AuthToken, UserLogin, UserRegistration } from '@/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (credentials: UserLogin) => Promise<void>
  register: (userData: UserRegistration) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setLoading(false)
        return
      }

      // Verify token and get user info
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      // Token is invalid, remove it
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials: UserLogin) => {
    try {
      const response = await api.post<AuthToken>('/auth/login', credentials)
      const { access_token, user: userData } = response.data

      // Store token
      localStorage.setItem('access_token', access_token)
      setUser(userData)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const register = async (userData: UserRegistration) => {
    try {
      const response = await api.post<AuthToken>('/auth/register', userData)
      const { access_token, user: newUser } = response.data

      // Store token
      localStorage.setItem('access_token', access_token)
      setUser(newUser)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      // If refresh fails, user might be logged out
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}