import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import authReducer from '../features/auth/authSlice'
import LoginPage from './LoginPage'
import * as authService from '../services/authService'

vi.mock('../services/authService')

function renderLoginPage() {
  const store = configureStore({ reducer: { auth: authReducer } })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<p>Home page</p>} />
        </Routes>
      </MemoryRouter>
    </Provider>
  )
}

describe('LoginPage', () => {
  beforeEach(() => vi.resetAllMocks())

  it('logs in successfully and navigates to /', async () => {
    authService.login.mockResolvedValueOnce({ user: { username: 'denis' }, access: 'tok123' })
    renderLoginPage()

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'denis' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass123' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText(/home page/i)).toBeInTheDocument())
  })

  it('shows an error message on failed login', async () => {
    authService.login.mockRejectedValueOnce({ response: { data: { detail: 'Invalid credentials.' } } })
    renderLoginPage()

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'denis' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument())
  })
})