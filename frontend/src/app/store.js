import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import activeStoreReducer from '../features/store/activeStoreSlice'
import posReducer from '../features/pos/posSlice'
import { setAccessToken } from '../services/apiClient'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    activeStore: activeStoreReducer,
    pos: posReducer,
  },
})

// Keep apiClient's Authorization header in sync with Redux's in-memory
// token, without services/apiClient.js needing to import the store
// directly — that would create a circular import (store -> apiClient ->
// store). Subscribing here, in the one place that already imports both,
// avoids that entirely.
let previousToken = store.getState().auth.accessToken
store.subscribe(() => {
  const currentToken = store.getState().auth.accessToken
  if (currentToken !== previousToken) {
    previousToken = currentToken
    setAccessToken(currentToken)
  }
})