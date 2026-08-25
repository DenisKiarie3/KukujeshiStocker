import { createSlice } from '@reduxjs/toolkit'

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    accessToken: null,
    // Becomes true once the app's initial silent-refresh attempt (see
    // useAuthInit) has resolved, either way — ProtectedRoute waits on
    // this so it doesn't redirect to /login before that check finishes.
    isInitialized: false,
  },
  reducers: {
    setCredentials: (state, action) => {
      state.user = action.payload.user
      state.accessToken = action.payload.accessToken
      state.isInitialized = true
    },
    logout: (state) => {
      state.user = null
      state.accessToken = null
      state.isInitialized = true
    },
  },
})

export const { setCredentials, logout } = authSlice.actions
export default authSlice.reducer