"use client"
import { useState, useRef, useEffect } from "react"
import axios from "axios"
import { BACKEND } from "@/lib/api"
import Link from "next/link"
import {
  Send,
  Loader2,
  Bot,
  User,
  HeartPulse,
  ArrowLeft,
  Trash2,
  Terminal,
  Activity,
  Cpu,
  Fingerprint,
  Sun,
  Moon
} from "lucide-react"
import { cn } from "@/lib/utils"
import ThemeToggle from "@/components/ThemeToggle"
import ReactMarkdown from 'react-markdown'

interface Message {
  role: "user" | "assistant"
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg: Message = { role: "user", content: input }
    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const response = await axios.post(`${BACKEND}/ask`, { question: input })
      setMessages(prev => [...prev, { role: "assistant", content: response.data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "AI Core Offline: Network request failed." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-background relative animate-nothing">

      {/* Industrial Header */}
      <header className="border-b border-border p-4 flex items-center justify-between bg-card relative z-20">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-7 h-7 flex items-center justify-center border border-border rounded-full bg-card group-hover:bg-primary transition-colors">
              <HeartPulse className="w-4 h-4 text-foreground" />
            </div>
            <span className="n-dot font-black text-sm uppercase tracking-tighter">medibotix</span>
          </Link>
          <div className="hidden md:flex items-center gap-4 border-l border-border pl-6">
            <div className="flex items-center gap-2 text-[10px] n-dot text-muted">
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              SESSION: ACTIVE
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link href="/upload" className="btn-nothing h-9 px-4 text-[10px]">
            UPLOAD NEW
          </Link>
          <button onClick={() => setMessages([])} className="btn-nothing h-9 px-4 text-[10px] hover:text-primary">
            RESET
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">

        {/* Workspace Area */}
        <main className="flex-1 flex flex-col min-w-0">
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 md:p-12 space-y-12"
          >
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto space-y-8">
                <div className="w-20 h-20 border border-border rounded-full flex items-center justify-center relative bg-secondary">
                  <Fingerprint className="w-10 h-10 opacity-20" />
                  <div className="absolute inset-0 border-t-2 border-primary rounded-full animate-spin" />
                </div>
                <div>
                  <h2 className="n-serif text-3xl mb-4 italic">Workspace ID: Analysis</h2>
                  <p className="text-[10px] text-muted n-dot tracking-widest uppercase">The ingested report is mapped to memory. Submit query to continue.</p>
                </div>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div
                  key={i}
                  className={cn(
                    "flex flex-col space-y-2 animate-nothing",
                    msg.role === "assistant" ? "items-start" : "items-end"
                  )}
                >
                  <div className="flex items-center gap-2 text-[9px] n-dot text-foreground/60 px-2 font-bold uppercase tracking-wider">
                    {msg.role === "assistant" ? <Bot className="w-3 h-3" /> : <User className="w-3 h-3" />}
                    {msg.role === "assistant" ? "Medibotix" : "User"}
                  </div>

                  <div className={cn(
                    "p-6 max-w-[90%] md:max-w-[75%] shadow-sm rounded-[24px] border transition-all",
                    msg.role === "assistant"
                      ? "bg-card border-border text-foreground"
                      : "bg-primary text-[#000000] border-primary font-bold"
                  )}>
                    <div className="text-xs md:text-sm leading-relaxed font-mono whitespace-pre-wrap">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-black border-b-[3px] border-primary/40 dark:border-primary/60 pb-0.5">{children}</strong>,
                          ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="flex flex-col space-y-2 animate-nothing">
                <div className="flex items-center gap-2 text-[9px] n-dot text-muted px-2">
                  <Loader2 className="w-3 h-3 animate-spin text-primary" />
                  AI_CORE_PROCESSING...
                </div>
                <div className="nothing-widget p-6 w-32 flex justify-between">
                  <div className="w-1 h-3 bg-primary animate-bounce" />
                  <div className="w-1 h-3 bg-primary animate-bounce [animation-delay:-0.1s]" />
                  <div className="w-1 h-3 bg-primary animate-bounce [animation-delay:-0.2s]" />
                </div>
              </div>
            )}
          </div>

          {/* Terminal Input */}
          <div className="p-4 md:p-8 bg-card border-t border-border mt-auto">
            <div className="max-w-4xl mx-auto flex gap-4">
              <div className="flex-1 relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-primary font-mono text-sm opacity-50">&gt;_</div>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && sendMessage()}
                  placeholder="Enter Command or Question..."
                  className="w-full bg-background border border-border rounded-full px-12 py-3 text-sm n-dot focus:outline-none focus:border-primary transition-all shadow-inner"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className={cn(
                  "w-12 h-12 rounded-full border border-border flex items-center justify-center transition-all bg-card",
                  loading || !input.trim() ? "opacity-20" : "hover:bg-primary hover:border-primary hover:text-white"
                )}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
