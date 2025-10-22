import axios from 'axios'

export interface ResultsRequest {
  age: number
  sex: 'Male' | 'Female'
  height_cm: number
  weight_kg: number
  biomarkers: Record<string, number>
}

export const api = axios.create({ baseURL: '/api' })

export async function getResults(payload: ResultsRequest) {
  const { data } = await api.post('/results', payload)
  return data
}

export async function getAdvice(type: string, payload: ResultsRequest) {
  const { data } = await api.post(`/advice/${type}`, payload)
  return data
}

