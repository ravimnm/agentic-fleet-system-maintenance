import axios from 'axios'

export async function sendBotMessage(vehicleId, message) {
  const res = await axios.post('/api/bot/chat', { vehicleId, message })
  return res.data
}
