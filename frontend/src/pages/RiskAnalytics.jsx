import React, { useEffect, useState } from 'react'
import { fetchTopRisk } from '../api/api'
import { BarSeries, LineSeries } from '../components/Charts'

const RiskAnalytics = () => {
  const [topRisk, setTopRisk] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTopRisk()
      .then((res) => setTopRisk(res.data || []))
      .catch(() => setTopRisk([]))
      .finally(() => setLoading(false))
  }, [])

  const eventCounts = topRisk.slice(0, 3).map((item, idx) => ({
    label: item.vehicleId || `Vehicle-${idx}`,
    count: item.risk_score ? Math.round(item.risk_score * 10) : 0,
  }))

  const timeline = topRisk.map((item, idx) => ({
    time: item.timestamp || `T${idx}`,
    score: item.risk_score || 0,
  }))

  if (loading) {
    return (
      <div className="space-y-4">
        <header>
          <h2 className="text-2xl font-semibold">Risk Analytics</h2>
          <p className="text-slate-500 text-sm">
            Breakdown of harsh events and temporal risk progression
          </p>
        </header>
        <div className="text-slate-500 text-sm">Loading...</div>
      </div>
    )
  }

  if (topRisk.length === 0) {
    return (
      <div className="space-y-4">
        <header>
          <h2 className="text-2xl font-semibold">Risk Analytics</h2>
          <p className="text-slate-500 text-sm">
            Breakdown of harsh events and temporal risk progression
          </p>
        </header>
        <div className="p-3 bg-amber-50 text-amber-700 rounded">
          No risk data available yet. Please run predictions on vehicle telemetry.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold">Risk Analytics</h2>
        <p className="text-slate-500 text-sm">
          Breakdown of harsh events and temporal risk progression
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BarSeries data={eventCounts} xKey="label" yKey="count" title="Event intensity" />
        <LineSeries data={timeline} xKey="time" yKey="score" title="Risk timeline" color="#f59e0b" />
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-3">High-risk vehicles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {topRisk.map((item, idx) => (
            <div key={idx} className="p-3 border rounded">
              <p className="font-semibold">{item.vehicleId}</p>
              <p className="text-sm text-slate-600">Risk score: {(item.risk_score || 0).toFixed(2)}</p>
              <p className="text-sm text-slate-600 capitalize">Category: {item.category}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RiskAnalytics

