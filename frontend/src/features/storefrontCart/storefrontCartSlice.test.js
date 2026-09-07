import { describe, it, expect } from 'vitest'
import storefrontCartReducer, { addItem, removeItem, clearCart, selectCartTotal, selectCartItemCount } from './storefrontCartSlice'

describe('storefrontCartSlice', () => {
  const item = { storeSlug: 'shop-a', variantId: 1, sku: 'SKU-1', name: 'Widget', unitPrice: 100 }

  it('adds an item to an empty cart', () => {
    const state = storefrontCartReducer(undefined, addItem(item))
    expect(state.items).toHaveLength(1)
    expect(state.storeSlug).toBe('shop-a')
  })

  it('increments quantity for the same variant', () => {
    let state = storefrontCartReducer(undefined, addItem(item))
    state = storefrontCartReducer(state, addItem(item))
    expect(state.items[0].quantity).toBe(2)
  })

  it('clears the cart when adding from a different store', () => {
    let state = storefrontCartReducer(undefined, addItem(item))
    state = storefrontCartReducer(state, addItem({ ...item, storeSlug: 'shop-b', variantId: 2, sku: 'SKU-2' }))
    expect(state.items).toHaveLength(1)
    expect(state.items[0].sku).toBe('SKU-2')
    expect(state.storeSlug).toBe('shop-b')
  })

  it('removes an item by variantId', () => {
    let state = storefrontCartReducer(undefined, addItem(item))
    state = storefrontCartReducer(state, removeItem(1))
    expect(state.items).toHaveLength(0)
  })

  it('clears the cart entirely', () => {
    let state = storefrontCartReducer(undefined, addItem(item))
    state = storefrontCartReducer(state, clearCart())
    expect(state.items).toHaveLength(0)
    expect(state.storeSlug).toBeNull()
  })

  it('computes cart total and item count via selectors', () => {
    const rootState = { storefrontCart: { items: [{ ...item, quantity: 3 }] } }
    expect(selectCartTotal(rootState)).toBe(300)
    expect(selectCartItemCount(rootState)).toBe(3)
  })
})