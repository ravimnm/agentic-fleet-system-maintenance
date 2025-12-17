import React from 'react'
import FloatingAssistant from '../components/FloatingAssistant'

const UserLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 flex">
      {children}
      <FloatingAssistant />
    </div>
  )
}

export default UserLayout
