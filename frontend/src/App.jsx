import { Routes, Route } from 'react-router-dom'
import { useAuthInit } from './features/auth/useAuthInit'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CheckoutCallbackPage from './pages/CheckoutCallbackPage'
import ProtectedRoute from './features/auth/ProtectedRoute'

function App() {
  useAuthInit()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/checkout/callback" element={<CheckoutCallbackPage />} />
      </Route>
    </Routes>
  )
}

export default App