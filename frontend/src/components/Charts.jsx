import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  ResponsiveContainer,
} from 'recharts'

export const LineSeries = ({ data, xKey, yKey, color = '#6366f1', title }) => {
  // Use provided data or generate demo data with variation
  const displayData = data && data.length > 0 ? data : generateDemoLineData(title)

  return (
    <div className="bg-white p-4 rounded shadow">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold">{title}</h3>
        <span className="text-xs text-slate-500">{displayData?.length || 0} pts</span>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={displayData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export const BarSeries = ({ data, xKey, yKey, color = '#22c55e', title }) => {
  // Use provided data or generate demo data
  const displayData = data && data.length > 0 ? data : generateDemoBarData()

  return (
    <div className="bg-white p-4 rounded shadow">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold">{title}</h3>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={displayData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey={yKey} fill={color} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Helper functions to generate varied demo data
function generateDemoLineData(title) {
  const baseValue = Math.random() * 100
  const trend = Math.random() > 0.5 ? 1 : -1
  const volatility = Math.random() * 20

  return [
    { label: '12:00', time: '12:00', value: baseValue, score: baseValue * 0.01, prob: baseValue * 0.01 },
    { label: '13:00', time: '13:00', value: baseValue + trend * 15 + (Math.random() - 0.5) * volatility, score: (baseValue + trend * 15) * 0.01, prob: (baseValue + trend * 15) * 0.01 },
    { label: '14:00', time: '14:00', value: baseValue + trend * 30 + (Math.random() - 0.5) * volatility, score: (baseValue + trend * 30) * 0.01, prob: (baseValue + trend * 30) * 0.01 },
    { label: '15:00', time: '15:00', value: baseValue + trend * 45 + (Math.random() - 0.5) * volatility, score: (baseValue + trend * 45) * 0.01, prob: (baseValue + trend * 45) * 0.01 },
    { label: '16:00', time: '16:00', value: baseValue + trend * 50 + (Math.random() - 0.5) * volatility, score: (baseValue + trend * 50) * 0.01, prob: (baseValue + trend * 50) * 0.01 },
  ]
}

function generateDemoBarData() {
  const vehicles = ['VH-001', 'VH-002', 'VH-003', 'VH-004', 'VH-005']
  return vehicles.map((name) => ({
    name,
    score: Math.random() * 100,
  }))
}

