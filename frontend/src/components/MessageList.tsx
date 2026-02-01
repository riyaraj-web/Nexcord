'use client'

import { useEffect, useRef } from 'react'
import { format } from 'date-fns'

interface MessageListProps {
  messages: any[]
}

export default function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-white">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          No messages yet. Start the conversation!
        </div>
      ) : (
        messages.map((message) => (
          <div key={message.id} className="flex gap-3">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
              {message.user_id?.substring(0, 2).toUpperCase() || 'U'}
            </div>
            <div className="flex-1">
              <div className="flex items-baseline gap-2">
                <span className="font-semibold text-gray-900">
                  User {message.user_id?.substring(0, 8)}
                </span>
                <span className="text-xs text-gray-500">
                  {format(new Date(message.created_at), 'HH:mm')}
                </span>
              </div>
              <p className="text-gray-800 mt-1">{message.content}</p>
              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-2 space-y-2">
                  {message.attachments.map((attachment: any, idx: number) => (
                    <div key={idx} className="text-sm text-blue-600 hover:underline">
                      📎 {attachment.filename}
                    </div>
                  ))}
                </div>
              )}
              {message.reactions && Object.keys(message.reactions).length > 0 && (
                <div className="flex gap-2 mt-2">
                  {Object.entries(message.reactions).map(([emoji, users]: any) => (
                    <span
                      key={emoji}
                      className="bg-gray-100 px-2 py-1 rounded-full text-sm"
                    >
                      {emoji} {users.length}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  )
}
