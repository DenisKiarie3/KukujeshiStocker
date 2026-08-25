import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import authReducer from './authSlice'
import ProtectedRoute from './ProtectedRoute'

function renderWithAuthState(authState) {
  const store = configureStore({ reducer: { auth: authReducer }, preloadedState: { auth: authState } })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/login" element={<p>Login page</p>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<p>Protected content</p>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </Provider>
  )
}

describe('ProtectedRoute', () => {
  it('shows a checking-session message before auth is initialized', () => {
    renderWithAuthState({ user: null, accessToken: null, isInitialized: false })
    expect(screen.getByText(/checking session/i)).toBeInTheDocument()
  })

  it('redirects to /login when initialized but not authenticated', () => {
    renderWithAuthState({ user: null, accessToken: null, isInitialized: true })
    expect(screen.getByText(/login page/i)).toBeInTheDocument()
  })

  it('renders the protected content when authenticated', () => {
    renderWithAuthState({ user: { username: 'test' }, accessToken: 'abc123', isInitialized: true })
    expect(screen.getByText(/protected content/i)).toBeInTheDocument()
  })
})