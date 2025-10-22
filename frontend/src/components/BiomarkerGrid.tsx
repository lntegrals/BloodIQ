import React from 'react'
import BiomarkerCard from './BiomarkerCard'

export default function BiomarkerGrid({ items }: { items: Array<any> }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((bm) => (
        <BiomarkerCard key={bm.name} {...bm} />
      ))}
    </div>
  )
}

