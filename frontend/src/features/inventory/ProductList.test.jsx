import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import ProductList from './ProductList'
import apiClient from '../../services/apiClient'

vi.mock('../../services/apiClient', () => ({ default: { get: vi.fn() } }))

function renderWithClient(ui) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>)
}

describe('ProductList', () => {
  it('renders products returned by the API', async () => {
    apiClient.get.mockResolvedValueOnce({
      data: [{ id: 1, name: 'Sugar 2kg', base_price: '250.00', variants: [{ id: 1, sku: 'SUGAR-2KG', stock_quantity: 30 }] }],
    })

    renderWithClient(<ProductList />)
    expect(screen.getByText(/Loading products/i)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText('Sugar 2kg')).toBeInTheDocument())
    expect(screen.getByText(/30 in stock/i)).toBeInTheDocument()
  })

  it('shows an error message when the API call fails', async () => {
    apiClient.get.mockRejectedValueOnce({
      response: { data: { detail: 'Authentication credentials were not provided.' } },
    })

    renderWithClient(<ProductList />)
    await waitFor(() =>
      expect(screen.getByText(/Authentication credentials were not provided/i)).toBeInTheDocument()
    )
  })
})