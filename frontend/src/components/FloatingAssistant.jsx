import React, { useState, useContext, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { UserContext } from '../context/UserContext'

const FloatingAssistant = () => {
  const { user } = useContext(UserContext)
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const messagesRef = useRef(null)

  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight
  }, [messages, open])

  const pushMessage = (m) => setMessages((s) => [...s.slice(-9), m])

  const send = async () => {
    if (!input.trim()) return
    const userMsg = { from: 'user', text: input }
    pushMessage(userMsg)
    setInput('')
    setTyping(true)

    try {
      const res = await axios.post('/api/assistant/chat', { vehicleId: user.vehicleId || 0, question: input })
      const answer = res.data?.answer || 'No answer available.'
      pushMessage({ from: 'bot', text: answer })
    } catch (e) {
      pushMessage({ from: 'bot', text: 'Assistant unavailable.' })
    } finally {
      setTyping(false)
    }
  }

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="w-80 h-96 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col"
            >
              <div className="p-3 bg-indigo-600 text-white font-semibold">Fleet Assistant</div>
              <div ref={messagesRef} className="flex-1 p-3 overflow-auto space-y-2">
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.from === 'bot' ? 'justify-start' : 'justify-end'}`}>
                    <div className={`${m.from === 'bot' ? 'bg-gray-100 text-slate-900' : 'bg-indigo-500 text-white'} rounded-lg px-3 py-2 max-w-[80%]`}>
                      {m.text}
                    </div>
                  </div>
                ))}
                {typing && <div className="text-sm text-slate-500">Assistant is typing…</div>}
              </div>
              <div className="p-2 border-t flex gap-2">
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about this vehicle..." className="flex-1 px-3 py-2 rounded border" />
                <button onClick={send} className="px-3 py-2 bg-indigo-600 text-white rounded">Send</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={() => setOpen((o) => !o)}
          className="w-14 h-14 rounded-full bg-indigo-600 text-white shadow-lg flex items-center justify-center"
          aria-label="Assistant"
        >
          🤖
        </button>
      </div>
    </>
  )
}

export default FloatingAssistant
