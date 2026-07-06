'use client'

import { useState } from 'react'

export default function Home() {
  const [url, setUrl] = useState('')
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_url: url,
          target_wp_connection_id: 'default-connection-id', // Replace with actual connection ID
        }),
      })

      if (response.ok) {
        setMessage('Job submitted successfully!')
        setUrl('')
      } else {
        const error = await response.json()
        setMessage(`Error: ${error.detail}`)
      }
    } catch (err) {
      setMessage('Failed to submit job')
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold mb-8">Blog Cloner</h1>
        
        <form onSubmit={handleSubmit} className="w-full max-w-md">
          <div className="mb-4">
            <label htmlFor="url" className="block mb-2 text-sm font-medium">
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
            <p className="mt-4 text-sm text-gray-600">{message}</p>
          )}
        </form>
      </div>
    </main>
  )
}
