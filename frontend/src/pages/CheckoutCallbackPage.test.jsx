import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import CheckoutCallbackPage from './CheckoutCallbackPage'
import * as paymentService from '../services/paymentService'

vi.mock('../services/paymentService')

function renderCallback(search) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/checkout/callback${search}`]}>
        <Routes>
          <Route path="/checkout/callback" element={<CheckoutCallbackPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('CheckoutCallbackPage', () => {
  it('shows success message once payment resolves', async () => {
    paymentService.getPaymentByReference.mockResolvedValue({ status: 'success' })
    renderCallback('?reference=kjs-1')
    await waitFor(() => expect(screen.getByText(/payment successful/i)).toBeInTheDocument())
  })

  it('shows failure message when payment failed', async () => {
    paymentService.getPaymentByReference.mockResolvedValue({ status: 'failed' })
    renderCallback('?reference=kjs-2')
    await waitFor(() => expect(screen.getByText(/payment failed/i)).toBeInTheDocument())
  })
})