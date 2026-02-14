import type { Metadata } from "next";
import { Geist, Geist_Mono, Newsreader } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/lib/ThemeContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  style: "italic",
});

export const metadata: Metadata = {
  title: "MediBotix - Medical AI Assistant",
  description: "Understand your medical reports in simple language",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${newsreader.variable} antialiased min-h-screen relative`}
      >
        {/* Global Dot Matrix */}
        <div className="fixed inset-0 dot-matrix opacity-[0.05] dark:opacity-[0.1] z-0 pointer-events-none" />

        <ThemeProvider>
          <div className="flex flex-col min-h-screen relative z-10">
            {children}
          </div>
        </ThemeProvider>
      </body>



    </html>
  );
}
