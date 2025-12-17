import React from 'react'

const PredictionExplanation = ({ explanation = [] }) => {
  // Handle different explanation formats
  let items = []
  
  if (!explanation) {
    return <p className="text-sm text-slate-500">No explanation available.</p>
  }
  
  // If it's a string, just display it
  if (typeof explanation === 'string') {
    return <p className="text-sm text-slate-600">{explanation}</p>
  }
  
  // If it's an array, use it as-is
  if (Array.isArray(explanation)) {
    items = explanation
  }
  
  // If it's an object, try to extract values
  if (typeof explanation === 'object' && !Array.isArray(explanation)) {
    items = Object.entries(explanation).map(([key, value]) => ({
      feature: key,
      impact: typeof value === 'number' ? value : 0.5,
    }))
  }
  
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No explanation available.</p>
  }

  return (
    <div className="space-y-2">
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center space-x-3">
          <div className="w-32 text-sm text-slate-700">{item.feature || `Item ${idx}`}</div>
          <div className="flex-1 bg-slate-100 rounded h-2 overflow-hidden">
            <div
              className="h-2 bg-indigo-500"
              style={{ width: `${Math.min((item.impact || 0.5) * 100, 100)}%` }}
            />
          </div>
          <div className="text-xs text-slate-600">{(item.impact || 0).toFixed(2)}</div>
        </div>
      ))}
    </div>
  )
}

export default PredictionExplanation


