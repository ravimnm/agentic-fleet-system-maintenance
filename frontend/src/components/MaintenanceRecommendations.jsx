import React from 'react'

const badgeColor = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
}

const MaintenanceRecommendations = ({ recommendations = [] }) => {
  // Handle if recommendations is not an array
  let items = []
  
  if (!recommendations) {
    return <p className="text-sm text-slate-500">No recommendations yet.</p>
  }
  
  if (Array.isArray(recommendations)) {
    items = recommendations
  } else if (typeof recommendations === 'object') {
    // Convert object to array
    items = Object.entries(recommendations).map(([key, value]) => ({
      component: key,
      severity: 'medium',
      recommendation: typeof value === 'string' ? value : JSON.stringify(value),
    }))
  }
  
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No recommendations yet.</p>
  }

  return (
    <div className="space-y-3">
      {items.map((rec, idx) => (
        <div key={idx} className="p-3 border rounded">
          <div className="flex items-center justify-between mb-1">
            <p className="font-semibold capitalize">{rec.component || `Recommendation ${idx}`}</p>
            <span
              className={`text-xs px-2 py-1 rounded ${badgeColor[rec.severity] || 'bg-slate-100 text-slate-700'}`}
            >
              {rec.severity || 'info'}
            </span>
          </div>
          <p className="text-sm text-slate-700">{rec.recommendation || 'See details'}</p>
        </div>
      ))}
    </div>
  )
}

export default MaintenanceRecommendations


