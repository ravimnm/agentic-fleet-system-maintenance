import React, { useEffect, useState, useContext } from 'react'
import { fetchFleetOverview, fetchTopRisk } from '../api/api'
import { BarSeries } from '../components/Charts'
import VehicleHealthBadge from '../components/VehicleHealthBadge'
import { AuthContext } from '../context/AuthContext'

const FleetDashboard = () => {
  const { auth } = useContext(AuthContext)
  const [overview, setOverview] = useState(null)
  const [topRisk, setTopRisk] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Non-admin users cannot access fleet dashboard
    if (auth?.role === 'user') {
      setLoading(false)
      return
    }

    const load = async () => {
      try {
        const [ov, tr] = await Promise.all([
          fetchFleetOverview().catch(() => ({ data: null })),
          fetchTopRisk().catch(() => ({ data: [] }))
        ])
        setOverview(ov.data)
        setTopRisk(tr.data || [])
      } catch (e) {
        console.error('Fleet dashboard error:', e)
        setOverview(null)
        setTopRisk([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [auth])

  const distribution = topRisk.map((item, idx) => ({
    name: item.vehicleId || `VH-${idx}`,
    score: item.risk_score || 0,
  }))

  if (auth?.role === 'user') {
    return (
      <div className="space-y-4">
        <div className="p-4 bg-amber-50 text-amber-700 rounded">
          Fleet Dashboard is only available to administrators.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Fleet Dashboard</h2>
          <p className="text-slate-500 text-sm">Health snapshot across the fleet</p>
        </div>
        {loading && <span className="text-sm text-slate-500">Loading...</span>}
      </div>

      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard title="Total vehicles" value={overview.totalVehicles} />
          <MetricCard title="High risk" value={overview.highRisk} variant="warn" />
          <MetricCard
            title="Avg failure probability"
            value={overview.avgFailureProbability?.toFixed(2)}
            variant="info"
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BarSeries data={distribution} xKey="name" yKey="score" title="Risk score histogram" />
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2">Top risky vehicles</h3>
          <div className="max-h-72 overflow-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-slate-500">
                <tr>
                  <th className="pb-2">Vehicle</th>
                  <th className="pb-2">Risk</th>
                  <th className="pb-2">Category</th>
                  <th className="pb-2">Health</th>
                </tr>
              </thead>
              <tbody>
                {topRisk.map((item, idx) => (
                  <tr key={idx} className="border-t">
                    <td className="py-2">{item.vehicleId}</td>
                    <td className="py-2">{(item.risk_score || 0).toFixed(2)}</td>
                    <td className="py-2 capitalize">{item.category}</td>
                    <td className="py-2">
                      <VehicleHealthBadge
                        state={
                          item.category === 'high'
                            ? 'critical'
                            : item.category === 'medium'
                            ? 'warning'
                            : 'healthy'
                        }
                      />
                    </td>
                  </tr>
                ))}
                {topRisk.length === 0 && (
                  <tr>
                    <td colSpan="4" className="py-3 text-center text-slate-500">
                      No risk data yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

const MetricCard = ({ title, value, variant = 'default' }) => {
  const colors = {
    default: 'bg-slate-100 text-slate-800',
    warn: 'bg-rose-100 text-rose-700',
    info: 'bg-indigo-100 text-indigo-700',
  }
  return (
    <div className={`p-4 rounded shadow-sm ${colors[variant]}`}>
      <p className="text-sm">{title}</p>
      <p className="text-2xl font-semibold">{value ?? '-'}</p>
    </div>
  )
}

export default FleetDashboard

