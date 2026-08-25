import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { setCredentials, logout } from './authSlice'
import { refreshAccessToken } from '../../services/apiClient'

/**
 * Runs once, on initial app load, to silently re-establish a session from
 * the httpOnly refresh cookie if one exists — without this, every page
 * reload would force a fresh login, even with days left on the cookie.
 */
export const useAuthInit = () => {
  const dispatch = useDispatch()

  useEffect(() => {
    let cancelled = false
    refreshAccessToken()
      .then((data) => {
        if (!cancelled) dispatch(setCredentials({ user: data.user, accessToken: data.access }))
      })
      .catch(() => {
        if (!cancelled) dispatch(logout())
      })
    return () => {
      cancelled = true
    }
  }, [dispatch])
}