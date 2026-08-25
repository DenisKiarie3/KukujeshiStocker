import { describe, it, expect } from 'vitest'
import authReducer, { setCredentials, logout } from './authSlice'

describe('authSlice', () => {
  const initialState = { user: null, accessToken: null, isInitialized: false }

  it('returns the initial state', () => {
    expect(authReducer(undefined, { type: 'unknown' })).toEqual(initialState)
  })

  it('sets credentials on login and marks auth as initialized', () => {
    const action = setCredentials({ user: { id: 1, username: 'owner1' }, accessToken: 'abc123' })
    const state = authReducer(initialState, action)
    expect(state.user.username).toBe('owner1')
    expect(state.accessToken).toBe('abc123')
    expect(state.isInitialized).toBe(true)
  })

  it('clears credentials on logout but keeps isInitialized true', () => {
    const loggedIn = { user: { id: 1, username: 'owner1' }, accessToken: 'abc123', isInitialized: true }
    const state = authReducer(loggedIn, logout())
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
    expect(state.isInitialized).toBe(true)
  })
})