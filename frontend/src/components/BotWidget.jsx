import React, { useState, useContext, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AuthContext } from '../context/AuthContext'
import { sendBotMessage } from '../api/bot'
import axios from 'axios'

const BotWidget = () => {
  const { auth } = useContext(AuthContext)
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [breakdownModal, setBreakdownModal] = useState(null)
  const ref = useRef(null)

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [messages, open])

  // NOTE: removed automatic breakdown popup to avoid unexpected call prompts.

  const push = (m) => setMessages((s) => [...s.slice(-9), m])

  const send = async () => {
    if (!input.trim()) return
    push({ from: 'user', text: input })
    setInput('')
    setTyping(true)
    try {
      const vid = auth?.vehicleId || 0
      const res = await sendBotMessage(vid, input)
      push({ from: 'bot', text: res.answer })
    } catch (e) {
      push({ from: 'bot', text: 'Assistant unavailable.' })
    } finally {
      setTyping(false)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* breakdown modal removed to prevent automatic call popups */}
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} className="w-80 h-96 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
            <div className="p-3 bg-indigo-600 text-white font-semibold">Fleet Assistant</div>
            {/* suggested queries */}
            <div className="p-2 border-b">
              <div className="text-xs text-slate-600 mb-1">Try a quick question:</div>
              <div className="flex gap-2 flex-wrap">
                {[
                  'Health of my vehicle',
                  'Vehicle details',
                  'Last prediction',
                  'Recommendations',
                ].map((s) => (
                  <button key={s} onClick={() => { setInput(s); }} className="text-xs px-2 py-1 bg-gray-100 rounded">{s}</button>
                ))}
              </div>
            </div>

            <div ref={ref} className="flex-1 p-3 overflow-auto space-y-2">
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
              <button onClick={() => { if (input.trim()) send() }} className="px-3 py-2 bg-indigo-600 text-white rounded">Send</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button onClick={() => setOpen((o) => !o)} className="w-14 h-14 rounded-full bg-indigo-600 text-white shadow-lg flex items-center justify-center" aria-label="Assistant">🤖</button>
    </div>
  )
}

export default BotWidget
