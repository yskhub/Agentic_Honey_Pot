
import React, { useState, useEffect } from 'react';
import { HoneyPotSession } from './types';
import Dashboard from './components/Dashboard';
import SessionConsole from './components/SessionConsole';
import IntelligenceVault from './components/IntelligenceVault';

const INITIAL_SESSION: HoneyPotSession = {
  sessionId: `ST-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
  status: 'idle',
  persona: 'Elderly',
  strategy: 'Confused',
  scamDetected: false,
  confidenceScore: 0,
  engagementMetrics: {
    engagementDurationSeconds: 0,
    totalMessagesExchanged: 0,
    startTime: new Date().toISOString()
  },
  extractedIntelligence: {
    bankAccounts: [],
    upiIds: [],
    phishingLinks: [],
    phoneNumbers: [],
    suspiciousKeywords: [],
    scamTactics: [],
    emotionalManipulation: []
  },
  agentNotes: '',
  conversationHistory: [],
  metadata: {
    channel: 'Ingestion_Node_01',
    language: 'English',
    locale: 'GLOBAL'
  }
};

const App: React.FC = () => {
  const [sessions, setSessions] = useState<HoneyPotSession[]>([]);
  const [currentSession, setCurrentSession] = useState<HoneyPotSession>(INITIAL_SESSION);
  const [view, setView] = useState<'dashboard' | 'console'>('console');
  const [isReporting, setIsReporting] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('sentineltrap_sessions_v2');
    if (saved) setSessions(JSON.parse(saved));
  }, []);

  const handleUpdateSession = (updated: HoneyPotSession) => {
    setCurrentSession(updated);
  };

  const handleFinalize = async (session: HoneyPotSession) => {
    if (session.conversationHistory.length === 0) {
      alert("Operational Buffer Empty: No engagement data to transmit.");
      return;
    }
    
    setIsReporting(true);
    
    // Mandatory Final Result Callback Payload strictly following Requirement 12
    const intelligenceDict = {
      bankAccounts: session.extractedIntelligence.bankAccounts,
      upiIds: session.extractedIntelligence.upiIds,
      phishingLinks: session.extractedIntelligence.phishingLinks,
      phoneNumbers: session.extractedIntelligence.phoneNumbers,
      suspiciousKeywords: session.extractedIntelligence.suspiciousKeywords
    };

    const payload = {
      sessionId: session.sessionId,
      scamDetected: session.scamDetected,
      totalMessagesExchanged: session.conversationHistory.length,
      extractedIntelligence: intelligenceDict,
      agentNotes: session.agentNotes
    };

    try {
      // POST to GUVI evaluation endpoint as per Requirement 12
      const response = await fetch("https://hackathon.guvi.in/api/updateHoneyPotFinalResult", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'YOUR_SECRET_API_KEY' // User's secret key
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error("Callback failed");
      
      const finalizedSession = { ...session, status: 'completed' as const };
      const newSessions = [finalizedSession, ...sessions];
      setSessions(newSessions);
      localStorage.setItem('sentineltrap_sessions_v2', JSON.stringify(newSessions));
      
      alert("Final Intelligence Report sent to GUVI Evaluation Endpoint.");
      
      setCurrentSession({
        ...INITIAL_SESSION,
        sessionId: `ST-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
        engagementMetrics: { ...INITIAL_SESSION.engagementMetrics, startTime: new Date().toISOString() }
      });
      setView('dashboard');
    } catch (err) {
      console.error("Signal Transmission Interrupted:", err);
      alert("Transmission Error: Endpoint unresponsive. Check console for details.");
    } finally {
      setIsReporting(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-100 font-sans selection:bg-blue-500/30 selection:text-white">
      {/* Dynamic Background Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.05]" style={{ backgroundImage: 'linear-gradient(#4f46e5 0.5px, transparent 0.5px), linear-gradient(90deg, #4f46e5 0.5px, transparent 0.5px)', backgroundSize: '40px 40px' }}></div>
      
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col p-6 space-y-8 sticky top-0 h-screen overflow-y-auto z-50">
        <div className="flex items-center gap-3 mb-4 group cursor-default">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-blue-600/20 group-hover:rotate-12 transition-transform">
            <i className="fas fa-spider text-xl"></i>
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-black tracking-tighter uppercase italic">
              SENTINEL<span className="text-blue-500">TRAP</span>
            </h1>
            <span className="text-[8px] font-mono text-slate-600 uppercase tracking-widest">v2.5 Stable</span>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          <div className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] mb-4 pl-2">Operations</div>
          <button 
            onClick={() => setView('dashboard')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition-all ${view === 'dashboard' ? 'bg-slate-900 text-blue-400 border border-slate-800' : 'text-slate-400 hover:bg-slate-900/50'}`}
          >
            <i className="fas fa-grid-2"></i> Dashboard
          </button>
          <button 
            onClick={() => setView('console')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition-all ${view === 'console' ? 'bg-slate-900 text-blue-400 border border-slate-800' : 'text-slate-400 hover:bg-slate-900/50'}`}
          >
            <i className="fas fa-satellite"></i> Active Sessions
          </button>
          <div className="pt-4 text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] mb-4 pl-2">Intelligence</div>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-900/50">
            <i className="fas fa-microchip"></i> Pattern Analysis
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-900/50">
            <i className="fas fa-cog"></i> Settings
          </button>
        </nav>

        <div className="mt-auto pt-6 border-t border-slate-900">
          <div className="flex items-center gap-3 bg-slate-900/50 p-3 rounded-xl border border-slate-800 group hover:border-blue-500/30 transition-colors cursor-default">
            <div className="relative">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500 font-bold text-xs">AI</div>
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            </div>
            <div className="flex-1">
              <div className="text-[9px] font-black text-slate-500 uppercase">Core Status</div>
              <div className="text-[10px] text-emerald-500 font-bold">NOMINAL</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col p-8 space-y-6 overflow-y-auto">
        {/* Top Header Panel */}
        <div className="flex justify-between items-center bg-slate-900/40 p-5 rounded-2xl border border-slate-800/60 backdrop-blur-xl shadow-2xl">
          <div className="flex items-center gap-4">
             <div className="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_10px_#10b981] animate-pulse"></div>
             <div className="text-xs text-slate-400 font-mono tracking-tighter">
              SESSION_ID: <span className="text-slate-100 font-bold">{currentSession.sessionId}</span>
              <span className="mx-6 text-slate-800 opacity-30">|</span>
              AGENT_CLASS: <span className="text-blue-400 font-bold">{currentSession.persona.toUpperCase()}</span>
             </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 px-3 py-1.5 bg-slate-800 rounded-lg border border-slate-700">
               <i className="fas fa-shield-halved text-emerald-500 text-[10px]"></i>
               <span className="text-[9px] font-black text-slate-100 uppercase tracking-widest">Ethics_Module_ON</span>
            </div>
            <div className="flex gap-4 border-l border-slate-800 pl-6">
              <button className="text-slate-500 hover:text-slate-200 transition-colors"><i className="fas fa-bell"></i></button>
              <button className="text-slate-100 font-black text-[10px] bg-slate-800 px-4 py-2 rounded-xl border border-slate-700 hover:bg-slate-700 transition-colors uppercase tracking-widest">Analyst_V2</button>
            </div>
          </div>
        </div>

        {/* Real-time Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className={`p-6 rounded-3xl border-2 transition-all duration-500 ${currentSession.scamDetected ? 'bg-red-500/10 border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.1)]' : 'bg-slate-900/50 border-slate-800'}`}>
            <div className="flex justify-between items-start mb-2">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Scam Confidence</div>
              {currentSession.scamDetected && <i className="fas fa-exclamation-triangle text-red-500 animate-bounce"></i>}
            </div>
            <div className={`text-3xl font-black font-mono ${currentSession.scamDetected ? 'text-red-500' : 'text-slate-100'}`}>
              {(currentSession.confidenceScore * 100).toFixed(0)}%
            </div>
            <div className="mt-2 text-[8px] font-bold text-slate-600 uppercase tracking-widest">Vector Analysis: {currentSession.scamDetected ? 'MALICIOUS' : 'MONITORING'}</div>
          </div>
          
          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-3xl backdrop-blur-md shadow-xl">
            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-2">Engagement Duration</div>
            <div className="text-3xl font-black font-mono">
              {Math.floor(currentSession.engagementMetrics.engagementDurationSeconds / 60).toString().padStart(2, '0')}:{(currentSession.engagementMetrics.engagementDurationSeconds % 60).toString().padStart(2, '0')}
              <span className="text-xs ml-2 opacity-30 font-sans">MM:SS</span>
            </div>
            <div className="mt-2 text-[8px] font-bold text-slate-600 uppercase tracking-widest">Uptime Signal: STABLE</div>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-3xl backdrop-blur-md shadow-xl">
            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-2">Intelligence Units</div>
            <div className="text-3xl font-black font-mono text-blue-400">
              {currentSession.engagementMetrics.totalMessagesExchanged}
            </div>
            <div className="mt-2 text-[8px] font-bold text-slate-600 uppercase tracking-widest">Network Ingestion: ACTIVE</div>
          </div>
        </div>

        {/* Dynamic Workspace */}
        {view === 'dashboard' ? (
          <div className="space-y-6 animate-in fade-in duration-700">
            <Dashboard sessions={sessions} />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 flex-1 min-h-0">
            <div className="lg:col-span-2 h-full flex flex-col">
              <SessionConsole 
                session={currentSession} 
                onUpdate={handleUpdateSession} 
                onFinalize={handleFinalize}
              />
            </div>
            <div className="lg:col-span-1 h-full overflow-y-auto">
              <IntelligenceVault session={currentSession} />
            </div>
          </div>
        )}

        {/* Global Safety & Compliance Panel */}
        <div className="bg-slate-900/40 border border-slate-800/60 p-6 rounded-[2rem] backdrop-blur-md">
          <div className="flex flex-col md:flex-row gap-8 items-center">
            <div className="flex-1 space-y-4">
              <h2 className="font-black text-[11px] uppercase tracking-[0.3em] text-slate-500 flex items-center gap-2">
                <i className="fas fa-user-shield text-blue-500"></i>
                Compliance & Callback Matrix
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 bg-slate-950/50 p-3 rounded-xl border border-slate-800/40">
                   <i className="fas fa-check text-emerald-500 text-[10px]"></i>
                   <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Zero Impersonation</span>
                </div>
                <div className="flex items-center gap-3 bg-slate-950/50 p-3 rounded-xl border border-slate-800/40">
                   <i className="fas fa-check text-emerald-500 text-[10px]"></i>
                   <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Safe Data Protocol</span>
                </div>
              </div>
            </div>
            
            <div className="h-12 w-px bg-slate-800 hidden md:block"></div>

            <div className="flex-1 space-y-4">
               <div className="flex justify-between items-center px-1">
                 <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Callback Readiness</span>
                 <span className={`text-[10px] font-black uppercase ${currentSession.status === 'completed' ? 'text-emerald-500' : 'text-amber-500'}`}>
                   {currentSession.status === 'completed' ? 'SYNCHRONIZED' : 'BUFFERING'}
                 </span>
               </div>
               <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                  <div 
                    className="h-full bg-blue-600 shadow-[0_0_10px_#2563eb] transition-all duration-1000" 
                    style={{ width: `${Math.min((currentSession.engagementMetrics.totalMessagesExchanged / 20) * 100, 100)}%` }}
                  ></div>
               </div>
               <div className="flex justify-between text-[8px] font-mono text-slate-600 uppercase tracking-widest px-1">
                 <span>Session Capacity</span>
                 <span>{currentSession.engagementMetrics.totalMessagesExchanged} / 20 Turns</span>
               </div>
            </div>
          </div>
        </div>
      </main>

      {/* Submission Portal Overlay */}
      {isReporting && (
        <div className="fixed inset-0 bg-slate-950/98 backdrop-blur-3xl z-[200] flex flex-col items-center justify-center">
          <div className="relative">
             <div className="w-32 h-32 border-[10px] border-blue-500/10 border-t-blue-600 rounded-full animate-spin shadow-2xl"></div>
             <div className="absolute inset-0 flex items-center justify-center text-blue-500">
               <i className="fas fa-cloud-upload-alt text-4xl animate-pulse"></i>
             </div>
          </div>
          <div className="mt-12 text-center">
            <h3 className="text-4xl font-black uppercase tracking-tighter text-white italic">Transmitting Signal</h3>
            <p className="text-slate-500 text-xs font-mono mt-4 animate-pulse uppercase tracking-[0.5em]">Target: GUVI_EVAL_ENDPOINT_SECURE</p>
          </div>
          <div className="mt-16 w-80 h-1.5 bg-slate-900 rounded-full overflow-hidden shadow-2xl">
            <div className="h-full bg-blue-600 animate-[loading_1.5s_infinite] shadow-[0_0_20px_#2563eb]" style={{ width: '40%' }}></div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(300%); }
        }
        .custom-scrollbar::-webkit-scrollbar { width: 5px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #334155; }
      `}</style>
    </div>
  );
};

export default App;
