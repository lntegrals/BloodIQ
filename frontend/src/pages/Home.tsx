import React from 'react'
import { useNavigate } from 'react-router-dom'

const DEFAULT_FIELDS: Array<{ key: string; label: string; type?: string; step?: string }> = [
  { key: 'glucose', label: 'Glucose (mg/dL)' },
  { key: 'albumin', label: 'Albumin (g/dL)', step: '0.1' },
  { key: 'creatinine', label: 'Creatinine (mg/dL)', step: '0.1' },
  { key: 'crp', label: 'CRP (mg/L)', step: '0.1' },
  { key: 'lymph_pct', label: 'Lymphocytes (%)', step: '0.1' },
  { key: 'mcv', label: 'MCV (fL)', step: '0.1' },
  { key: 'rdw', label: 'RDW (%)', step: '0.1' },
  { key: 'alk_phos', label: 'Alkaline Phosphatase (U/L)' },
  { key: 'wbc', label: 'WBC (10^3/µL)', step: '0.1' },
]

export default function Home() {
  const nav = useNavigate()
  const [form, setForm] = React.useState({
    age: 30,
    sex: 'Male',
    height_cm: 175,
    weight_kg: 70,
    biomarkers: Object.fromEntries(DEFAULT_FIELDS.map((f) => [f.key, ''])) as Record<string, string>,
  })

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload = {
      age: Number(form.age),
      sex: form.sex as 'Male' | 'Female',
      height_cm: Number(form.height_cm),
      weight_kg: Number(form.weight_kg),
      biomarkers: Object.fromEntries(
        Object.entries(form.biomarkers).filter(([, v]) => v !== '').map(([k, v]) => [k, Number(v)])
      ),
    }
    nav('/results', { state: payload })
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6" aria-label="BloodLens Input Form">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <label className="block text-sm text-slate-600">Age</label>
          <input aria-label="Age" type="number" className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2"
                 value={form.age} onChange={(e) => setForm({ ...form, age: Number(e.target.value) })} />
        </div>
        <div className="card p-4">
          <label className="block text-sm text-slate-600">Sex</label>
          <select aria-label="Sex" className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2"
                  value={form.sex} onChange={(e) => setForm({ ...form, sex: e.target.value })}>
            <option>Male</option>
            <option>Female</option>
          </select>
        </div>
        <div className="card p-4">
          <label className="block text-sm text-slate-600">Height (cm)</label>
          <input aria-label="Height cm" type="number" className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2"
                 value={form.height_cm} onChange={(e) => setForm({ ...form, height_cm: Number(e.target.value) })} />
        </div>
        <div className="card p-4">
          <label className="block text-sm text-slate-600">Weight (kg)</label>
          <input aria-label="Weight kg" type="number" className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2"
                 value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: Number(e.target.value) })} />
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-2">Biomarkers</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {DEFAULT_FIELDS.map((f) => (
            <div key={f.key} className="card p-4">
              <label className="block text-sm text-slate-600">{f.label}</label>
              <input aria-label={f.label} type="number" step={f.step || '1'} className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2"
                     value={form.biomarkers[f.key] ?? ''}
                     onChange={(e) => setForm({ ...form, biomarkers: { ...form.biomarkers, [f.key]: e.target.value } })}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <button type="submit" className="bg-primary-600 text-white px-5 py-2 rounded-md shadow hover:bg-primary-700">Analyze</button>
        <button type="button" className="px-4 py-2 rounded-md border border-slate-300"
                onClick={() => setForm({
                  ...form,
                  biomarkers: {
                    glucose: '85', albumin: '4.7', creatinine: '0.9', crp: '0.5', lymph_pct: '30', mcv: '90', rdw: '12.5', alk_phos: '80', wbc: '6.5'
                  }
                })}
        >Fill Sample Data</button>
      </div>
    </form>
  )
}

