import React, {useEffect, useState} from 'react'

export default function Home(){
  const [sessions, setSessions] = useState([])
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8030'

  useEffect(()=>{
    fetch(`${backend}/health`).catch(()=>{})
    fetchSessions()
  }, [])

  async function fetchSessions(){
    try{
      const res = await fetch(`${backend}/admin/ui/sessions`)
      if(!res.ok) return
      const data = await res.json()
      setSessions(data)
    }catch(e){ console.warn(e) }
  }

  return (
    <div style={{padding:20,fontFamily:'Arial'}}>
      <h1>Sentinel — Judge Dashboard (Preview)</h1>
      <p>Simple read-only view. Use the Streamlit app for detailed session export.</p>
      <div style={{marginBottom:10}}>
        <a href="/judge-login" style={{marginRight:12}}>Judge Login</a>
        <button onClick={fetchSessions}>Refresh</button>
      </div>
      <ul>
        {sessions.map(s=> <li key={s.id}><a href={`/session/${encodeURIComponent(s.id)}`}>{s.id}</a> — {s.persona}</li>)}
      </ul>
    </div>
  )
}
