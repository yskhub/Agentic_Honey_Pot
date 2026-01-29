import React, {useState, useEffect} from 'react'
import {useRouter} from 'next/router'

export default function JudgeLogin(){
  const router = useRouter()
  const [user,setUser]=useState('')
  const [passw,setPass]=useState('')
  const [msg,setMsg]=useState('')
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8030'
  const [nextUrl,setNextUrl] = useState('/')

  useEffect(()=>{
    const q = (typeof window !== 'undefined' && new URLSearchParams(window.location.search)) || null
    if(q && q.get('next')) setNextUrl(q.get('next'))
  }, [])

  async function submit(e){
    e.preventDefault()
    setMsg('')
    try{
      const res = await fetch(`${backend}/admin/ui/judge-login`, {method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username:user,password:passw})})
      if(!res.ok){ setMsg('Login failed'); return }
      const data = await res.json()
      sessionStorage.setItem('judge_token', data.token)
      setMsg('Token saved to session storage')
      // redirect to requested page
      try{ window.location.href = nextUrl }catch(e){ /* ignore */ }
    }catch(e){ setMsg('Error: '+String(e)) }
  }

  return (
    <div style={{padding:20,fontFamily:'Arial'}}>
      <h2>Judge Login</h2>
      <form onSubmit={submit}>
        <div><label>Username: <input value={user} onChange={e=>setUser(e.target.value)} /></label></div>
        <div><label>Password: <input type="password" value={passw} onChange={e=>setPass(e.target.value)} /></label></div>
        <div><button type="submit">Login & Store Token</button></div>
      </form>
      <div style={{marginTop:10,color:'#666'}}>{msg}</div>
      <p>After logging in, open a session page and click <b>Start Live SSE</b>.</p>
    </div>
  )
}
