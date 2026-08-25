import { configureStore } from '@reduxjs/toolkit'
import authReducer, { setCredentials, logout } from '../features/auth/authSlice'
import activeStoreReducer from '../features/store/activeStoreSlice'
import posReducer from '../features/pos/posSlice'
import { setAccessToken, attachAuthInterceptor } from '../services/apiClient'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    activeStore: activeStoreReducer,
    pos: posReducer,
  },
})

let previousToken = store.getState().auth.accessToken
store.subscribe(() => {
  const currentToken = store.getState().auth.accessToken
  if (currentToken !== previousToken) {
    previousToken = currentToken
    setAccessToken(currentToken)
  }
})

// Keeps a session alive across an expired access token mid-session,
// as long as the httpOnly refresh cookie is still valid.
attachAuthInterceptor({
  onRefreshSuccess: (data) => {
    store.dispatch(setCredentials({ user: data.user, accessToken: data.access }))
  },
  onRefreshFailure: () => {
    store.dispatch(logout())
  },
})