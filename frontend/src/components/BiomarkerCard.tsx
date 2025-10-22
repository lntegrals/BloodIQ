import React from 'react'

export default function BiomarkerCard({
  name,
  value,
  unit,
  range,
  status,
  description
}: {
  name: string
  value: number
  unit: string
  range: string
  status: 'Low' | 'Normal' | 'High'
  description: string
}) {
  const chip = status === 'Normal' ? 'chip-normal' : status === 'Low' ? 'chip-low' : 'chip-high'
  const label = name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  return (
    <div className="card p-4" role="group" aria-label={`${label} biomarker`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium">{label}</div>
          <div className="text-sm text-slate-500">Range: {range}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-semibold">{value} <span className="text-sm text-slate-500">{unit}</span></div>
          <div className={chip + " inline-block mt-1"} aria-label={`Status ${status}`}>{status}</div>
        </div>
      </div>
      <div className="text-slate-600 text-sm mt-3">{description}</div>
    </div>
  )
}

