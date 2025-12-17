import React, { useEffect, useState, useContext } from 'react'
import {
  fetchVehicles,
  fetchTelemetry,
  fetchPrediction,
  fetchRisk,
  postPredict,
  fetchRecommendations,
  ingestTelemetryFile,
} from '../api/api'
import { LineSeries } from '../components/Charts'
import VehicleHealthBadge from '../components/VehicleHealthBadge'
import PredictionExplanation from '../components/PredictionExplanation'
import MaintenanceRecommendations from '../components/MaintenanceRecommendations'
import { AuthContext } from '../context/AuthContext'

const VehicleAnalytics = () => {
  const { auth } = useContext(AuthContext)
  const [vehicles, setVehicles] = useState([])
  const [selected, setSelected] = useState('')
  const [telemetry, setTelemetry] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [risk, setRisk] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [csvFile, setCsvFile] = useState(null)
  const [csvError, setCsvError] = useState('')
  const [uploadStatus, setUploadStatus] = useState('')
  const [vehiclesLoading, setVehiclesLoading] = useState(true)

  useEffect(() => {
    // If user is logged in with a specific vehicle, only show that vehicle
    if (auth?.role === 'user' && auth?.vehicleId) {
      setVehicles([String(auth.vehicleId)])
      setSelected(String(auth.vehicleId))
      setVehiclesLoading(false)
    } else {
      // Admin sees all vehicles
      fetchVehicles()
        .then((res) => {
          const ids = res.data?.vehicles || []
          setVehicles(ids)
          if (ids.length > 0) setSelected(ids[0])
        })
        .catch(() => setVehicles([]))
        .finally(() => setVehiclesLoading(false))
    }
  }, [auth])

  useEffect(() => {
    if (!selected) return
    setLoading(true)
    setError('')
    Promise.all([fetchTelemetry(selected), fetchPrediction(selected), fetchRisk(selected)])
      .then(([t, p, r]) => {
        setTelemetry(t.data)
        setPrediction(p.data)
        setRisk(r.data)
        return fetchRecommendations(selected)
      })
      .then((recRes) => setRecommendations(recRes.data || []))
      .catch(() => setError('Data not available for this vehicle yet.'))
      .finally(() => setLoading(false))
  }, [selected])

  const handleReRun = async () => {
    if (!telemetry) return
    const res = await postPredict(telemetry)
    setPrediction(res.data?.prediction)
    setRisk(res.data?.risk)
    setRecommendations(res.data?.recommendations || [])
  }

  const handleCsvChange = (event) => {
    const file = event.target.files?.[0]
    setCsvFile(file || null)
    setUploadStatus('')
    if (!file) {
      setCsvError('Select a CSV file to upload.')
      return
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setCsvError('File must be a CSV.')
      return
    }
    setCsvError('')
  }

  const handleUpload = async () => {
    if (!csvFile || csvError) return
    setUploadStatus('Uploading...')
    setError('')
    try {
      const res = await ingestTelemetryFile(csvFile)
      setUploadStatus(`Uploaded ${res.data?.inserted || 0} records.`)
    } catch (err) {
      const detail = err?.response?.data?.detail
      const message = typeof detail === 'object' ? detail?.message || detail?.error : detail
      setUploadStatus('')
      setCsvError(message || 'Invalid telemetry CSV format')
    }
  }

  const telemSeries = telemetry
    ? Object.entries(telemetry)
        .filter(([k, v]) => typeof v === 'number')
        .slice(0, 5)
        .map(([k, v]) => ({ metric: k, value: v, label: telemetry.timestamp }))
    : [
        // Demo telemetry data for different vehicles
        { metric: 'Temperature', value: 87.5, label: '14:30' },
        { metric: 'Pressure', value: 32.1, label: '14:35' },
        { metric: 'RPM', value: 2150, label: '14:40' },
        { metric: 'Fuel', value: 45.3, label: '14:45' },
        { metric: 'Voltage', value: 13.8, label: '14:50' }
      ]

  const riskSeries = risk 
    ? [{ time: risk.timestamp, score: risk.risk_score || 0 }]
    : [
        // Demo risk trend data
        { time: '12:00', score: 0.25 },
        { time: '13:00', score: 0.35 },
        { time: '14:00', score: 0.52 },
        { time: '15:00', score: 0.68 }
      ]

  const predSeries = prediction 
    ? [{ time: prediction.timestamp, prob: prediction.probability || 0 }]
    : [
        // Demo prediction probability data
        { time: '12:00', prob: 0.15 },
        { time: '13:00', prob: 0.28 },
        { time: '14:00', prob: 0.52 },
        { time: '15:00', prob: 0.72 }
      ]

  const healthState =
    risk?.risk_score > 0.8
      ? 'grounded'
      : prediction?.probability > 0.75
      ? 'critical'
      : risk?.risk_score >= 0.4 || prediction?.probability > 0.5
      ? 'warning'
      : 'healthy'

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Vehicle Analytics</h2>
          <p className="text-slate-500 text-sm">Latest telemetry and predictions</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            className="border rounded px-3 py-2 disabled:opacity-50"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            disabled={vehiclesLoading}
          >
            <option value="">{vehiclesLoading ? 'Loading vehicles...' : 'Select vehicle'}</option>
            {vehicles.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
          <button
            onClick={handleReRun}
            className="bg-indigo-600 text-white px-3 py-2 rounded disabled:opacity-50"
            disabled={!telemetry}
          >
            Re-run Prediction
          </button>
        </div>
      </header>

      {error && <div className="p-3 bg-rose-50 text-rose-700 rounded">{error}</div>}
      {!vehiclesLoading && vehicles.length === 0 && (
        <div className="p-3 bg-amber-50 text-amber-700 rounded">
          No vehicles available. Please ingest telemetry data first.
        </div>
      )}
      {!selected && !vehiclesLoading && vehicles.length > 0 && (
        <div className="p-3 bg-slate-100 text-slate-600 rounded">
          Select a vehicle to view analytics.
        </div>
      )}
      {loading && <div className="text-slate-500 text-sm">Loading...</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <LineSeries data={telemSeries} xKey="label" yKey="value" title="Telemetry snapshot" />
        <LineSeries data={riskSeries} xKey="time" yKey="score" title="Risk trend" color="#f97316" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <LineSeries data={predSeries} xKey="time" yKey="prob" title="Prediction probability" color="#22c55e" />
        <div className="bg-white p-4 rounded shadow space-y-2">
          <h3 className="font-semibold">Details</h3>
          <p className="text-sm text-slate-600">
            Predicted event: <strong>{prediction?.predicted_event || 'N/A'}</strong>
          </p>
          <p className="text-sm text-slate-600">
            Probability: <strong>{prediction?.probability?.toFixed(2) || '-'}</strong>
          </p>
          <p className="text-sm text-slate-600">
            Risk category: <strong>{risk?.category || '-'}</strong>
          </p>
          <div className="flex items-center space-x-2">
            <p className="text-sm text-slate-600">Health:</p>
            <VehicleHealthBadge state={healthState} />
          </div>
          <div className="mt-3">
            <p className="text-sm font-semibold mb-1">Explanation</p>
            <PredictionExplanation explanation={prediction?.explanation} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2">Maintenance Recommendations</h3>
          <MaintenanceRecommendations recommendations={recommendations} />
        </div>
        <div className="bg-white p-4 rounded shadow space-y-3">
          <h3 className="font-semibold">Upload Telemetry CSV</h3>
          <p className="text-sm text-slate-600">
            Files are validated for required columns, null checks, and numeric ranges.
          </p>
          <input type="file" accept=".csv,text/csv" onChange={handleCsvChange} />
          {csvError && <div className="text-sm text-rose-600">{csvError}</div>}
          {uploadStatus && <div className="text-sm text-green-700">{uploadStatus}</div>}
          <button
            onClick={handleUpload}
            className="bg-slate-900 text-white px-3 py-2 rounded text-sm disabled:opacity-50"
            disabled={!csvFile || !!csvError}
          >
            Upload & Validate
          </button>
        </div>
      </div>
    </div>
  )
}

export default VehicleAnalytics

