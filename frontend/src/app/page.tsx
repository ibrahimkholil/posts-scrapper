'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface ImportJob {
  id: string
  source_url: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  wp_draft_url?: string
  error_log?: string
  created_at: string
}

export default function HomePage() {
  const [url, setUrl] = useState('')
  const [message, setMessage] = useState('')
  const [jobs, setJobs] = useState<ImportJob[]>([])
  const [connections, setConnections] = useState<{id: string, site_name: string}[]>([])
  const [selectedConnection, setSelectedConnection] = useState('')
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    fetchJobs()
    fetchConnections()
  }, [])

  const fetchJobs = async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setJobs(data.slice(0, 10))
      }
    } catch (err) {
      console.error('Failed to fetch jobs')
    }
  }

  const fetchConnections = async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/wp-connections/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setConnections(data)
        if (data.length > 0) {
          setSelectedConnection(data[0].id)
        }
      }
    } catch (err) {
      console.error('Failed to fetch connections')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const token = localStorage.getItem('token')
    
    if (!selectedConnection) {
      setMessage('Please select a WordPress connection first')
      return
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          source_url: url,
          target_wp_connection_id: selectedConnection
        })
      })

      if (response.ok) {
        setMessage('Job submitted successfully!')
        setUrl('')
        fetchJobs()
      } else {
        const error = await response.json()
        setMessage(`Error: ${error.detail}`)
      }
    } catch (err) {
      setMessage('Failed to submit job')
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'processing': return 'text-blue-600 bg-blue-100'
      case 'failed': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Blog Cloner</h1>
          <nav className="space-x-4">
            <Link href="/connections" className="text-blue-700 hover:underline">Connections</Link>
            <button onClick={() => { localStorage.removeItem('token'); router.push('/login') }} className="text-red-700 hover:underline">Logout</button>
          </nav>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="mb-4">
            <label htmlFor="connection" className="block mb-2 text-sm font-medium text-gray-700">
              Target WordPress Site
            </label>
            <select
              id="connection"
              value={selectedConnection}
              onChange={(e) => setSelectedConnection(e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            >
              {connections.map(conn => (
                <option key={conn.id} value={conn.id}>{conn.site_name}</option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label htmlFor="url" className="block mb-2 text-sm font-medium text-gray-700">
              Source URL
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
              placeholder="https://example.com/blog-post"
              required
            />
          </div>
          
          <button
            type="submit"
            className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center"
          >
            Import Blog Post
          </button>
          
          {message && (
            <p className={`mt-4 text-sm ${message.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>{message}</p>
          )}
        </form>

        <h2 className="text-xl font-semibold mb-4">Recent Jobs</h2>
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {jobs.map(job => (
                <tr key={job.id}>
                  <td className="px-6 py-4 text-sm text-gray-900 truncate max-w-xs">{job.source_url}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{new Date(job.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    {job.wp_draft_url ? (
                      <a href={job.wp_draft_url} target="_blank" rel="noopener noreferrer" className="text-blue-700 hover:underline text-sm">
                        View Draft
                      </a>
                    ) : job.error_log ? (
                      <span className="text-red-600 text-sm" title={job.error_log}>Error</span>
                    ) : (
                      <Link href={`/jobs/${job.id}`} className="text-blue-700 hover:underline text-sm">Details</Link>
                    )}
                  </td>
                </tr>
              ))}
              {jobs.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">No jobs yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}
