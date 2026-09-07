import { useSearchParams, Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getStorefrontOrderStatus } from '../services/storefrontService'

function StorefrontCheckoutCallbackPage() {
  const { slug } = useParams()
  const [searchParams] = useSearchParams()
  const orderRef = searchParams.get('order')

  const { data: order, isLoading } = useQuery({
    queryKey: ['storefront-order-status', orderRef],
    queryFn: () => getStorefrontOrderStatus(orderRef),
    enabled: !!orderRef,
    refetchInterval: (query) => {
      const data = query.state.data
      return data && data.payment_status !== 'pending' ? false : 2000
    },
  })

  let message = 'Verifying your payment…'
  if (!orderRef) {
    message = 'Missing order reference.'
  } else if (!isLoading && order) {
    if (order.payment_status === 'paid') message = 'Payment successful! Your order is confirmed.'
    else if (order.payment_status === 'failed') message = 'Payment failed. Please try again.'
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
      <div className="text-center space-y-4 max-w-sm">
        <h1 className="text-2xl font-semibold text-brand-700">Order Status</h1>
        <p className="text-neutral-600">{message}</p>
        {orderRef && (
          <p className="text-xs text-neutral-400 break-all">
            Reference: {orderRef} — save this to check your order status later.
          </p>
        )}
        <Link to={`/store/${slug}`} className="text-brand-700 underline block">Back to shop</Link>
        <Link to="/order-status" className="text-brand-700 underline block">Check order status later</Link>
      </div>
    </div>
  )
}

export default StorefrontCheckoutCallbackPage