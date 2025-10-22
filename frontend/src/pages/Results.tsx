import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getResults, ResultsRequest } from '../api/client'
import AgeGauge from '../components/AgeGauge'
import BiomarkerGrid from '../components/BiomarkerGrid'
import AdvicePanel from '../components/AdvicePanel'

export default function Results() {
  const nav = useNavigate()
  const location = useLocation()
  const payload = (location.state || null) as ResultsRequest | null
  const [data, setData] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    if (!payload) {
      nav('/')
      return
    }
    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await getResults(payload)
        setData(res)
      } catch (e: any) {
        setError(e?.message || 'Failed to fetch results')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [payload])

  if (!payload) return null

  return (
    <div className="space-y-6" aria-live="polite">
      {loading && <div className="text-slate-500">Analyzing…</div>}
      {error && <div className="text-red-600">{error}</div>}
      {data && (
        <>
          <AgeGauge chronological={payload.age} biological={data.biological_age} />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 space-y-4">
              <BiomarkerGrid items={data.biomarkers} />
            </div>
            <div className="space-y-4">
              <div className="card p-4">
                <div className="text-sm text-slate-600">Overall Health Score</div>
                <div className="text-3xl font-bold">{data.overall_health_score}</div>
                <ul className="list-disc ml-5 text-sm text-slate-600 mt-3">
                  {data.concerns.map((c: string) => <li key={c}>{c}</li>)}
                </ul>
              </div>
              <AdvicePanel form={payload} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}

