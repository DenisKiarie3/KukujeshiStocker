import apiClient from './apiClient'

export const getProducts = async () => {
  const { data } = await apiClient.get('/products/')
  return data.results // pagination metadata (count/next/previous) is discarded for now — see explanation
}