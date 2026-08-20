import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30s — inventory/orders don't need refetching on every render
      retry: 1,
    },
  },
})