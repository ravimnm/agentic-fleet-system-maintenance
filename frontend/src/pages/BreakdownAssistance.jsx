import React, { useContext, useEffect, useState } from 'react'
import axios from 'axios'
import { AuthContext } from '../context/AuthContext'
import { motion } from 'framer-motion'

const BreakdownAssistance = () => {
  const { auth: user } = useContext(AuthContext)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetch = async () => {
      if (!user || !user.vehicleId) return
      setLoading(true)
      setError(null)
      try {
        // Try compatibility endpoint first, then assistant endpoint
        const endpoints = [
          `/api/assist/breakdown/${user.vehicleId}`,
          `/api/assistant/assistance/${user.vehicleId}`,
        ]
        let res = null
        for (const ep of endpoints) {
          try {
            res = await axios.get(ep)
            if (res && res.data) break
          } catch (err) {
            // continue to next endpoint
            console.warn('assist fetch failed for', ep, err?.message || err)
          }
        }
        if (!res || !res.data) throw new Error('No assistant response')

        // Normalize response shapes to { breakdown: bool, service_centers: [] }
        const body = res.data
        const normalized = { breakdown: false, service_centers: [] }
        if (typeof body.breakdown === 'boolean') {
          normalized.breakdown = body.breakdown
        } else if (body.message && body.message.toLowerCase().includes('breakdown')) {
          normalized.breakdown = true
        }
        if (Array.isArray(body.service_centers)) {
          normalized.service_centers = body.service_centers
        } else {
          // support nearest_open_center / best_rated_center
          const list = []
          if (body.nearest_open_center) list.push(body.nearest_open_center)
          if (body.best_rated_center) list.push(body.best_rated_center)
          if (body.service_centers && typeof body.service_centers === 'object') {
            // some shapes might embed centers differently
            normalized.service_centers = Object.values(body.service_centers)
          } else if (list.length > 0) {
            normalized.service_centers = list
          }
        }
        setData(normalized)
      } catch (e) {
        console.error('Failed to fetch assistance:', e)
        setError('Assistance data unavailable')
        setData(null)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [user])

  if (!user || user.role !== 'user') {
    return <div className="p-6 text-slate-600">This page is for vehicle users only.</div>
  }

  if (loading) return <div className="p-6 text-slate-600">Loading assistance...</div>

  if (error) return <div className="p-6 text-red-600">{error}</div>

  if (!data?.breakdown) {
    return (
      <div className="p-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-green-900">✓ Vehicle Status Normal</h2>
          <p className="text-green-700 mt-2">Your vehicle is operating within safe parameters.</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 8 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="p-6 space-y-6"
    >
      <div className="bg-red-50 border-l-4 border-red-600 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-red-900">🚨 Breakdown Detected</h2>
        <p className="text-red-700 mt-2">Your vehicle requires immediate assistance. Below are nearby service centers.</p>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Available Service Centers (best rated first)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {((data && data.service_centers) || []).map((c, idx) => (
            <motion.div key={c._id || idx} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * idx }} className={`bg-white rounded-lg shadow-md p-4 border ${idx === 0 ? 'border-amber-400' : 'border-gray-100'}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-800">{c.name}</p>
                  <p className="text-sm text-gray-600">{c.address || ''}</p>
                </div>
                {idx === 0 && <div className="text-sm font-semibold text-amber-700">⭐ Best</div>}
              </div>
              <div className="mt-3 text-sm text-gray-600 space-y-1">
                <p><span className="font-semibold">Distance:</span> {(c.distance_km || 0).toFixed(1)} km</p>
                <p><span className="font-semibold">Rating:</span> ⭐ {c.rating || 'N/A'}</p>
                {c.phone && <p><span className="font-semibold">Phone:</span> {c.phone}</p>}
              </div>
              <div className="mt-3 flex gap-2">
                <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(c.latitude + ',' + c.longitude)}`} target="_blank" rel="noreferrer" className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-center">🗺️ Navigate</a>
                <button onClick={() => { navigator.clipboard && c.phone && navigator.clipboard.writeText(c.phone) }} className="px-3 py-2 bg-gray-200 text-gray-800 rounded">Copy Phone</button>
              </div>
            </motion.div>
          ))}
          {(!data?.service_centers || data.service_centers.length === 0) && (
            <div className="p-4 text-sm text-gray-600">No open service centers found nearby.</div>
          )}
        </div>
      </div>

      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          💡 <span className="font-semibold">Tip:</span> Ask the AI assistant (bottom right) for more information about your vehicle's condition.
        </p>
      </div>
    </motion.div>
  )
}

export default BreakdownAssistance
