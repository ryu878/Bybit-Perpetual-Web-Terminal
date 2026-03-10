import { Routes, Route, Navigate } from 'react-router-dom'
import TerminalPage from './pages/TerminalPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/BTCUSDT" replace />} />
      <Route path="/:symbol" element={<TerminalPage />} />
      <Route path="*" element={<Navigate to="/BTCUSDT" replace />} />
    </Routes>
  )
}

export default App
