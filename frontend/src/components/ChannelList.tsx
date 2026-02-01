'use client'

import { useState } from 'react'
import { channelsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { PlusIcon, HashtagIcon } from '@heroicons/react/24/outline'

interface ChannelListProps {
  channels: any[]
  selectedChannel: any
  onSelectChannel: (channel: any) => void
  onCreateChannel: () => void
}

export default function ChannelList({
  channels,
  selectedChannel,
  onSelectChannel,
  onCreateChannel,
}: ChannelListProps) {
  const [showModal, setShowModal] = useState(false)
  const [newChannel, setNewChannel] = useState({
    name: '',
    description: '',
    type: 'public',
  })

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await channelsAPI.create(newChannel)
      toast.success('Channel created!')
      setShowModal(false)
      setNewChannel({ name: '', description: '', type: 'public' })
      onCreateChannel()
    } catch (error: any) {
      console.error('Failed to create channel:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to create channel. Please check your connection.'
      toast.error(errorMessage)
    }
  }

  return (
    <>
      <div className="w-64 bg-gray-800 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Nexcord</h1>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-semibold text-gray-400">CHANNELS</h2>
              <button
                onClick={() => setShowModal(true)}
                className="text-gray-400 hover:text-white"
              >
                <PlusIcon className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-1">
              {channels.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => onSelectChannel(channel)}
                  className={`w-full flex items-center px-2 py-2 rounded hover:bg-gray-700 transition ${
                    selectedChannel?.id === channel.id ? 'bg-gray-700' : ''
                  }`}
                >
                  <HashtagIcon className="w-5 h-5 mr-2" />
                  <span className="truncate">{channel.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Create Channel</h2>
            <form onSubmit={handleCreateChannel} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Channel Name
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                  value={newChannel.name}
                  onChange={(e) =>
                    setNewChannel({ ...newChannel, name: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                  rows={3}
                  value={newChannel.description}
                  onChange={(e) =>
                    setNewChannel({ ...newChannel, description: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                  value={newChannel.type}
                  onChange={(e) =>
                    setNewChannel({ ...newChannel, type: e.target.value })
                  }
                >
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-primary text-white py-2 rounded-lg hover:bg-primary/90"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
