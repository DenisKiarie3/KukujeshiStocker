import { vi, describe, it, expect } from 'vitest'
import apiClient from './apiClient'
import { createOrder, addOrderItem, payOnline, getPaymentByReference } from './paymentService'

vi.mock('./apiClient', () => ({ default: { post: vi.fn(), get: vi.fn() } }))

describe('paymentService', () => {
  it('creates an order for a store', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { id: 1 } })
    const order = await createOrder({ storeId: 5 })
    expect(apiClient.post).toHaveBeenCalledWith('/orders/', { store: 5, channel: 'online' })
    expect(order.id).toBe(1)
  })

  it('adds an item to an order', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { id: 1 } })
    await addOrderItem({ orderId: 1, variantId: 9, quantity: 2 })
    expect(apiClient.post).toHaveBeenCalledWith('/orders/1/add_item/', { variant: 9, quantity: 2 })
  })

  it('initiates online payment', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { checkout_url: 'https://checkout.paystack.co/x' } })
    const result = await payOnline({ orderId: 1, email: 'a@example.com' })
    expect(apiClient.post).toHaveBeenCalledWith('/orders/1/pay-online/', { email: 'a@example.com' })
    expect(result.checkout_url).toBe('https://checkout.paystack.co/x')
  })

  it('fetches a payment by reference', async () => {
    apiClient.get.mockResolvedValueOnce({ data: { results: [{ id: 1, status: 'success' }] } })
    const payment = await getPaymentByReference('kjs-1')
    expect(payment.status).toBe('success')
  })

  it('returns null when no payment matches the reference', async () => {
    apiClient.get.mockResolvedValueOnce({ data: { results: [] } })
    expect(await getPaymentByReference('unknown')).toBeNull()
  })
})