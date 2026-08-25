import apiClient from './apiClient'

export const getProducts = async () => {
  const { data } = await apiClient.get('/products/')
  return data
}