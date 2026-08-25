import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import App from './App'

vi.mock('./services/apiClient', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: [] }) },
}))

function renderApp(initialRoute) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('App routing', () => {
  it('renders the home page at /', () => {
    renderApp('/')
    expect(screen.getByText(/KukujeshiStocker/i)).toBeInTheDocument()
  })

  it('renders the login page at /login', () => {
    renderApp('/login')
    expect(screen.getByText(/Login/i)).toBeInTheDocument()
  })
})