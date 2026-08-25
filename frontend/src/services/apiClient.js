import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // sends the httpOnly refresh cookie on every request
})

export const setAccessToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

export const getCsrfToken = () => {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : null
}

/**
 * Calls the refresh endpoint directly, with the CSRF double-submit header
 * the backend requires. Used both by useAuthInit (on app load) and by the
 * response interceptor below (when a request hits a 401 mid-session).
 */
export const refreshAccessToken = async () => {
  const { data } = await apiClient.post('/auth/refresh/', null, {
    headers: { 'X-CSRFToken': getCsrfToken() },
  })
  return data // { access, user }
}

/**
 * Wires up automatic "access token expired -> refresh -> retry" handling.
 * Takes plain callbacks instead of importing the Redux store directly, to
 * avoid a circular import — see app/store.js, which calls this once.
 */
export const attachAuthInterceptor = ({ onRefreshSuccess, onRefreshFailure }) => {
  let isRefreshing = false
  let pendingRequests = []

  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      const responseStatus = error.response?.status
      const isAuthEndpoint = originalRequest?.url?.includes('/auth/')

      if (responseStatus !== 401 || originalRequest._retry || isAuthEndpoint) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push({ resolve, reject, originalRequest })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const data = await refreshAccessToken()
        setAccessToken(data.access)
        onRefreshSuccess(data)
        pendingRequests.forEach(({ resolve, originalRequest: req }) => resolve(apiClient(req)))
        pendingRequests = []
        return apiClient(originalRequest)
      } catch (refreshError) {
        onRefreshFailure()
        pendingRequests.forEach(({ reject }) => reject(refreshError))
        pendingRequests = []
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
  )
}

export default apiClient