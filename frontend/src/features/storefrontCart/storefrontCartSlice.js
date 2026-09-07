import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  storeSlug: null,
  items: [], // { variantId, sku, name, unitPrice, quantity }
}

const storefrontCartSlice = createSlice({
  name: 'storefrontCart',
  initialState,
  reducers: {
    addItem: (state, action) => {
      const { storeSlug, variantId, sku, name, unitPrice, quantity = 1 } = action.payload
      // A cart holds items from ONE store at a time, since checkout is
      // always scoped to a single store on the backend — switching stores
      // mid-session clears whatever was there before.
      if (state.storeSlug && state.storeSlug !== storeSlug) {
        state.items = []
      }
      state.storeSlug = storeSlug
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
      state.storeSlug = null
    },
  },
})

export const { addItem, removeItem, clearCart } = storefrontCartSlice.actions
export default storefrontCartSlice.reducer

export const selectCartTotal = (state) =>
  state.storefrontCart.items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0)

export const selectCartItemCount = (state) =>
  state.storefrontCart.items.reduce((sum, item) => sum + item.quantity, 0)