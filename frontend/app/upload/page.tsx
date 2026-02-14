"use client"
import { useState } from "react"
import axios from "axios"
import { BACKEND } from "@/lib/api"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  Upload as UploadIcon,
  FileText,
  X,
  AlertCircle,
  ShieldCheck,
  ArrowLeft,
  Loader2,
  HeartPulse,
  Terminal,
  Activity
} from "lucide-react"
import { cn } from "@/lib/utils"
import ThemeToggle from "@/components/ThemeToggle"

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
      setError(err.response?.data?.message || "Network error. Check backend connection.")
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(e.type === "dragenter" || e.type === "dragover")
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.pdf') || droppedFile.name.endsWith('.txt')) {
        setFile(droppedFile)
      } else {
        setError("Invalid format. Use PDF or TXT.")
      }
    }
  }

  return (
    <div className="min-h-screen flex flex-col p-4 md:p-8 animate-nothing">

      {/* Nothing Nav */}
      <header className="flex items-center justify-between mb-12 relative z-10">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 flex items-center justify-center border border-border rounded-full bg-card group-hover:bg-primary transition-colors">
            <HeartPulse className="w-4 h-4 text-foreground" />
          </div>
          <span className="n-dot font-bold tracking-tighter">medibotix</span>
        </Link>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link href="/" className="btn-nothing h-10 px-4">
            <ArrowLeft className="w-4 h-4" />
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-2xl w-full mx-auto space-y-6">

        <div className="mb-12">
          <h2 className="n-serif text-5xl md:text-6xl mb-4 italic">UPLOAD.</h2>
          <p className="text-xs text-muted n-dot tracking-widest uppercase">Select Clinical Report for AI Processing</p>
        </div>

        {/* Upload Widget */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={cn(
            "nothing-widget p-16 border-dashed text-center flex flex-col items-center justify-center min-h-[400px] transition-all relative overflow-hidden",
            dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
          )}
        >
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={e => setFile(e.target.files?.[0] || null)}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />

          <div className="w-16 h-16 border border-border rounded-full flex items-center justify-center mb-8 bg-secondary">
            <UploadIcon className={cn("w-6 h-6", dragActive ? "text-primary" : "text-foreground")} />
          </div>

          <p className="n-dot font-bold text-sm mb-2">Drop Clinical Report</p>
          <p className="text-[10px] text-muted uppercase tracking-widest mb-12">PDF / TXT ONLY [10MB MAX]</p>

          {file && (
            <div className="nothing-widget p-4 bg-background border-primary border-[2px] flex items-center gap-4 w-full animate-nothing shadow-lg">
              <FileText className="w-5 h-5 text-primary" />
              <div className="flex-1 text-left">
                <p className="font-mono text-[10px] font-bold truncate max-w-[200px] text-foreground">{file.name}</p>
                <p className="text-[8px] text-muted opacity-100">FILE READY FOR ENGINE</p>
              </div>
              <button onClick={() => setFile(null)} className="hover:text-primary p-2">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="nothing-widget p-4 border-primary text-primary flex items-center gap-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <p className="text-[10px] n-dot font-bold">{error}</p>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={upload}
          disabled={loading || !file}
          className={cn(
            "btn-nothing btn-nothing-primary w-full py-4 text-base font-black n-dot",
            (loading || !file) && "opacity-20 cursor-not-allowed"
          )}
        >
          {loading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            "INITIALIZE"
          )}
        </button>

      </main>

    </div>
  )
}
