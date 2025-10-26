export interface User {
  id: string
  email: string
  created_at: string
  updated_at: string
  is_active: boolean
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