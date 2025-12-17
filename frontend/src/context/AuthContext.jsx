import React, { createContext, useState, useEffect } from 'react'

export const AuthContext = createContext({ auth: null, setAuth: () => {} })

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(() => {
    try {
      const raw = localStorage.getItem('auth')
      return raw ? JSON.parse(raw) : { role: 'admin', vehicleId: null }
    } catch {
      return { role: 'admin', vehicleId: null }
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem('auth', JSON.stringify(auth))
    } catch {}
  }, [auth])

  return <AuthContext.Provider value={{ auth, setAuth }}>{children}</AuthContext.Provider>
}

export default AuthProvider
