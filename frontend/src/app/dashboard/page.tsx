'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { analyticsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { 
  MessageSquare, 
  Users, 
  Shield,
  Activity,
  TrendingUp,
  Zap
} from 'lucide-react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function DashboardPage() {
  const router = useRouter()
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    loadAnalytics()
  }, [router])

  const loadAnalytics = async () => {
    try {
      const response = await analyticsAPI.dashboard()
      setAnalytics(response.data)
    } catch (error) {
      console.error('Analytics error:', error)
      // Set default values if analytics fails
      setAnalytics({
        active_users: 0,
        total_messages: 0,
        total_channels: 0,
        messages_today: 0,
        online_users: 0,
        ai_moderation_flags: 0
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Nexcord</h1>
                <p className="text-sm text-muted-foreground">Real-time collaborative messaging</p>
              </div>
            </div>
            <Link href="/chat">
              <Button size="lg">
                Open Chat
                <Zap className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Feature Badges */}
        <div className="flex flex-wrap gap-2 mb-8">
          <Badge variant="default" className="gap-1">
            <Activity className="w-3 h-3" />
            Live presence
          </Badge>
          <Badge variant="secondary" className="gap-1">
            <MessageSquare className="w-3 h-3" />
            Real-time messaging
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Shield className="w-3 h-3" />
            AI-powered moderation
          </Badge>
        </div>

        {/* Hero Section */}
        <Card className="mb-8 border-none shadow-lg bg-gradient-to-br from-white to-blue-50/50">
          <CardHeader className="pb-4">
            <CardTitle className="text-4xl">
              A collaborative command center for teams that ship.
            </CardTitle>
            <CardDescription className="text-lg mt-2">
              Real-time messaging, AI moderation, and seamless collaboration—wrapped in a modern interface. 
              Connect with your team instantly with WebSocket-powered chat.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Link href="/chat">
                <Button size="lg">Start Chatting</Button>
              </Link>
              <Button size="lg" variant="outline">View Features</Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics?.active_users || 0}</div>
              <p className="text-xs text-muted-foreground">Last 24 hours</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics?.total_messages || 0}</div>
              <p className="text-xs text-green-600">
                +{analytics?.messages_today || 0} today
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Online Now</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics?.online_users || 0}</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                Active connections
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Collaboration Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Collaboration Health</CardTitle>
                <Badge>Live workspace</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Channels</p>
                  <p className="text-2xl font-bold">{analytics?.total_channels || 0}</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Messages Today</p>
                  <p className="text-2xl font-bold">{analytics?.messages_today || 0}</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">AI Flags</p>
                  <p className="text-2xl font-bold">{analytics?.ai_moderation_flags || 0}</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium">Real-time Messaging</p>
                      <p className="text-sm text-muted-foreground">WebSocket connections active</p>
                    </div>
                  </div>
                  <Badge>Active</Badge>
                </div>

                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                      <Shield className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium">AI Moderation</p>
                      <p className="text-sm text-muted-foreground">Content safety enabled</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Protected</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {analytics?.online_users || 0}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Users Online</p>
                  <p className="text-xs text-muted-foreground">Active now</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {analytics?.total_channels || 0}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Active Channels</p>
                  <p className="text-xs text-muted-foreground">Available to join</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {analytics?.messages_today || 0}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Messages Today</p>
                  <p className="text-xs text-muted-foreground">Sent in last 24h</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
