import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { setCredentials } from '../features/auth/authSlice'
import { register } from '../services/authService'

function RegisterPage() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const data = await register({ username, email, password })
      dispatch(setCredentials({ user: data.user, accessToken: data.access }))
      navigate('/')
    } catch (err) {
      const detail = err?.response?.data
      setError(typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Registration failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-700 text-center">Create account</h1>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-neutral-700">Username</label>
          <input id="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} required
            className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-neutral-700">Email</label>
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-neutral-700">Password</label>
          <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
            className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <button type="submit" disabled={isSubmitting}
          className="w-full rounded-md bg-brand-700 py-2 text-white font-medium disabled:opacity-50">
          {isSubmitting ? 'Creating account…' : 'Create account'}
        </button>
        <p className="text-sm text-center text-neutral-500">
          Already have an account? <Link to="/login" className="text-brand-700 underline">Log in</Link>
        </p>
      </form>
    </div>
  )
}

export default RegisterPage