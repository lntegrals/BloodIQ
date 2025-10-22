import React from 'react'

export default function App({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="text-xl font-bold text-primary-700">BloodLens</div>
          <div className="text-sm text-slate-500">AI Blood Test Interpreter</div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      <footer className="py-8 text-center text-sm text-slate-400">© {new Date().getFullYear()} BloodLens</footer>
    </div>
  )
}

