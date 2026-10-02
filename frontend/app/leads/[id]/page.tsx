'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Shell from '../../../components/Shell'
import Badge from '../../../components/Badge'
import PropertyCard from '../../../components/PropertyCard'
import { api } from '../../../lib/api'
import { Bot, Send, Plus, RefreshCw, RotateCcw } from 'lucide-react'
import { formatINR } from '../../../lib/format'

type Notice = { kind: 'analysis' | 'chat' | 'extract' | 'general'; message: string }

export default function LeadDetail() {
  const { id } = useParams()
  const [lead, setLead] = useState<any>()
  const [matches, setMatches] = useState<any[]>([])
  const [interactions, setInteractions] = useState<any[]>([])
  const [tab, setTab] = useState<'chat' | 'interaction'>('chat')
  const [msg, setMsg] = useState('')
  const [chat, setChat] = useState<any[]>([])
  const [busyAction, setBusyAction] = useState<string | null>(null)
  const [type, setType] = useState('Call')
  const [note, setNote] = useState('')
  const [change, setChange] = useState<any>()
  const [notice, setNotice] = useState<Notice | null>(null)
  const [lastChatQuestion, setLastChatQuestion] = useState('')
  const [lastExtractInteraction, setLastExtractInteraction] = useState<any>()

  async function load() {
    const [l, m, i] = await Promise.all([
      api(`/leads/${id}`),
      api(`/leads/${id}/matches`),
      api(`/leads/${id}/interactions`),
    ])
    setLead(l)
    setMatches(m)
    setInteractions(i)
  }

  useEffect(() => {
    load().catch((e: any) => setNotice({ kind: 'general', message: e.message || 'Could not load this lead.' }))
  }, [id])

  if (!lead) return <Shell><div className="p-10 muted">Loading lead...</div></Shell>

  async function analyze() {
    setBusyAction('analysis')
    setNotice(null)
    try {
      await api(`/leads/${id}/analyze`, { method: 'POST' })
      await load()
    } catch (e: any) {
      setNotice({ kind: 'analysis', message: 'AI analysis is temporarily unavailable.' })
    } finally {
      setBusyAction(null)
    }
  }

  async function send(question = msg) {
    const trimmed = question.trim()
    if (!trimmed) return
    setBusyAction('chat')
    setNotice(null)
    setLastChatQuestion(trimmed)
    try {
      const r = await api(`/leads/${id}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message: trimmed }),
      })
      setChat((current) => [...current, { q: trimmed, a: r.answer }])
      setMsg('')
    } catch (e: any) {
      setNotice({ kind: 'chat', message: 'AI assistant is temporarily unavailable. Please try again.' })
    } finally {
      setBusyAction(null)
    }
  }

  async function saveInteraction() {
    if (!note.trim()) return
    setBusyAction('save')
    setNotice(null)
    try {
      await api(`/leads/${id}/interactions`, {
        method: 'POST',
        body: JSON.stringify({ type, note }),
      })
      setNote('')
      await load()
      setTab('chat')
    } catch (e: any) {
      setNotice({ kind: 'general', message: e.message || 'Could not save the interaction.' })
    } finally {
      setBusyAction(null)
    }
  }

  async function extract(i: any) {
    setBusyAction('extract')
    setLastExtractInteraction(i)
    setNotice(null)
    try {
      const r = await api(`/leads/${id}/extract-requirement-changes?interaction_id=${i.id}`, { method: 'POST' })
      setChange({ interaction: i, result: r })
    } catch (e: any) {
      setNotice({ kind: 'extract', message: 'Could not safely detect requirement changes. Your interaction was saved, but no profile changes were applied.' })
    } finally {
      setBusyAction(null)
    }
  }

  async function apply() {
    if (!change?.interaction?.id) return
    setBusyAction('apply')
    setNotice(null)
    try {
      await api(`/leads/${id}/apply-requirement-changes?interaction_id=${change.interaction.id}`, { method: 'POST' })
      setChange(null)
      await load()
      setNotice({ kind: 'general', message: 'Profile updated. Recommendations refreshed.' })
    } catch (e: any) {
      setNotice({ kind: 'general', message: e.message || 'Could not apply the proposed changes.' })
    } finally {
      setBusyAction(null)
    }
  }

  return (
    <Shell>
      <div className="px-6 md:px-10 py-7">
        <div className="flex flex-wrap justify-between gap-4">
          <div>
            <div className="flex items-center gap-3"><h1 className="text-2xl font-semibold">{lead.name}</h1><Badge value={lead.priority} /></div>
            <div className="text-sm muted mt-1">{lead.location} · {lead.timeline} · score {lead.lead_score}</div>
          </div>
          <button onClick={analyze} disabled={busyAction === 'analysis'} className="btn btn-primary">
            {busyAction === 'analysis' ? 'Analyzing...' : lead.ai_analysis ? 'Re-analyze lead' : 'Analyze lead'}
          </button>
        </div>

        {notice && (
          <div className="mt-4 border border-neutral-200 bg-[#f7f7f5] rounded-lg p-3 text-sm flex items-center justify-between gap-4">
            <span>{notice.message}</span>
            {notice.kind === 'analysis' && <button onClick={analyze} disabled={busyAction !== null} className="btn py-1.5"><RotateCcw size={14} /> Try Again</button>}
            {notice.kind === 'chat' && <button onClick={() => send(lastChatQuestion)} disabled={busyAction !== null} className="btn py-1.5"><RotateCcw size={14} /> Try Again</button>}
            {notice.kind === 'extract' && lastExtractInteraction && <button onClick={() => extract(lastExtractInteraction)} disabled={busyAction !== null} className="btn py-1.5"><RotateCcw size={14} /> Try Again</button>}
          </div>
        )}

        <div className="grid lg:grid-cols-[1fr_360px] gap-5 mt-6">
          <div className="space-y-5">
            <section className="surface rounded-xl p-5">
              <div className="label mb-3">Customer wants</div>
              <div className="flex flex-wrap gap-2 text-sm">
                <span className="px-3 py-2 bg-[#f5f5f2] rounded-lg">{lead.bhk?.join(', ')} BHK</span>
                <span className="px-3 py-2 bg-[#f5f5f2] rounded-lg">≤ {formatINR(lead.budget)}</span>
                <span className="px-3 py-2 bg-[#f5f5f2] rounded-lg">{lead.location}</span>
                <span className="px-3 py-2 bg-[#f5f5f2] rounded-lg">{lead.parking_required ? 'Parking required' : 'Parking flexible'}</span>
              </div>
            </section>

            <section className="surface rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="label">AI summary</div>
                {lead.ai_analyzed_at && <div className="text-xs muted">Last analyzed: {new Date(lead.ai_analyzed_at).toLocaleString()}</div>}
              </div>
              {lead.ai_analysis ? <>
                <p className="text-sm leading-6">{lead.ai_analysis.summary}</p>
                <div className="grid md:grid-cols-2 gap-5 mt-5">
                  <Info title="Intent" items={[lead.ai_analysis.intent]} />
                  <Info title="Key requirements" items={lead.ai_analysis.key_requirements} />
                  <Info title="Concerns" items={lead.ai_analysis.objections} />
                  <Info title="Next action" items={[lead.ai_analysis.recommended_next_action]} />
                </div>
                <div className="mt-5 p-4 bg-[#f7f7f5] rounded-lg"><div className="label mb-2">Suggested response</div><p className="text-sm leading-6">{lead.ai_analysis.suggested_response}</p></div>
              </> : <p className="text-sm muted">No analysis stored yet. Click Analyze lead when you want to spend an AI request.</p>}
            </section>

            <section>
              <div className="flex justify-between items-center mb-3"><div><h2 className="font-semibold">Top property matches</h2><p className="text-xs muted mt-1">Deterministic backend scoring</p></div><RefreshCw size={15} className="muted" /></div>
              <div className="grid md:grid-cols-2 gap-3">
                {matches.slice(0, 6).map(m => <div key={m.id} className="space-y-2"><PropertyCard row={m} /><div className="flex items-center justify-between px-1"><label className="text-xs muted">Relationship status</label><select className="input py-1.5 text-xs w-auto" value={m.status} disabled={busyAction !== null} onChange={async e => { setBusyAction('status'); try { await api(`/leads/${id}/properties/${m.property_id}?status=${encodeURIComponent(e.target.value)}`, { method: 'PATCH' }); await load() } catch (err: any) { setNotice({ kind: 'general', message: err.message || 'Could not update property status.' }) } finally { setBusyAction(null) } }}>{['Recommended','Shortlisted','Shared','Site Visit Scheduled','Visited','Interested','Not Interested'].map(s => <option key={s}>{s}</option>)}</select></div></div>)}
              </div>
            </section>

            <section className="surface rounded-xl p-5">
              <div className="flex justify-between items-center mb-4"><div><h2 className="font-semibold">Customer journey</h2><p className="text-xs muted mt-1">History stays intact after profile changes.</p></div></div>
              <div className="space-y-4">{interactions.map(i => <div key={i.id} className="border-l-2 border-neutral-200 pl-4"><div className="flex justify-between text-xs"><span className="font-semibold">{i.type}</span><span className="muted"> {new Date(i.created_at).toLocaleString('en-IN', { day: '2-digit',  month: '2-digit', year: 'numeric',  hour: '2-digit',  minute: '2-digit',  second: '2-digit',   hour12: true,  })}</span></div><p className="text-sm mt-2">{i.note}</p>{i.ai_extracted_changes?.changes?.length > 0 && <button onClick={() => setChange({ interaction: i, result: i.ai_extracted_changes })} className="text-xs mt-2 underline">View proposed changes</button>}{!i.ai_extracted_changes && <button disabled={busyAction === 'extract'} onClick={() => extract(i)} className="text-xs mt-2 text-[#285943]">{busyAction === 'extract' ? 'Detecting changes...' : 'Analyze requirement changes'}</button>}</div>)}{!interactions.length && <p className="text-sm muted">No interactions yet.</p>}</div>
            </section>
          </div>

          <aside className="surface rounded-xl h-fit lg:sticky lg:top-5 overflow-hidden">
            <div className="p-4 border-b flex items-center gap-2"><Bot size={17} /><div><div className="font-semibold text-sm">Lead assistant</div><div className="text-[11px] muted">Context-only · explicit AI calls</div></div></div>
            <div className="p-4 min-h-80 max-h-[520px] overflow-auto space-y-4">{chat.length === 0 && <div className="text-sm muted leading-6">Ask about this customer's concerns, what to emphasize, or why a property matches. Unrelated questions are rejected.</div>}{chat.map((x, i) => <div key={i} className="space-y-2"><div className="text-xs font-semibold">You</div><div className="text-sm bg-[#f5f5f2] rounded-lg p-3">{x.q}</div><div className="text-xs font-semibold">Assistant</div><div className="text-sm leading-5">{x.a}</div></div>)}</div>
            <div className="p-3 border-t">{tab === 'chat' ? <><textarea className="input min-h-20 text-sm" placeholder="Ask about this lead..." value={msg} onChange={e => setMsg(e.target.value)} /><button onClick={() => send()} disabled={busyAction === 'chat' || !msg.trim()} className="btn btn-primary w-full mt-2"><Send size={14} /> {busyAction === 'chat' ? 'Thinking...' : 'Ask assistant'}</button><button onClick={() => setTab('interaction')} className="btn w-full mt-2"><Plus size={14} /> Log interaction</button></> : <><select className="input mb-2" value={type} onChange={e => setType(e.target.value)}><option>Call</option><option>WhatsApp</option><option>Site Visit</option><option>Meeting</option><option>Other</option></select><textarea className="input min-h-28 text-sm" placeholder="What did the customer say?" value={note} onChange={e => setNote(e.target.value)} /><button onClick={saveInteraction} disabled={busyAction === 'save' || !note.trim()} className="btn btn-primary w-full mt-2">{busyAction === 'save' ? 'Saving...' : 'Save interaction'}</button><button onClick={() => setTab('chat')} className="btn w-full mt-2">Back to assistant</button></>}</div>
          </aside>
        </div>
      </div>

      {change && <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50"><div className="surface rounded-xl max-w-lg w-full p-6"><h2 className="font-semibold">New customer information detected</h2><p className="text-xs muted mt-1">Review before changing the current lead profile.</p><div className="space-y-3 mt-5">{change.result.changes.map((c: any) => <div key={c.field} className="p-3 bg-[#f7f7f5] rounded-lg"><div className="label">{c.field}</div><div className="text-sm mt-1">{JSON.stringify(c.old_value)} → <b>{JSON.stringify(c.new_value)}</b></div><div className="text-xs muted mt-1">{c.reason}</div></div>)}</div><div className="flex justify-end gap-2 mt-5"><button onClick={() => setChange(null)} className="btn">Cancel</button><button onClick={apply} disabled={busyAction === 'apply'} className="btn btn-primary">{busyAction === 'apply' ? 'Applying...' : 'Apply updates'}</button></div></div></div>}
    </Shell>
  )
}

function Info({ title, items }: { title: string; items: string[] }) {
  return <div><div className="label mb-2">{title}</div><ul className="space-y-1">{items?.map((x: string) => <li key={x} className="text-sm">• {x}</li>)}</ul></div>
}
