
import React from 'react';
import { HoneyPotSession } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

interface DashboardProps {
  sessions: HoneyPotSession[];
}

const Dashboard: React.FC<DashboardProps> = ({ sessions }) => {
  const activeCount = sessions.filter(s => s.status === 'active').length;
  const scamCount = sessions.filter(s => s.scamDetected).length;
  
  const intelligenceCount = sessions.reduce((acc, s) => {
    return acc + 
           s.extractedIntelligence.bankAccounts.length + 
           s.extractedIntelligence.upiIds.length + 
           s.extractedIntelligence.phishingLinks.length +
           s.extractedIntelligence.phoneNumbers.length;
  }, 0);

  const mainStats = [
    { name: 'Active Ops', value: activeCount, color: '#3b82f6', icon: 'fa-satellite-dish' },
    { name: 'Detections', value: scamCount, color: '#ef4444', icon: 'fa-shield-virus' },
    { name: 'Intel Gathered', value: intelligenceCount, color: '#10b981', icon: 'fa-microchip' },
  ];

  const personaData = sessions.reduce((acc: any[], s) => {
    const existing = acc.find(p => p.name === s.persona);
    if (existing) existing.value++;
    else acc.push({ name: s.persona, value: 1 });
    return acc;
  }, []);

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {mainStats.map((stat, i) => (
          <div key={i} className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl shadow-xl hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm font-semibold uppercase tracking-wider">{stat.name}</span>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center`} style={{ backgroundColor: `${stat.color}20`, color: stat.color }}>
                <i className={`fas ${stat.icon}`}></i>
              </div>
            </div>
            <p className="text-4xl font-black text-slate-100">{stat.value}</p>
            <div className="mt-2 text-[10px] text-slate-500 font-mono">LIVE STATUS: SYNCED</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl shadow-xl h-80">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
            <i className="fas fa-chart-bar text-blue-500"></i>
            Intelligence Extraction Trend
          </h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sessions.slice(0, 7).reverse().map(s => ({ name: s.sessionId.slice(-4), intel: Object.values(s.extractedIntelligence).flat().length }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Bar dataKey="intel" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl shadow-xl h-80">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
            <i className="fas fa-users text-purple-500"></i>
            Persona Effectiveness
          </h3>
          <div className="flex items-center justify-center h-full pb-8">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={personaData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {personaData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-col gap-2 ml-4">
              {personaData.map((p, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                  <span className="text-slate-400">{p.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
