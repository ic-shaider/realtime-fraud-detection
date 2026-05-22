import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, BarChart3, Activity, Zap } from 'lucide-react'

const API = 'http://localhost:8000/api/v1'

export default function App() {
  const [tab, setTab] = useState<'dashboard'|'transactions'|'alerts'|'agents'>('dashboard')
  const [dashboard, setDashboard] = useState<any>(null)
  const [transactions, setTransactions] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const [agents, setAgents] = useState<any>(null)

  useEffect(() => {
    fetch(`${API}/dashboard`).then(r=>r.json()).then(setDashboard).catch(console.error)
    fetch(`${API}/transactions`).then(r=>r.json()).then(d=>setTransactions(d.transactions)).catch(console.error)
    fetch(`${API}/alerts`).then(r=>r.json()).then(d=>setAlerts(d.alerts)).catch(console.error)
    fetch(`${API}/agents/status`).then(r=>r.json()).then(setAgents).catch(console.error)
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2"><Shield className="w-6 h-6 text-red-400"/>Fraud Detection</h1>
            <p className="text-sm text-gray-400">Real-time payment fraud scoring engine</p>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-green-400"/>
            <span className="text-sm text-green-400">{dashboard?.avg_processing_ms || 0}ms avg</span>
          </div>
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <nav className="flex space-x-1 mb-6 bg-gray-800 rounded-lg p-1">
          {[{id:'dashboard' as const,l:'Dashboard'},{id:'transactions' as const,l:'Transactions'},{id:'alerts' as const,l:'Alerts'},{id:'agents' as const,l:'Agents'}].map(t=>(
            <button key={t.id} onClick={()=>setTab(t.id)} className={`px-4 py-2 rounded-md text-sm font-medium ${tab===t.id?'bg-red-600 text-white':'text-gray-400 hover:bg-gray-700'}`}>{t.l}</button>
          ))}
        </nav>

        {tab==='dashboard' && dashboard && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                {label:'Total Transactions',value:dashboard.total_transactions,color:'text-blue-400'},
                {label:'Block Rate',value:`${dashboard.block_rate}%`,color:'text-red-400'},
                {label:'Avg Score',value:dashboard.avg_fraud_score.toFixed(3),color:'text-yellow-400'},
                {label:'Open Alerts',value:dashboard.open_alerts,color:'text-orange-400'},
              ].map(k=>(
                <div key={k.label} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <p className="text-sm text-gray-400">{k.label}</p>
                  <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <p className="text-3xl font-bold text-green-400">{dashboard.approved}</p>
                <p className="text-sm text-gray-400">Approved</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <p className="text-3xl font-bold text-yellow-400">{dashboard.flagged}</p>
                <p className="text-sm text-gray-400">Flagged</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <p className="text-3xl font-bold text-red-400">{dashboard.blocked}</p>
                <p className="text-sm text-gray-400">Blocked</p>
              </div>
            </div>
          </div>
        )}

        {tab==='transactions' && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-gray-700"><tr>
                <th className="px-4 py-3 text-left text-gray-400">ID</th>
                <th className="px-4 py-3 text-left text-gray-400">Biller</th>
                <th className="px-4 py-3 text-right text-gray-400">Amount</th>
                <th className="px-4 py-3 text-center text-gray-400">Channel</th>
                <th className="px-4 py-3 text-center text-gray-400">Score</th>
                <th className="px-4 py-3 text-center text-gray-400">Decision</th>
                <th className="px-4 py-3 text-center text-gray-400">Latency</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-700">
                {transactions.map(t=>(
                  <tr key={t.id} className="hover:bg-gray-750">
                    <td className="px-4 py-2 font-mono text-xs">{t.id}</td>
                    <td className="px-4 py-2">{t.biller}</td>
                    <td className="px-4 py-2 text-right">${t.amount?.toFixed(2)}</td>
                    <td className="px-4 py-2 text-center text-xs">{t.channel}</td>
                    <td className="px-4 py-2 text-center">
                      <span className={`font-mono ${t.fraud_score>0.5?'text-red-400':t.fraud_score>0.3?'text-yellow-400':'text-green-400'}`}>{t.fraud_score?.toFixed(3)}</span>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs ${t.decision==='block'?'bg-red-900 text-red-300':t.decision==='flag_review'?'bg-yellow-900 text-yellow-300':t.decision==='step_up_auth'?'bg-orange-900 text-orange-300':'bg-green-900 text-green-300'}`}>{t.decision}</span>
                    </td>
                    <td className="px-4 py-2 text-center text-gray-400">{t.ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab==='alerts' && (
          <div className="space-y-3">
            {alerts.map((a,i)=>(
              <div key={i} className="bg-gray-800 border border-red-800 rounded-lg p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5"/>
                <div>
                  <p className="font-medium">{a.txn} — <span className="text-red-400">{a.type}</span></p>
                  <p className="text-sm text-gray-400">{a.desc}</p>
                  <p className="text-xs text-gray-500 mt-1">{a.time}</p>
                </div>
              </div>
            ))}
            {alerts.length===0 && <p className="text-center text-gray-500 py-8">No open alerts</p>}
          </div>
        )}

        {tab==='agents' && agents && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {agents.agents.map((a:any)=>(
              <div key={a.name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{a.name}</h4>
                  <span className="w-3 h-3 rounded-full bg-green-400"/>
                </div>
                <p className="text-sm text-gray-400">Processed: {a.records_processed}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
