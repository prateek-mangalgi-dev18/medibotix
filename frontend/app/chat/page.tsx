"use client"
import { useState, useRef, useEffect } from "react"
import axios from "axios"
import { BACKEND } from "@/lib/api"
import Link from "next/link"

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {

  const [q, setQ] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const ask = async () => {
    if (!q.trim()) return

    const userMessage: Message = { role: 'user', content: q }
    setMessages(prev => [...prev, userMessage])

    const currentQuestion = q
    setQ("")
    setLoading(true)

    try {
      const res = await axios.post(`${BACKEND}/ask?q=${currentQuestion}`)
      const aiMessage: Message = { role: 'assistant', content: res.data.answer }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask()
    }
  }

  const formatResponse = (text: string) => {
    const lines = text.split('\n')

    return lines.map((line, idx) => {
      const numberedMatch = line.match(/^(\d+\.\s+\*\*)(.*?)(\*\*:?\s*)(.*)/);
      if (numberedMatch) {
        return (
          <div key={idx} className="mb-3 animate-fadeIn">
            <span className="font-bold text-green-600 dark:text-green-400">{numberedMatch[1].replace('**', '')}{numberedMatch[2]}:</span>
            <span className="ml-1">{numberedMatch[4]}</span>
          </div>
        )
      }

      const parts = line.split(/(\*\*.*?\*\*)/g)

      return (
        <div key={idx} className={line.trim() === '' ? 'h-2' : 'mb-2 animate-fadeIn'}>
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              const boldText = part.slice(2, -1)
              return <strong key={i} className="font-bold text-green-600 dark:text-green-400">{boldText}</strong>
            }
            return <span key={i}>{part}</span>
          })}
        </div>
      )
    })
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-blue-950 dark:to-gray-900 transition-colors duration-500">

      {/* Header */}
      <div className="glass dark:glass-dark shadow-lg animate-fadeIn sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300">
                <span className="text-2xl">🏥</span>
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Medical AI Assistant</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">Understanding your health reports, simplified</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm font-medium px-4 py-2 rounded-lg hover:bg-white/50 dark:hover:bg-black/20"
              >
                ← Home
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">

        {messages.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-20 animate-fadeIn">
            <div className="text-7xl mb-6 animate-bounce">💬</div>
            <p className="text-2xl font-medium text-gray-700 dark:text-gray-200 mb-3">No messages yet</p>
            <p className="text-lg text-gray-500 dark:text-gray-400 mb-6">Ask a question about your uploaded medical document</p>
            <div className="max-w-md mx-auto glass dark:glass-dark p-6 rounded-2xl">
              <p className="text-sm text-gray-600 dark:text-gray-300 flex items-center justify-center gap-2">
                <span className="text-xl">💡</span>
                <span>I can only answer health-related questions from your documents</span>
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slideIn`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-6 py-4 shadow-lg transform hover:scale-[1.02] transition-all duration-300 ${msg.role === 'user'
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 text-white'
                : 'glass dark:glass-dark text-gray-800 dark:text-gray-100 border border-green-100 dark:border-green-900'
                }`}
            >
              <div className={`text-xs font-semibold mb-3 flex items-center gap-2 ${msg.role === 'user' ? 'text-blue-100' : 'text-green-600 dark:text-green-400'
                }`}>
                {msg.role === 'user' ? (
                  <>
                    <span className="text-base">👤</span>
                    <span>You</span>
                  </>
                ) : (
                  <>
                    <span className="text-base">🏥</span>
                    <span>Medical Assistant</span>
                  </>
                )}
              </div>
              <div className="leading-relaxed text-[15px]">
                {msg.role === 'assistant' ? formatResponse(msg.content) : msg.content}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-slideIn">
            <div className="glass dark:glass-dark text-gray-800 dark:text-gray-100 border border-green-100 dark:border-green-900 shadow-lg rounded-2xl px-6 py-4 max-w-2xl">
              <div className="text-xs font-semibold mb-3 flex items-center gap-2 text-green-600 dark:text-green-400">
                <span className="text-base">🏥</span>
                <span>Medical Assistant</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1">
                  <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-gray-600 dark:text-gray-300 text-sm">Analyzing your question...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="glass dark:glass-dark border-t-2 border-green-100 dark:border-green-900 px-6 py-5 shadow-2xl animate-fadeIn">
        <div className="max-w-4xl mx-auto flex gap-4">
          <textarea
            value={q}
            onChange={e => setQ(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your medical report... (Press Enter to send)"
            className="flex-1 border-2 border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-green-400 dark:focus:border-green-500 rounded-xl px-5 py-4 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-200 dark:focus:ring-green-800 resize-none transition-all placeholder-gray-400 dark:placeholder-gray-500"
            rows={2}
          />
          <button
            onClick={ask}
            disabled={loading || !q.trim()}
            className="bg-gradient-to-br from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white px-10 py-4 rounded-xl font-semibold transition-all shadow-lg hover:shadow-2xl transform hover:scale-105 disabled:hover:scale-100 duration-300 flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <span className="text-xl">📤</span>
                <span>Send</span>
              </>
            )}
          </button>
        </div>
      </div>

    </div>
  )
}
