import React, { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

const Login = () => {
  const { setAuth } = useContext(AuthContext)
  const [role, setRole] = useState('admin')
  const [vehicleId, setVehicleId] = useState('')
  const navigate = useNavigate()

  const submit = (e) => {
    e.preventDefault()
    const payload = { role, vehicleId: role === 'user' && vehicleId ? parseInt(vehicleId, 10) : null }
    setAuth(payload)
    if (role === 'admin') navigate('/')
    else navigate('/vehicle')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="w-full max-w-md bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Mock Login</h2>
        <div className="mb-4">
          <label className="block text-sm">Role</label>
          <select value={role} onChange={(e) => setRole(e.target.value)} className="w-full p-2 border rounded">
            <option value="admin">Admin</option>
            <option value="user">User</option>
          </select>
        </div>

        {role === 'user' && (
          <div className="mb-4">
            <label className="block text-sm">Vehicle ID</label>
            <input value={vehicleId} onChange={(e) => setVehicleId(e.target.value)} className="w-full p-2 border rounded" />
          </div>
        )}

        <div className="flex justify-end">
          <button className="px-4 py-2 bg-indigo-600 text-white rounded">Login</button>
        </div>
      </form>
    </div>
  )
}

export default Login
