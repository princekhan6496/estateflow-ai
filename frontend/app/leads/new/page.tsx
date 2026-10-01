'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Shell from '../../../components/Shell'
import { api } from '../../../lib/api'

export default function NewLead() {
  const router = useRouter()
  const [f, setF] = useState<any>({ name: '', location: 'Nagpur', property_requirement: '', budget: '', timeline: '1-3 months', customer_message: '', bhk: '3', parking_required: true })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const set = (k: string, v: any) => setF({ ...f, [k]: v })

  async function submit(e: any) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const l = await api('/leads', {
        method: 'POST',
        body: JSON.stringify({
          ...f,
          budget: Number(f.budget) * 100000,
          bhk: String(f.bhk).split(',').map((x: string) => Number(x.trim())).filter(Boolean),
        }),
      })
      router.push(`/leads/${l.id}`)
    } catch (e: any) {
      setError(e.message || 'Could not save the lead. Please check the fields and try again.')
    } finally {
      setBusy(false)
    }
  }

  return <Shell><div className="max-w-2xl px-6 md:px-10 py-8">
    <div className="mb-7"><h1 className="text-2xl font-semibold">New lead</h1><p className="text-sm muted mt-1">Capture customer context first. AI analysis is always explicit.</p></div>
    {error && <div className="mb-4 border border-neutral-200 bg-[#f7f7f5] rounded-lg p-3 text-sm">{error}</div>}
    <form onSubmit={submit} className="surface rounded-xl p-6 space-y-5">
      <div className="grid md:grid-cols-2 gap-4">
        <Field label="Name"><input required className="input" value={f.name} onChange={e => set('name', e.target.value)} /></Field>
        <Field label="Location"><input required className="input" value={f.location} onChange={e => set('location', e.target.value)} /></Field>
        <Field label="BHK preference"><input className="input" value={f.bhk} onChange={e => set('bhk', e.target.value)} placeholder="3 or 2,3,4" /></Field>
        <Field label="Budget (₹ lakh)"><input required min="1" type="number" className="input" value={f.budget} onChange={e => set('budget', e.target.value)} /></Field>
        <Field label="Buying timeline"><select className="input" value={f.timeline} onChange={e => set('timeline', e.target.value)}><option>1 month</option><option>1-3 months</option><option>3 months</option><option>3-6 months</option><option>6+ months</option></select></Field>
        <Field label="Parking"><select className="input" value={String(f.parking_required)} onChange={e => set('parking_required', e.target.value === 'true')}><option value="true">Required</option><option value="false">Not required</option></select></Field>
      </div>
      <Field label="Property requirement"><input required className="input" value={f.property_requirement} onChange={e => set('property_requirement', e.target.value)} /></Field>
      <Field label="Customer message"><textarea required className="input min-h-28" value={f.customer_message} onChange={e => set('customer_message', e.target.value)} /></Field>
      <div className="flex justify-end"><button disabled={busy} className="btn btn-primary">{busy ? 'Saving...' : 'Save lead'}</button></div>
    </form>
  </div></Shell>
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="label block mb-2">{label}</span>{children}</label>
}
