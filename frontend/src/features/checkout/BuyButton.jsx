import { useState } from 'react'
import { createOrder, addOrderItem, payOnline } from '../../services/paymentService'

/**
 * Deliberately minimal — a stand-in for a real storefront cart/checkout,
 * built here only to drive one real order through the real Paystack
 * pipeline. Not the final UI.
 */
function BuyButton({ product }) {
  const [email, setEmail] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const variant = product.variants?.[0]

  const handleBuy = async () => {
    if (!variant) return
    if (!email) {
      setError('Enter an email to test checkout.')
      return
    }
    setError(null)
    setIsProcessing(true)
    try {
      const order = await createOrder({ storeId: product.store })
      await addOrderItem({ orderId: order.id, variantId: variant.id, quantity: 1 })
      const { checkout_url } = await payOnline({ orderId: order.id, email })
      window.location.href = checkout_url
    } catch (err) {
      setError(err?.response?.data?.detail || 'Checkout failed.')
      setIsProcessing(false)
    }
  }

  if (!variant || variant.stock_quantity === 0) {
    return <p className="text-xs text-neutral-400 mt-2">Out of stock</p>
  }

  return (
    <div className="mt-2 flex items-center gap-2">
      <input
        type="email"
        placeholder="buyer@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="text-sm border border-neutral-300 rounded px-2 py-1 w-40"
      />
      <button
        onClick={handleBuy}
        disabled={isProcessing}
        className="text-sm bg-brand-700 text-white rounded px-3 py-1 disabled:opacity-50"
      >
        {isProcessing ? 'Redirecting…' : 'Buy (test)'}
      </button>
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  )
}

export default BuyButton