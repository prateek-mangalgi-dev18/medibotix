"use client"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-blue-950 dark:to-gray-900 transition-colors duration-500">

      {/* Header */}
      <header className="glass dark:glass-dark sticky top-0 z-50 animate-fadeIn">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 animate-slideIn">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">🏥</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MediBotix</h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">Your Medical AI Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/upload"
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-2.5 rounded-lg font-semibold transition-all shadow-md hover:shadow-xl transform hover:scale-105 duration-300"
              >
                Get Started →
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 animate-fadeIn">
        <div className="text-center max-w-4xl mx-auto">
          <div className="text-7xl mb-6 animate-scaleIn">🏥💬</div>
          <h2 className="text-5xl font-bold text-gray-900 dark:text-white mb-6 animate-slideIn">
            Understand Your Medical Reports
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600 dark:from-blue-400 dark:to-green-400 mt-2">
              In Simple Language
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-10 leading-relaxed animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            Upload your medical reports and get clear, easy-to-understand explanations from our AI assistant.
            No medical degree required.
          </p>
          <div className="flex gap-4 justify-center animate-fadeIn" style={{ animationDelay: '0.4s' }}>
            <Link
              href="/upload"
              className="group bg-gradient-to-br from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-8 py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-2xl transition-all transform hover:scale-105 duration-300 flex items-center gap-2"
            >
              <span className="group-hover:rotate-12 transition-transform duration-300">📤</span>
              <span>Upload Report</span>
            </Link>
            <a
              href="#features"
              className="bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-200 px-8 py-4 rounded-xl font-semibold text-lg shadow-md hover:shadow-lg transition-all transform hover:scale-105 duration-300"
            >
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-16">
        <h3 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12 animate-fadeIn">
          How MediBotix Helps You
        </h3>

        <div className="grid md:grid-cols-3 gap-8">

          {/* Feature 1 */}
          <div className="group glass dark:glass-dark rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 animate-fadeIn border border-blue-100 dark:border-blue-900" style={{ animationDelay: '0.1s' }}>
            <div className="text-5xl mb-4 group-hover:scale-110 transition-transform duration-300">📄</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Upload Reports</h4>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Simply upload your medical reports in PDF or text format. We support all types of medical documents.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group glass dark:glass-dark rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 animate-fadeIn border border-green-100 dark:border-green-900" style={{ animationDelay: '0.2s' }}>
            <div className="text-5xl mb-4 group-hover:scale-110 transition-transform duration-300">🤖</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">AI Analysis</h4>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Our AI reads your reports and understands the medical information to provide accurate answers.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="group glass dark:glass-dark rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 animate-fadeIn border border-blue-100 dark:border-blue-900" style={{ animationDelay: '0.3s' }}>
            <div className="text-5xl mb-4 group-hover:scale-110 transition-transform duration-300">💬</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Simple Explanations</h4>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Ask questions and get clear answers in simple language that anyone can understand.
            </p>
          </div>

        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-900 dark:to-blue-950 py-16 mt-16 animate-fadeIn">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">

            <div className="text-white animate-slideIn">
              <h3 className="text-3xl font-bold mb-6">Why Choose MediBotix?</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 transform hover:translate-x-2 transition-transform duration-300">
                  <span className="text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-lg">Simple Language</p>
                    <p className="text-blue-100 dark:text-blue-200">No medical jargon - explanations anyone can understand</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 transform hover:translate-x-2 transition-transform duration-300">
                  <span className="text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-lg">Instant Answers</p>
                    <p className="text-blue-100 dark:text-blue-200">Get explanations in seconds, not days</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 transform hover:translate-x-2 transition-transform duration-300">
                  <span className="text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-lg">Medical Focus</p>
                    <p className="text-blue-100 dark:text-blue-200">Only answers health-related questions from your reports</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 transform hover:translate-x-2 transition-transform duration-300">
                  <span className="text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-lg">24/7 Available</p>
                    <p className="text-blue-100 dark:text-blue-200">Access your medical information anytime, anywhere</p>
                  </div>
                </li>
              </ul>
            </div>

            <div className="glass dark:glass-dark rounded-2xl p-8 border border-white/20 animate-scaleIn transform hover:scale-105 transition-all duration-500">
              <div className="text-6xl mb-4 text-center animate-bounce">🎯</div>
              <h4 className="text-2xl font-bold text-white text-center mb-4">Ready to Get Started?</h4>
              <p className="text-blue-100 dark:text-blue-200 text-center mb-6">
                Upload your medical report and start getting clear answers today
              </p>
              <Link
                href="/upload"
                className="block w-full bg-white dark:bg-gray-800 text-blue-700 dark:text-blue-400 px-6 py-4 rounded-xl font-bold text-lg text-center hover:bg-blue-50 dark:hover:bg-gray-700 transition-all shadow-lg transform hover:scale-105 duration-300"
              >
                Upload Your Report →
              </Link>
            </div>

          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 dark:bg-black text-gray-400 dark:text-gray-500 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="text-2xl">🏥</span>
            <span className="text-white font-bold text-lg">MediBotix</span>
          </div>
          <p className="text-sm">
            Your Medical AI Assistant - Understanding health reports made simple
          </p>
          <p className="text-xs mt-4 text-gray-500 dark:text-gray-600">
            ⚠️ Disclaimer: This is an educational tool. Always consult healthcare professionals for medical advice.
          </p>
        </div>
      </footer>

    </div>
  )
}
