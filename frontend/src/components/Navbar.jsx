import React, { useContext } from 'react'
import { NavLink } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

const adminNavItems = [
  { to: '/', label: 'Fleet Dashboard' },
  { to: '/risk', label: 'Risk Analytics' },
  { to: '/agents', label: 'Agent Timeline' },
  { to: '/alerts', label: 'Alerts' },
]

const userNavItems = [
  { to: '/vehicle', label: 'Vehicle Analytics' },
  { to: '/assistance', label: 'Breakdown Assistance' },
  { to: '/alerts', label: 'Alerts' },
]

const Navbar = () => {
  try {
    const { auth, setAuth } = useContext(AuthContext)
    const navItems = auth?.role === 'admin' ? adminNavItems : userNavItems

    return (
      <aside className="w-64 bg-slate-900 text-white min-h-screen p-6 space-y-6">
        <div>
          <h1 className="text-xl font-semibold">Agentic Fleet</h1>
          <p className="text-sm text-slate-300">Predictive Maintenance</p>
        </div>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block px-3 py-2 rounded ${
                  isActive ? 'bg-indigo-500 text-white' : 'text-slate-200 hover:bg-slate-800'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-6">
          <label className="text-sm text-slate-300">Account</label>
          <div className="mt-2 text-sm text-slate-200">{auth?.role === 'admin' ? 'Admin' : `User (${auth?.vehicleId || '—'})`}</div>
          <div className="mt-2">
            <a href="/login" className="text-indigo-300 hover:underline text-sm">Switch account</a>
          </div>
        </div>
      </aside>
    )
  } catch (e) {
    console.error('Navbar error:', e)
    return null
  }
}

export default Navbar

