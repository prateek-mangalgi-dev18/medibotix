"use client"
import { useTheme } from '@/lib/ThemeContext'
import { Sun, Moon } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className="w-10 h-10 rounded-full bg-card border border-border flex items-center justify-center transition-colors hover:bg-foreground hover:text-background active:scale-95 z-50"
            aria-label="Toggle theme"
        >
            <AnimatePresence mode="wait" initial={false}>
                {theme === 'light' ? (
                    <motion.div
                        key="sun"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <Sun className="w-5 h-5" />
                    </motion.div>
                ) : (
                    <motion.div
                        key="moon"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <Moon className="w-5 h-5" />
                    </motion.div>
                )}
            </AnimatePresence>
        </button>
    )
}

