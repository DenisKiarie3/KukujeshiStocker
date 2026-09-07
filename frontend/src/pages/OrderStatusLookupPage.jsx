import { useState } from 'react'
import { getStorefrontOrderStatus } from '../services/storefrontService'

function OrderStatusLookupPage() {
  const [reference, setReference] = useState('')
  const [order, setOrder] = useState(null)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setOrder(null)
    setIsLoading(true)
    try {
      const data = await getStorefrontOrderStatus(reference.trim())
      setOrder(data)
    } catch {
      setError('No order found with that reference.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold text-brand-700 text-center">Check Order Status</h1>
        <form onSubmit={handleSubmit} className="space-y-3 bg-white rounded-lg border border-neutral-200 p-6 shadow-sm">
          <input
            type="text"
            placeholder="Order reference"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
            required
            className="w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <button type="submit" disabled={isLoading}
            className="w-full rounded-md bg-brand-700 py-2 text-white font-medium disabled:opacity-50">
            {isLoading ? 'Checking…' : 'Check status'}
          </button>
        </form>
        {error && <p className="text-red-600 text-sm text-center">{error}</p>}
        {order && (
          <div className="bg-white rounded-lg border border-neutral-200 p-4 text-sm space-y-1">
            <p>Status: <span className="font-medium">{order.status}</span></p>
            <p>Payment: <span className="font-medium">{order.payment_status}</span></p>
            <p>Total: KES {order.total}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrderStatusLookupPage