import React from 'react'
import { motion } from 'framer-motion'

const colorMap = {
  healthy: 'bg-green-100 text-green-700 border-green-200',
  warning: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  critical: 'bg-red-100 text-red-700 border-red-200',
  grounded: 'bg-black text-white border-slate-800',
}

const labelMap = {
  healthy: 'Healthy',
  warning: 'Warning',
  critical: 'Critical',
  grounded: 'Grounded',
}

const VehicleHealthBadge = ({ state = 'healthy' }) => {
  const color = colorMap[state] || colorMap.healthy
  const label = labelMap[state] || labelMap.healthy
  const isCritical = state === 'critical'

  return (
    <motion.span 
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold border ${color}`}
      animate={isCritical ? { scale: [1, 1.05, 1] } : {}}
      transition={isCritical ? { duration: 2, repeat: Infinity } : {}}
    >
      {label}
    </motion.span>
  )
}

export default VehicleHealthBadge

