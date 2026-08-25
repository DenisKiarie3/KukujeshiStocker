import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import ProductList from '../features/inventory/ProductList'
import { logout as logoutAction } from '../features/auth/authSlice'
import { logout as logoutRequest } from '../services/authService'

function HomePage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const user = useSelector((state) => state.auth.user)

  const handleLogout = async () => {
    try {
      await logoutRequest()
    } finally {
      dispatch(logoutAction())
      navigate('/login')
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col items-center py-12 px-4 gap-6">
      <div className="w-full max-w-md flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-700">KukujeshiStocker</h1>
          {user && <p className="text-sm text-neutral-500">Logged in as {user.username}</p>}
        </div>
        <button onClick={handleLogout} className="text-sm text-neutral-500 underline">Log out</button>
      </div>
      <ProductList />
    </div>
  )
}

export default HomePage