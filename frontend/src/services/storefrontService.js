import apiClient from './apiClient'

export const getStoreProducts = async (slug) => {
  const { data } = await apiClient.get(`/storefront/${slug}/products/`)
  return data.results
}

export const createStorefrontOrder = async (slug, { name, email, phone, items }) => {
  const { data } = await apiClient.post(`/storefront/${slug}/orders/`, { name, email, phone, items })
  return data // { public_reference, total }
}

export const initiateStorefrontCheckout = async (publicReference, email) => {
  const { data } = await apiClient.post(`/storefront/orders/${publicReference}/checkout/`, { email })
  return data // { checkout_url }
}

export const getStorefrontOrderStatus = async (publicReference) => {
  const { data } = await apiClient.get(`/storefront/orders/${publicReference}/status/`)
  return data
}