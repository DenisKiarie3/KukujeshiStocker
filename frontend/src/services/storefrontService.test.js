import { describe, it, expect, vi } from 'vitest'
import apiClient from './apiClient'
import { getStoreProducts, createStorefrontOrder, initiateStorefrontCheckout, getStorefrontOrderStatus } from './storefrontService'

vi.mock('./apiClient', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('storefrontService', () => {
  it('fetches and unwraps store products', async () => {
    apiClient.get.mockResolvedValueOnce({ data: { results: [{ id: 1, name: 'Widget' }] } })
    const products = await getStoreProducts('shop-a')
    expect(apiClient.get).toHaveBeenCalledWith('/storefront/shop-a/products/')
    expect(products).toEqual([{ id: 1, name: 'Widget' }])
  })

  it('creates a storefront order', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { public_reference: 'abc-123', total: '100.00' } })
    const order = await createStorefrontOrder('shop-a', { name: 'Jane', email: 'jane@example.com', phone: '', items: [] })
    expect(order.public_reference).toBe('abc-123')
  })

  it('initiates storefront checkout', async () => {
    apiClient.post.mockResolvedValueOnce({ data: { checkout_url: 'https://checkout.paystack.co/x' } })
    const result = await initiateStorefrontCheckout('abc-123', 'jane@example.com')
    expect(apiClient.post).toHaveBeenCalledWith('/storefront/orders/abc-123/checkout/', { email: 'jane@example.com' })
    expect(result.checkout_url).toBe('https://checkout.paystack.co/x')
  })

  it('fetches order status', async () => {
    apiClient.get.mockResolvedValueOnce({ data: { payment_status: 'paid' } })
    const status = await getStorefrontOrderStatus('abc-123')
    expect(status.payment_status).toBe('paid')
  })
})