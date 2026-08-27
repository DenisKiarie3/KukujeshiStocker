import { useQuery } from '@tanstack/react-query'
import { getPaymentByReference } from '../../services/paymentService'

/**
 * Polls for a payment's status by its Paystack reference. The webhook that
 * actually confirms payment arrives asynchronously, server-to-server —
 * this is how the browser finds out once it has.
 */
export const usePaymentStatus = (reference) => {
  return useQuery({
    queryKey: ['payment-status', reference],
    queryFn: () => getPaymentByReference(reference),
    enabled: !!reference,
    refetchInterval: (query) => {
      const payment = query.state.data
      return payment && payment.status !== 'pending' ? false : 2000
    },
  })
}