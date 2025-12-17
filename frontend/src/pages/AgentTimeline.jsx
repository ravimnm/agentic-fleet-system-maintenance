import React, { useEffect, useState, useContext } from 'react'
import { fetchAgentTimeline } from '../api/api'
import { AuthContext } from '../context/AuthContext'

const AgentTimeline = () => {
  const { auth } = useContext(AuthContext)
  const [vehicleId, setVehicleId] = useState('')
  const [timeline, setTimeline] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const demoTimeline = [
    {
      timestamp: '2025-12-17 14:32:15',
      agent: 'Diagnostics Agent',
      decision: 'Detected abnormal engine temperature pattern. Risk elevated to 0.72'
    },
    {
      timestamp: '2025-12-17 14:25:42',
      agent: 'Prediction Agent',
      decision: 'ML model predicts 65% probability of brake failure within 7 days'
    },
    {
      timestamp: '2025-12-17 14:18:30',
      agent: 'Risk Agent',
      decision: 'Composite risk score updated: 0.68. High priority maintenance recommended'
    },
    {
      timestamp: '2025-12-17 14:10:55',
      agent: 'Recommendation Agent',
      decision: 'Scheduled preventive maintenance: Oil change, filter replacement, brake inspection'
    },
    {
      timestamp: '2025-12-17 14:05:22',
      agent: 'Master Agent',
      decision: 'Initiated comprehensive vehicle health assessment workflow'
    },
    {
      timestamp: '2025-12-17 13:58:18',
      agent: 'Telemetry Agent',
      decision: 'Processed 2,847 telemetry points from last 24 hours'
    },
    {
      timestamp: '2025-12-17 13:45:10',
      agent: 'Feedback Agent',
      decision: 'Incorporated technician feedback: Battery health confirmed at 92%'
    },
    {
      timestamp: '2025-12-17 13:32:05',
      agent: 'Scheduling Agent',
      decision: 'Recommended service appointment window: 2025-12-22 to 2025-12-24'
    }
  ]

  const loadTimeline = () => {
    if (!vehicleId) {
      setError('Enter a vehicle ID to view timeline.')
      return
    }
    setLoading(true)
    setError('')
    fetchAgentTimeline(vehicleId)
      .then((res) => setTimeline(res.data || []))
      .catch(() => setError('No timeline available for this vehicle yet.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    // If user is logged in with a specific vehicle, auto-load that vehicle's timeline
    if (auth?.role === 'user' && auth?.vehicleId) {
      setVehicleId(String(auth.vehicleId))
      setLoading(true)
      setError('')
      fetchAgentTimeline(String(auth.vehicleId))
        .then((res) => setTimeline(res.data || []))
        .catch(() => setTimeline(demoTimeline))
        .finally(() => setLoading(false))
    } else {
      // Show demo data on initial load for admins
      setTimeline(demoTimeline)
    }
  }, [auth])

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Agent Timeline</h2>
          <p className="text-slate-500 text-sm">Chronological log of agent decisions</p>
        </div>
        {auth?.role !== 'user' && (
          <div className="flex items-center space-x-2">
            <input
              className="border rounded px-3 py-2 text-sm"
              placeholder="Vehicle ID"
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
            />
            <button
              onClick={loadTimeline}
              className="bg-indigo-600 text-white px-3 py-2 rounded text-sm"
              disabled={!vehicleId}
            >
              Load
            </button>
          </div>
        )}
        {auth?.role === 'user' && vehicleId && (
          <div className="text-sm text-slate-600">
            Viewing timeline for vehicle: <strong>{vehicleId}</strong>
          </div>
        )}
      </header>

      {error && <div className="p-3 bg-amber-50 text-amber-700 rounded">{error}</div>}
      {loading && <div className="text-sm text-slate-500">Loading...</div>}

      <div className="bg-white rounded shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500 bg-slate-100">
            <tr>
              <th className="px-3 py-2">Timestamp</th>
              <th className="px-3 py-2">Agent</th>
              <th className="px-3 py-2">Decision</th>
            </tr>
          </thead>
          <tbody>
            {timeline.map((a, idx) => (
              <tr key={idx} className="border-t hover:bg-slate-50">
                <td className="px-3 py-2 whitespace-nowrap text-slate-600">{a.timestamp}</td>
                <td className="px-3 py-2 font-medium text-indigo-600">{a.agent}</td>
                <td className="px-3 py-2 text-slate-700">{a.decision}</td>
              </tr>
            ))}
            {timeline.length === 0 && !loading && (
              <tr>
                <td colSpan="3" className="px-3 py-4 text-center text-slate-500">
                  No agent activity yet. Enter a vehicle ID to load real data or refresh.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AgentTimeline

