import { Routes, Route } from 'react-router-dom'
import { useAuthInit } from './features/auth/useAuthInit'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CheckoutCallbackPage from './pages/CheckoutCallbackPage'
import StorefrontCatalogPage from './pages/StorefrontCatalogPage'
import StorefrontCheckoutPage from './pages/StorefrontCheckoutPage'
import StorefrontCheckoutCallbackPage from './pages/StorefrontCheckoutCallbackPage'
import OrderStatusLookupPage from './pages/OrderStatusLookupPage'
import ProtectedRoute from './features/auth/ProtectedRoute'

function App() {
  useAuthInit()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/store/:slug" element={<StorefrontCatalogPage />} />
      <Route path="/store/:slug/checkout" element={<StorefrontCheckoutPage />} />
      <Route path="/store/:slug/checkout/callback" element={<StorefrontCheckoutCallbackPage />} />
      <Route path="/order-status" element={<OrderStatusLookupPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/checkout/callback" element={<CheckoutCallbackPage />} />
      </Route>
    </Routes>
  )
}

export default App