import React, {useEffect, useState} from 'react'
import {useRouter} from 'next/router'

export default function Session(){
  const r = useRouter()
  const {id} = r.query
  const [session, setSession] = useState(null)
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8030'

  useEffect(()=>{
    if(!id) return
    // If no judge token in sessionStorage, redirect to login page
    try{
      const tk = typeof window !== 'undefined' ? sessionStorage.getItem('judge_token') : null
      if(!tk){
        const next = `/session/${encodeURIComponent(id)}`
        window.location.href = `/judge-login?next=${encodeURIComponent(next)}`
        return
      }
    }catch(e){}
    fetch(`${backend}/admin/ui/session/${encodeURIComponent(id)}`).then(r=>r.json()).then(setSession).catch(()=>{})
  },[id])

  // Live SSE
  const startSSE = async ()=>{
    try{
      // Prefer judge proxy flow: prompt for judge secret (not ADMIN_API_KEY)
      const judgeKey = window.prompt('Enter judge secret for SSE (judge-only)')
      if(!judgeKey) return
      const tokRes = await fetch(`${backend}/admin/ui/token-proxy?session_id=${encodeURIComponent(id)}`, {method:'POST', headers: {'x-judge-token': judgeKey}})
      if(!tokRes.ok){ alert('Failed to get token (proxy)'); return }
      const data = await tokRes.json()
      const token = data.token
      const es = new EventSource(`${backend}/admin/ui/sse/session/${encodeURIComponent(id)}?token=${token}`)
      es.onmessage = (e)=>{ try{ location.reload() }catch(_){} }
      es.onerror = (ev)=>{ console.warn('SSE error', ev); es.close() }
    }catch(e){ console.warn(e); alert('SSE failed') }
  }

  if(!id) return <div>Loading...</div>
  return (
    <div style={{padding:20,fontFamily:'Arial'}}>
      <h2>Session {id}</h2>
      <div style={{marginBottom:10}}>
        <button onClick={startSSE}>Start Live SSE</button>
        <button onClick={async ()=>{
            // request CSV via proxy (prefer judge proxy)
            const judgeKey = window.prompt('Enter judge secret for CSV export (judge-only)')
            if(!judgeKey) return
            const res = await fetch(`${backend}/admin/ui/session/${encodeURIComponent(id)}/export.csv`, {headers: {'x-judge-token': judgeKey}})
            if(!res.ok){ alert('Export failed'); return }
            const blob = await res.blob()
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a'); a.href = url; a.download = `session_${id}.csv`; a.click();
        }}>Export CSV</button>
        <button onClick={()=>{ navigator.clipboard.writeText(JSON.stringify(session||{},null,2)) }}>Copy JSON</button>
      </div>
      {session ? <pre>{JSON.stringify(session, null, 2)}</pre> : <div>Loading...</div>}
    </div>
  )
}
