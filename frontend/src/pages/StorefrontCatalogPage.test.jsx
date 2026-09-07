import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import storefrontCartReducer from '../features/storefrontCart/storefrontCartSlice'
import StorefrontCatalogPage from './StorefrontCatalogPage'
import * as storefrontService from '../services/storefrontService'

vi.mock('../services/storefrontService')

function renderPage() {
  const store = configureStore({ reducer: { storefrontCart: storefrontCartReducer } })
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/store/shop-a']}>
          <Routes>
            <Route path="/store/:slug" element={<StorefrontCatalogPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>
  )
}

describe('StorefrontCatalogPage', () => {
  it('renders products and allows adding an in-stock variant to the cart', async () => {
    storefrontService.getStoreProducts.mockResolvedValueOnce([
      { id: 1, name: 'Widget', description: '', base_price: '100.00', variants: [{ id: 9, sku: 'W-1', price: '100.00', in_stock: true }] },
    ])
    renderPage()
    await waitFor(() => expect(screen.getByText('Widget')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /add to cart/i }))
    await waitFor(() => expect(screen.getByText(/cart \(1\)/i)).toBeInTheDocument())
  })

  it('shows out of stock for a depleted variant', async () => {
    storefrontService.getStoreProducts.mockResolvedValueOnce([
      { id: 1, name: 'Widget', description: '', base_price: '100.00', variants: [{ id: 9, sku: 'W-1', price: '100.00', in_stock: false }] },
    ])
    renderPage()
    await waitFor(() => expect(screen.getByText(/out of stock/i)).toBeInTheDocument())
  })
})