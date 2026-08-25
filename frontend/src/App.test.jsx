import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import authReducer from './features/auth/authSlice'
import activeStoreReducer from './features/store/activeStoreSlice'
import posReducer from './features/pos/posSlice'
import App from './App'

vi.mock('./services/apiClient', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: [] }) },
  setAccessToken: vi.fn(),
  attachAuthInterceptor: vi.fn(),
  refreshAccessToken: vi.fn().mockRejectedValue({ response: { status: 401 } }),
  getCsrfToken: vi.fn(() => null),
}))

function renderApp(initialRoute) {
  const store = configureStore({
    reducer: { auth: authReducer, activeStore: activeStoreReducer, pos: posReducer },
  })
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[initialRoute]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>
  )
}

describe('App routing', () => {
  it('redirects an unauthenticated visitor from / to /login', async () => {
    renderApp('/')
    await waitFor(() => expect(screen.getByRole('heading', { name: /log in/i })).toBeInTheDocument())
  })

  it('renders the login page directly at /login', async () => {
    renderApp('/login')
    expect(await screen.findByRole('heading', { name: /log in/i })).toBeInTheDocument()
  })
})