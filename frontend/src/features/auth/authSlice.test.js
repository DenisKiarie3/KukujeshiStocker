import { describe, it, expect } from 'vitest'
import authReducer, { setCredentials, logout } from './authSlice'

describe('authSlice', () => {
  const initialState = { user: null, accessToken: null }

  it('returns the initial state', () => {
    expect(authReducer(undefined, { type: 'unknown' })).toEqual(initialState)
  })

  it('sets credentials on login', () => {
    const action = setCredentials({ user: { id: 1, username: 'owner1' }, accessToken: 'abc123' })
    const state = authReducer(initialState, action)
    expect(state.user.username).toBe('owner1')
    expect(state.accessToken).toBe('abc123')
  })

  it('clears credentials on logout', () => {
    const loggedIn = { user: { id: 1, username: 'owner1' }, accessToken: 'abc123' }
    const state = authReducer(loggedIn, logout())
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
  })
})