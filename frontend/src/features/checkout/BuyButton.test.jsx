import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import BuyButton from './BuyButton'
import * as paymentService from '../../services/paymentService'

vi.mock('../../services/paymentService')

const product = { id: 1, store: 5, variants: [{ id: 9, sku: 'SKU-1', stock_quantity: 10 }] }

describe('BuyButton', () => {
  beforeEach(() => vi.resetAllMocks())

  it('shows out of stock when variant has zero stock', () => {
    render(<BuyButton product={{ ...product, variants: [{ id: 9, sku: 'SKU-1', stock_quantity: 0 }] }} />)
    expect(screen.getByText(/out of stock/i)).toBeInTheDocument()
  })

  it('requires an email before checkout', () => {
    render(<BuyButton product={product} />)
    fireEvent.click(screen.getByRole('button', { name: /buy/i }))
    expect(screen.getByText(/enter an email/i)).toBeInTheDocument()
  })

  it('runs the full checkout chain and redirects on success', async () => {
    paymentService.createOrder.mockResolvedValueOnce({ id: 1 })
    paymentService.addOrderItem.mockResolvedValueOnce({})
    paymentService.payOnline.mockResolvedValueOnce({ checkout_url: 'https://checkout.paystack.co/x' })
    delete window.location
    window.location = { href: '' }

    render(<BuyButton product={product} />)
    fireEvent.change(screen.getByPlaceholderText(/buyer@example.com/i), { target: { value: 'buyer@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: /buy/i }))

    await waitFor(() => expect(window.location.href).toBe('https://checkout.paystack.co/x'))
    expect(paymentService.createOrder).toHaveBeenCalledWith({ storeId: 5 })
    expect(paymentService.addOrderItem).toHaveBeenCalledWith({ orderId: 1, variantId: 9, quantity: 1 })
  })
})