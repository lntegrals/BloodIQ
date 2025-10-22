import React from 'react'

export default function AgeGauge({ chronological, biological }: { chronological: number; biological: number }) {
  const min = 0
  const max = 120
  const pct = Math.min(100, Math.max(0, (biological / max) * 100))
  const good = biological <= chronological
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-slate-500 text-sm">Biological Age</div>
          <div className="text-3xl font-extrabold">{biological.toFixed(1)} yrs</div>
          <div className="text-sm text-slate-500">Chronological: {chronological} yrs</div>
        </div>
        <div className="relative w-28 h-28">
          <svg viewBox="0 0 36 36" className="w-28 h-28">
            <path className="text-slate-200" strokeWidth="3.8" stroke="currentColor" fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path className={good ? 'text-green-500' : 'text-red-500'} strokeWidth="3.8" strokeLinecap="round" stroke="currentColor" fill="none"
              strokeDasharray={`${pct}, 100`}
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <text x="18" y="20.35" className="text-sm" textAnchor="middle">{Math.round(pct)}%</text>
          </svg>
        </div>
      </div>
    </div>
  )
}

