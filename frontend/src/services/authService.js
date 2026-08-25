import apiClient from './apiClient'

export const register = async ({ username, email, password }) => {
  const { data } = await apiClient.post('/auth/register/', { username, email, password })
  return data // { user, access }
}

export const login = async ({ username, password }) => {
  const { data } = await apiClient.post('/auth/login/', { username, password })
  return data // { user, access }
}

export const logout = async () => {
  await apiClient.post('/auth/logout/')
}