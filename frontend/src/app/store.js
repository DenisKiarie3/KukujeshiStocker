import { configureStore } from '@reduxjs/toolkit'
import authReducer, { setCredentials, logout } from '../features/auth/authSlice'
import activeStoreReducer from '../features/store/activeStoreSlice'
import posReducer from '../features/pos/posSlice'
import storefrontCartReducer from '../features/storefrontCart/storefrontCartSlice'
import { setAccessToken, attachAuthInterceptor } from '../services/apiClient'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    activeStore: activeStoreReducer,
    pos: posReducer,
    storefrontCart: storefrontCartReducer,
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

attachAuthInterceptor({
  onRefreshSuccess: (data) => {
    store.dispatch(setCredentials({ user: data.user, accessToken: data.access }))
  },
  onRefreshFailure: () => {
    store.dispatch(logout())
  },
})