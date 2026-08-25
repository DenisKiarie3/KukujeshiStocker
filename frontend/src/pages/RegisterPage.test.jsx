import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import authReducer from '../features/auth/authSlice'
import RegisterPage from './RegisterPage'
import * as authService from '../services/authService'

vi.mock('../services/authService')

function renderRegisterPage() {
  const store = configureStore({ reducer: { auth: authReducer } })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/register']}>
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<p>Home page</p>} />
        </Routes>
      </MemoryRouter>
    </Provider>
  )
}

describe('RegisterPage', () => {
  it('registers successfully and navigates to /', async () => {
    authService.register.mockResolvedValueOnce({ user: { username: 'newuser' }, access: 'tok456' })
    renderRegisterPage()

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'newuser' } })
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'new@example.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'StrongPass123!' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => expect(screen.getByText(/home page/i)).toBeInTheDocument())
  })
})