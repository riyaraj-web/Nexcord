'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { channelsAPI, messagesAPI } from '@/lib/api'
import { wsService } from '@/lib/websocket'
import toast from 'react-hot-toast'
import ChannelList from '@/components/ChannelList'
import MessageList from '@/components/MessageList'
import MessageInput from '@/components/MessageInput'

export default function ChatPage() {
  const router = useRouter()
  const [channels, setChannels] = useState<any[]>([])
  const [selectedChannel, setSelectedChannel] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    loadChannels()
    
    // Connect WebSocket
    const userId = getUserIdFromToken(token)
    if (userId) {
      wsService.connect(userId)
      
      wsService.onMessage((data) => {
        if (data.type === 'message' && data.channel_id === selectedChannel?.id) {
          setMessages((prev) => [...prev, data])
        }
      })
    }

    return () => {
      wsService.disconnect()
    }
  }, [router])

  useEffect(() => {
    if (selectedChannel) {
      loadMessages(selectedChannel.id)
    }
  }, [selectedChannel])

  const getUserIdFromToken = (token: string) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.sub
    } catch {
      return null
    }
  }

  const loadChannels = async () => {
    try {
      const response = await channelsAPI.list()
      setChannels(response.data)
      if (response.data.length > 0) {
        setSelectedChannel(response.data[0])
      }
    } catch (error: any) {
      console.error('Failed to load channels:', error)
      // Don't show error toast, just set empty state
      setChannels([])
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (channelId: string) => {
    try {
      const response = await messagesAPI.list(channelId)
      setMessages(response.data.reverse())
    } catch (error: any) {
      console.error('Failed to load messages:', error)
      setMessages([])
    }
  }

  const handleSendMessage = async (content: string) => {
    if (!selectedChannel) return

    try {
      const response = await messagesAPI.create({
        channel_id: selectedChannel.id,
        content,
      })
      
      // Add the new message to the local state immediately
      setMessages((prev) => [...prev, response.data])
      
      // Also reload messages to ensure sync
      loadMessages(selectedChannel.id)
      
      wsService.sendMessage(selectedChannel.id, content)
    } catch (error: any) {
      console.error('Send message error:', error)
      toast.error(error.response?.data?.detail || 'Failed to send message')
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
    <div className="flex h-screen bg-gray-100">
      <ChannelList
        channels={channels}
        selectedChannel={selectedChannel}
        onSelectChannel={setSelectedChannel}
        onCreateChannel={loadChannels}
      />
      <div className="flex-1 flex flex-col">
        {selectedChannel ? (
          <>
            <div className="bg-white border-b px-6 py-4">
              <h2 className="text-xl font-semibold">{selectedChannel.name}</h2>
              <p className="text-sm text-gray-500">{selectedChannel.description}</p>
            </div>
            <MessageList messages={messages} />
            <MessageInput onSend={handleSendMessage} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a channel to start chatting
          </div>
        )}
      </div>
    </div>
  )
}
