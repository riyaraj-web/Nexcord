'use client'

import { useState } from 'react'
import { PaperAirplaneIcon, PaperClipIcon } from '@heroicons/react/24/solid'
import { filesAPI } from '@/lib/api'
import toast from 'react-hot-toast'

interface MessageInputProps {
  onSend: (content: string) => void
}

export default function MessageInput({ onSend }: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [uploading, setUploading] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      onSend(message)
      setMessage('')
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const response = await filesAPI.upload(file)
      const fileUrl = response.data.url
      onSend(`📎 File uploaded: ${file.name}\n${fileUrl}`)
      toast.success('File uploaded!')
    } catch (error) {
      toast.error('Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white border-t p-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <label className="cursor-pointer">
          <input
            type="file"
            className="hidden"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          <div className="p-2 hover:bg-gray-100 rounded-lg transition">
            <PaperClipIcon className="w-6 h-6 text-gray-600" />
          </div>
        </label>
        <input
          type="text"
          placeholder="Type a message..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={uploading}
        />
        <button
          type="submit"
          disabled={!message.trim() || uploading}
          className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition disabled:opacity-50"
        >
          <PaperAirplaneIcon className="w-6 h-6" />
        </button>
      </form>
    </div>
  )
}
