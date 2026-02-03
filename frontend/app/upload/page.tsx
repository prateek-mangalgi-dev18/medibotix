"use client"
import { useState } from "react"
import axios from "axios"
import { BACKEND } from "@/lib/api"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function UploadPage() {

  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const router = useRouter()

  const upload = async () => {
    if (!file) return

    setLoading(true)
    setError(null)

    try {
      const fd = new FormData()
      fd.append("file", file)

      const response = await axios.post(`${BACKEND}/upload`, fd)

      if (response.data.error) {
        setError(response.data.message || "Failed to upload file")
        setLoading(false)
        return
      }

      router.push("/chat")
    } catch (err: any) {
      setError(err.response?.data?.message || "Network error. Please check if the backend is running.")
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-blue-950 dark:to-gray-900 flex flex-col transition-colors duration-500">

      {/* Header */}
      <header className="glass dark:glass-dark animate-fadeIn">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300">
                <span className="text-2xl">🏥</span>
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">MediBotix</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">Your Medical AI Assistant</p>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-6 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
        <div className="max-w-2xl w-full">

          {/* Upload Card */}
          <div className="glass dark:glass-dark rounded-3xl shadow-2xl border-2 border-green-100 dark:border-green-900 p-10 transform hover:scale-[1.02] transition-all duration-500">

            <div className="text-center mb-8 animate-scaleIn">
              <div className="text-7xl mb-4 animate-bounce">📄</div>
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">Upload Medical Report</h2>
              <p className="text-gray-600 dark:text-gray-300 text-lg">Upload your medical documents to get started</p>
            </div>

            {/* Drag & Drop Area */}
            <div
              className={`mb-6 border-3 border-dashed rounded-2xl p-12 transition-all duration-300 ${dragActive
                ? 'border-green-500 bg-green-50 dark:bg-green-900/20 scale-105'
                : 'border-gray-300 dark:border-gray-600 hover:border-green-400 dark:hover:border-green-500'
                }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="text-center">
                <div className="text-5xl mb-4">☁️</div>
                <label className="cursor-pointer">
                  <span className="text-lg font-semibold text-gray-700 dark:text-gray-200 hover:text-green-600 dark:hover:text-green-400 transition-colors">
                    Click to browse
                  </span>
                  <span className="text-gray-500 dark:text-gray-400"> or drag and drop</span>
                  <input
                    type="file"
                    accept=".pdf,.txt"
                    onChange={e => setFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">PDF or TXT files only</p>
              </div>
            </div>

            {/* Selected File */}
            {file && (
              <div className="mb-6 animate-scaleIn">
                <div className="flex items-center justify-between gap-3 p-4 bg-green-50 dark:bg-green-900/30 border-2 border-green-200 dark:border-green-700 rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">📎</span>
                    <div>
                      <p className="font-semibold text-green-800 dark:text-green-300">{file.name}</p>
                      <p className="text-xs text-green-600 dark:text-green-400">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-red-500 hover:text-red-700 dark:hover:text-red-400 transition-colors p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path>
                    </svg>
                  </button>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-5 bg-red-50 dark:bg-red-900/30 border-l-4 border-red-500 text-red-700 dark:text-red-300 rounded-xl animate-scaleIn">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <p className="font-semibold text-lg">Upload Failed</p>
                    <p className="text-sm mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={upload}
              disabled={loading || !file}
              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white px-6 py-5 rounded-xl font-semibold text-lg transition-all shadow-lg hover:shadow-2xl transform hover:scale-105 disabled:hover:scale-100 duration-300 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <span className="text-2xl">📤</span>
                  <span>Upload & Continue</span>
                </>
              )}
            </button>

            {/* Info */}
            <div className="mt-6 p-5 bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-500 rounded-xl animate-fadeIn" style={{ animationDelay: '0.4s' }}>
              <div className="flex items-start gap-3">
                <span className="text-xl">💡</span>
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  <span className="font-semibold">Tip:</span> Your medical reports are processed securely. We support PDF and text files up to 10MB.
                </p>
              </div>
            </div>

          </div>

          {/* Additional Info Cards */}
          <div className="grid md:grid-cols-3 gap-4 mt-6">
            <div className="glass dark:glass-dark p-4 rounded-xl text-center transform hover:scale-105 transition-all duration-300 animate-fadeIn" style={{ animationDelay: '0.5s' }}>
              <div className="text-3xl mb-2">🔒</div>
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">Secure</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Encrypted upload</p>
            </div>
            <div className="glass dark:glass-dark p-4 rounded-xl text-center transform hover:scale-105 transition-all duration-300 animate-fadeIn" style={{ animationDelay: '0.6s' }}>
              <div className="text-3xl mb-2">⚡</div>
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">Fast</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Instant processing</p>
            </div>
            <div className="glass dark:glass-dark p-4 rounded-xl text-center transform hover:scale-105 transition-all duration-300 animate-fadeIn" style={{ animationDelay: '0.7s' }}>
              <div className="text-3xl mb-2">🎯</div>
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">Accurate</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">AI-powered analysis</p>
            </div>
          </div>

        </div>
      </div>

    </div>
  )
}
