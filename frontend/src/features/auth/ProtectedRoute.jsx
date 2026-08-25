import { useSelector } from 'react-redux'
import { Navigate, Outlet } from 'react-router-dom'

function ProtectedRoute() {
  const { accessToken, isInitialized } = useSelector((state) => state.auth)

  if (!isInitialized) {
    return <p className="text-center mt-12 text-neutral-500">Checking session…</p>
  }

  if (!accessToken) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default ProtectedRoute