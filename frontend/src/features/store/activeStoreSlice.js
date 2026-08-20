import { createSlice } from '@reduxjs/toolkit'

/**
 * Tracks which Store the logged-in user is currently working in — relevant
 * because a person could own or staff more than one Store (see StoreStaff
 * in the backend). Nothing in the UI should assume "the" store; it should
 * always read from here.
 */
const activeStoreSlice = createSlice({
  name: 'activeStore',
  initialState: {
    storeId: null,
    storeName: null,
  },
  reducers: {
    setActiveStore: (state, action) => {
      state.storeId = action.payload.storeId
      state.storeName = action.payload.storeName
    },
    clearActiveStore: (state) => {
      state.storeId = null
      state.storeName = null
    },
  },
})

export const { setActiveStore, clearActiveStore } = activeStoreSlice.actions
export default activeStoreSlice.reducer