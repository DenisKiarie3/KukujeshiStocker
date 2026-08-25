import { describe, it, expect, vi } from 'vitest'
import { getProducts } from './productService'
import apiClient from './apiClient'

vi.mock('./apiClient', () => ({ default: { get: vi.fn() } }))

describe('productService', () => {
  it('calls the products endpoint and returns the data', async () => {
    apiClient.get.mockResolvedValueOnce({ data: [{ id: 1, name: 'Test' }] })
    const result = await getProducts()
    expect(apiClient.get).toHaveBeenCalledWith('/products/')
    expect(result).toEqual([{ id: 1, name: 'Test' }])
  })
})