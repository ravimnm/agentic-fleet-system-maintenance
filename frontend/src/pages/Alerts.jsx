import React, { useEffect, useState } from 'react'
import { fetchAlerts } from '../api/api'
import VehicleHealthBadge from '../components/VehicleHealthBadge'

const Alerts = () => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
      .then((res) => setAlerts(res.data || []))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold">Alerts Feed</h2>
        <p className="text-slate-500 text-sm">Hybrid rule-triggered alerts</p>
      </header>

      {loading && <div className="text-sm text-slate-500">Loading...</div>}

      <div className="bg-white rounded shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500 bg-slate-100">
            <tr>
              <th className="px-3 py-2">Time</th>
              <th className="px-3 py-2">Vehicle</th>
              <th className="px-3 py-2">Rule</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">Details</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-3 py-2 whitespace-nowrap">{a.timestamp}</td>
                <td className="px-3 py-2">{a.vehicleId}</td>
                <td className="px-3 py-2">{a.rule}</td>
                <td className="px-3 py-2">
                  <VehicleHealthBadge state={a.severity === 'high' ? 'critical' : 'warning'} />
                </td>
                <td className="px-3 py-2 text-slate-700">{a.details}</td>
              </tr>
            ))}
            {alerts.length === 0 && !loading && (
              <tr>
                <td colSpan="5" className="px-3 py-4 text-center text-slate-500">
                  No alerts yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Alerts

