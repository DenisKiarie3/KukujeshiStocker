import { describe, it, expect } from 'vitest'
import posReducer, { addItem, removeItem, clearCart, selectCartTotal } from './posSlice'

describe('posSlice', () => {
  const item = { variantId: 1, sku: 'SODA-500ML', name: 'Soda 500ml', unitPrice: 50 }

  it('adds a new item to an empty cart', () => {
    const state = posReducer({ items: [] }, addItem(item))
    expect(state.items).toHaveLength(1)
    expect(state.items[0].quantity).toBe(1)
  })

  it('increments quantity when the same variant is added again', () => {
    let state = posReducer({ items: [] }, addItem(item))
    state = posReducer(state, addItem(item))
    expect(state.items).toHaveLength(1)
    expect(state.items[0].quantity).toBe(2)
  })

  it('removes an item by variantId', () => {
    let state = posReducer({ items: [] }, addItem(item))
    state = posReducer(state, removeItem(1))
    expect(state.items).toHaveLength(0)
  })

  it('clears the cart', () => {
    let state = posReducer({ items: [] }, addItem(item))
    state = posReducer(state, clearCart())
    expect(state.items).toHaveLength(0)
  })

  it('computes the cart total via the selector', () => {
    const rootState = { pos: { items: [{ ...item, quantity: 3 }] } }
    expect(selectCartTotal(rootState)).toBe(150)
  })
})