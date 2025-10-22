import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { getAdvice, ResultsRequest } from '../api/client'

const TYPES = [
  { key: 'overall_analysis', label: 'Overall Analysis' },
  { key: 'meal_plan', label: 'Meal Plan' },
  { key: 'exercise_plan', label: 'Exercise Plan' },
  { key: 'supplement_advice', label: 'Supplements' },
  { key: 'risk_assessment', label: 'Risk Assessment' },
]

export default function AdvicePanel({ form }: { form: ResultsRequest }) {
  const [active, setActive] = useState<string>('overall_analysis')
  const [loading, setLoading] = useState(false)
  const [content, setContent] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)

  const load = async (type: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await getAdvice(type, form)
      setContent((c) => ({ ...c, [type]: res.content || res.error || '' }))
    } catch (e: any) {
      setError(e?.message || 'Failed to load advice')
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    // prefetch default
    load('overall_analysis')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  React.useEffect(() => {
    if (!content[active]) {
      load(active)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active])

  return (
    <div className="card p-4">
      <div className="flex gap-2 flex-wrap">
        {TYPES.map((t) => (
          <button
            key={t.key}
            onClick={() => setActive(t.key)}
            className={`px-3 py-1.5 rounded-md text-sm border ${active === t.key ? 'bg-primary-50 border-primary-200 text-primary-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}
            aria-pressed={active === t.key}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="mt-4 min-h-[160px]">
        {loading && <div className="animate-pulse text-slate-500">Generating {active.replace('_', ' ')}…</div>}
        {error && <div className="text-red-600">{error}</div>}
        <AnimatePresence mode="wait">
          <motion.div
            key={active + (loading ? '-loading' : '-ready')}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="prose max-w-none"
          >
            <ReactMarkdown>{content[active] || ''}</ReactMarkdown>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}

