import React, { createContext, useState } from 'react'

export const UserContext = createContext({ user: null, setUser: () => {} })

export const UserProvider = ({ children }) => {
  // default to admin for ease of demo; frontend mock login will switch
  const [user, setUser] = useState({ userId: 'admin_1', role: 'admin', vehicleId: null })

  return (
    <UserContext.Provider value={{ user, setUser }}>{children}</UserContext.Provider>
  )
}

export default UserProvider
