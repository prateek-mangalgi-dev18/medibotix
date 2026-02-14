"use client"
import Link from "next/link"
import {
  FileText,
  Bot,
  MessageSquare,
  Upload,
  HeartPulse,
  Activity,
  ArrowUpRight,
  Shield,
  Zap
} from "lucide-react"
import ThemeToggle from "@/components/ThemeToggle"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col p-4 md:p-8 relative">
      {/* Nothing Style Navigation */}
      <nav className="flex items-center justify-between mb-16 px-4 relative z-10">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 flex items-center justify-center border border-border rounded-full bg-card group-hover:bg-primary transition-colors">
            <HeartPulse className="w-4 h-4 text-foreground" />
          </div>
          <span className="n-dot font-bold text-lg tracking-tighter">medibotix</span>
        </Link>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link href="/upload" className="btn-nothing btn-nothing-primary">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero: Industrial Typography */}
      <main className="flex-1 max-w-7xl mx-auto w-full relative z-10">
        <div className="flex flex-col items-center text-center mb-32 animate-nothing">
          <div className="inline-block px-3 py-1 border border-border rounded-full text-[10px] n-dot mb-12">
           PATIENT DATA SIMPLIFIED
          </div>

          <h1 className="n-serif text-5xl md:text-8xl leading-[1.1] mb-12 max-w-4xl">
            Come to play with AI. Your reports <span className="text-primary italic">simplified</span>.
          </h1>

          <p className="text-sm text-muted max-w-lg n-dot leading-relaxed uppercase tracking-widest">
            Join thousands of users to build something uniquely yours, and discover the creativity of the MediBotix community.
          </p>
        </div>

        {/* Feature Cards Matrix */}
        <div className="grid md:grid-cols-3 gap-1 border-t border-l border-border mb-32 industrial-grid shadow-2xl shadow-black/5 dark:shadow-white/5">
          {features.map((feature, i) => (
            <div
              key={i}
              className="p-12 border-r border-b border-border bg-card/50 hover:bg-card transition-all group animate-nothing"
              style={{ animationDelay: `${0.1 + (i * 0.1)}s` }}
            >
              <div className="flex justify-between items-start mb-12">
                <div className="w-12 h-12 border border-border rounded-full flex items-center justify-center bg-background transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <feature.icon className="w-6 h-6" />
                </div>
              </div>

              <h3 className="n-serif text-3xl mb-4 italic">{feature.title}</h3>
              <p className="text-xs text-muted leading-relaxed uppercase tracking-tighter mb-8 font-medium">
                {feature.description}
              </p>

              <div className="h-[1px] w-full bg-border relative overflow-hidden bg-background">
                <div className="absolute inset-0 bg-primary translate-x-[-100%] group-hover:translate-x-0 transition-transform duration-500" />
              </div>
            </div>
          ))}
        </div>

        {/* Essential Action Box */}
        <div className="nothing-widget bg-card/80 backdrop-blur-md border-[2px] border-primary p-16 md:p-24 text-center overflow-hidden relative mb-24 shadow-2xl shadow-primary/10">
          <div className="absolute inset-0 dot-matrix opacity-10" />
          <div className="relative z-10">
            <h2 className="n-serif text-4xl md:text-6xl mb-12 italic text-foreground">
              Ready to start your analysis?
            </h2>
            <Link
              href="/upload"
              className="inline-flex items-center gap-4 px-12 py-5 bg-primary text-primary-foreground rounded-full n-dot text-sm font-bold uppercase tracking-widest hover:scale-105 transition-transform"
            >
              Upload Sample <ArrowUpRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </main>

    
    </div>
  )
}

const features = [
  {
    title: "Ingestion",
    description: "Pure document extraction. Minimalist processing paths for clinical data.",
    icon: FileText
  },
  {
    title: "Intelligence",
    description: "Decoding complex terminology, powered by Mistral AI.",
    icon: Bot
  },
  {
    title: "Interaction",
    description: "Quick responses within seconds.",
    icon: MessageSquare
  }
]
