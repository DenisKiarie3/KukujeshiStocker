import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // sends the httpOnly refresh cookie on every request
})

/**
 * Keeps the in-memory access token attached to every outgoing request.
 * Never called directly from components — see app/store.js, which calls
 * this automatically whenever Redux's auth.accessToken changes.
 */
export const setAccessToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

export default apiClient