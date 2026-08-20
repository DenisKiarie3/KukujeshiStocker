import { createSlice } from '@reduxjs/toolkit'

const posSlice = createSlice({
  name: 'pos',
  initialState: {
    items: [], // { variantId, sku, name, unitPrice, quantity }
  },
  reducers: {
    addItem: (state, action) => {
      const { variantId, sku, name, unitPrice, quantity = 1 } = action.payload
      const existing = state.items.find((item) => item.variantId === variantId)
      if (existing) {
        existing.quantity += quantity
      } else {
        state.items.push({ variantId, sku, name, unitPrice, quantity })
      }
    },
    removeItem: (state, action) => {
      state.items = state.items.filter((item) => item.variantId !== action.payload)
    },
    clearCart: (state) => {
      state.items = []
    },
  },
})

export const { addItem, removeItem, clearCart } = posSlice.actions
export default posSlice.reducer

// Derived value, computed on read rather than stored — avoids the cart
// total ever drifting out of sync with its items.
export const selectCartTotal = (state) =>
  state.pos.items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0)