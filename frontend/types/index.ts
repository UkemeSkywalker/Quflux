export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface UserRegistration {
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface UserUpdate {
  first_name?: string
  last_name?: string
}

export interface PlatformConnection {
  id: string
  user_id: string
  platform: 'twitter' | 'linkedin' | 'instagram' | 'facebook'
  platform_user_id: string
  platform_username: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Post {
  id: string
  user_id: string
  title?: string
  content: string
  media_files: string[]
  link_url?: string
  link_preview?: any
  ai_generated: boolean
  status: 'draft' | 'scheduled' | 'published' | 'failed'
  created_at: string
  updated_at: string
}

export interface Schedule {
  id: string
  post_id: string
  user_id: string
  scheduled_time: string
  platforms: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}