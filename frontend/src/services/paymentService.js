import apiClient from './apiClient'

export const createOrder = async ({ storeId, channel = 'online' }) => {
  const { data } = await apiClient.post('/orders/', { store: storeId, channel })
  return data
}

export const addOrderItem = async ({ orderId, variantId, quantity = 1 }) => {
  const { data } = await apiClient.post(`/orders/${orderId}/add_item/`, { variant: variantId, quantity })
  return data
}

export const payOnline = async ({ orderId, email }) => {
  const { data } = await apiClient.post(`/orders/${orderId}/pay-online/`, { email })
  return data // { checkout_url }
}

export const getPaymentByReference = async (reference) => {
  const { data } = await apiClient.get(`/payments/?paystack_reference=${encodeURIComponent(reference)}`)
  return data.results[0] || null
}