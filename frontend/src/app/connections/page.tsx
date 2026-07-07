'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface WPConnection {
  id: string
  site_name: string
  site_url: string
  wp_username: string
  created_at: string
}

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<WPConnection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    site_name: '',
    site_url: '',
    wp_username: '',
    wp_app_password: ''
  })
  const router = useRouter()

  useEffect(() => {
    fetchConnections()
  }, [])

  const fetchConnections = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/wp-connections/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setConnections(data)
      } else {
        setError('Failed to load connections')
      }
    } catch (err) {
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const token = localStorage.getItem('token')
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/wp-connections/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setShowForm(false)
        setFormData({ site_name: '', site_url: '', wp_username: '', wp_app_password: '' })
        fetchConnections()
      } else {
        const err = await response.json()
        setError(err.detail || 'Failed to create connection')
      }
    } catch (err) {
      setError('Failed to connect to server')
    }
  }

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  }

  return (
    <main className="min-h-screen p-24 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">WordPress Connections</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-700 text-white px-4 py-2 rounded-lg hover:bg-blue-800"
          >
            {showForm ? 'Cancel' : 'Add Connection'}
          </button>
        </div>

        {error && (
          <p className="mb-4 text-sm text-red-600">{error}</p>
        )}

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">Site Name</label>
              <input
                type="text"
                value={formData.site_name}
                onChange={(e) => setFormData({...formData, site_name: e.target.value})}
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">Site URL</label>
              <input
                type="url"
                value={formData.site_url}
                onChange={(e) => setFormData({...formData, site_url: e.target.value})}
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                placeholder="https://example.com"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">WordPress Username</label>
              <input
                type="text"
                value={formData.wp_username}
                onChange={(e) => setFormData({...formData, wp_username: e.target.value})}
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">Application Password</label>
              <input
                type="password"
                value={formData.wp_app_password}
                onChange={(e) => setFormData({...formData, wp_app_password: e.target.value})}
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                required
              />
            </div>
            <button type="submit" className="bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800">
              Save Connection
            </button>
          </form>
        )}

        <div className="grid gap-4">
          {connections.map((conn) => (
            <div key={conn.id} className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-2">{conn.site_name}</h3>
              <p className="text-gray-600 mb-1">URL: {conn.site_url}</p>
              <p className="text-gray-600 mb-1">Username: {conn.wp_username}</p>
              <p className="text-xs text-gray-400">Created: {new Date(conn.created_at).toLocaleDateString()}</p>
            </div>
          ))}
          {connections.length === 0 && (
            <p className="text-gray-500 text-center py-8">No WordPress connections yet. Add one to get started.</p>
          )}
        </div>
      </div>
    </main>
  )
}
