import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { store } from './app/store'
import { queryClient } from './app/queryClient'
import { setCredentials } from './features/auth/authSlice'
import './index.css'
import App from './App.jsx'

// TEMPORARY — DEV ONLY. Real login arrives in Phase 6; until then, this
// lets us prove the frontend can call the live, authenticated API.
// DELETE this whole block once LoginPage actually authenticates users.
if (import.meta.env.DEV && import.meta.env.VITE_DEV_ACCESS_TOKEN) {
  store.dispatch(
    setCredentials({
      user: { username: 'dev' },
      accessToken: import.meta.env.VITE_DEV_ACCESS_TOKEN,
    })
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  </StrictMode>,
)