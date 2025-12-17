import React, { useContext } from 'react'
import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Navbar from './components/Navbar'
import ErrorBoundary from './components/ErrorBoundary'
import FleetDashboard from './pages/FleetDashboard'
import VehicleAnalytics from './pages/VehicleAnalytics'
import RiskAnalytics from './pages/RiskAnalytics'
import AgentTimeline from './pages/AgentTimeline'
import Alerts from './pages/Alerts'
import BreakdownAssistance from './pages/BreakdownAssistance'
import AdminLayout from './layouts/AdminLayout'
import UserLayout from './layouts/UserLayout'
import { AuthProvider, AuthContext } from './context/AuthContext'
import Login from './pages/Login'
import BotWidget from './components/BotWidget'

const PageWrapper = ({ children }) => {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <motion.div key={location.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

const RequireRole = ({ role, children }) => {
  const { auth } = useContext(AuthContext)
  
  // Check if we're on login page - allow all
  if (role === 'login') return children
  
  // If not authenticated, redirect to login
  if (!auth) return <Navigate to="/login" replace />
  
  // If no role set, go to login
  if (!auth.role) return <Navigate to="/login" replace />
  
  // Allow any authenticated user
  if (role === 'any') return children

  // Check specific role -> redirect to login on mismatch
  if (role === 'admin' && auth.role !== 'admin') return <Navigate to="/login" replace />
  if (role === 'user' && auth.role !== 'user') return <Navigate to="/login" replace />
  
  return children
}

function AppInner() {
  const { auth } = useContext(AuthContext)
  const isAuthenticated = auth?.role

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 flex">
      {isAuthenticated && <Navbar />}
      <main className={isAuthenticated ? 'flex-1 p-6 overflow-auto' : 'w-full'}>
        <PageWrapper>
          <Routes>
            <Route path="/login" element={<RequireRole role="login"><Login /></RequireRole>} />
            <Route path="/" element={<RequireRole role="admin"><AdminLayout><FleetDashboard /></AdminLayout></RequireRole>} />
            <Route path="/vehicle" element={<RequireRole role="any"><UserLayout><VehicleAnalytics /></UserLayout></RequireRole>} />
            <Route path="/risk" element={<RequireRole role="admin"><AdminLayout><RiskAnalytics /></AdminLayout></RequireRole>} />
            <Route path="/agents" element={<RequireRole role="admin"><AdminLayout><AgentTimeline /></AdminLayout></RequireRole>} />
            <Route
              path="/alerts"
              element={
                <RequireRole role="any">
                  {auth?.role === 'admin' ? (
                    <AdminLayout><Alerts /></AdminLayout>
                  ) : (
                    <UserLayout><Alerts /></UserLayout>
                  )}
                </RequireRole>
              }
            />
            <Route path="/assistance" element={<RequireRole role="user"><UserLayout><BreakdownAssistance /></UserLayout></RequireRole>} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </PageWrapper>
      </main>
      {isAuthenticated && <BotWidget />}
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppInner />
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App

