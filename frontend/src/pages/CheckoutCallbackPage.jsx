import { useSearchParams, Link } from 'react-router-dom'
import { usePaymentStatus } from '../features/checkout/usePaymentStatus'

function CheckoutCallbackPage() {
  const [searchParams] = useSearchParams()
  const reference = searchParams.get('reference') || searchParams.get('trxref')
  const { data: payment, isLoading } = usePaymentStatus(reference)

  let message = 'Verifying payment…'
  if (!isLoading && payment) {
    if (payment.status === 'success') message = 'Payment successful! Stock and order updated.'
    else if (payment.status === 'failed') message = 'Payment failed or amount mismatch.'
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
      <div className="text-center space-y-4">
        <h1 className="text-2xl font-semibold text-brand-700">Checkout</h1>
        <p className="text-neutral-600">{message}</p>
        <Link to="/" className="text-brand-700 underline">Back to dashboard</Link>
      </div>
    </div>
  )
}

export default CheckoutCallbackPage