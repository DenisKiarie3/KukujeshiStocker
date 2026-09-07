import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { createStorefrontOrder, initiateStorefrontCheckout } from '../services/storefrontService'
import { clearCart, selectCartTotal } from '../features/storefrontCart/storefrontCartSlice'

function StorefrontCheckoutPage() {
  const { slug } = useParams()
  const dispatch = useDispatch()
  const items = useSelector((state) => state.storefrontCart.items)
  const total = useSelector(selectCartTotal)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (items.length === 0) {
      setError('Your cart is empty.')
      return
    }
    setError(null)
    setIsSubmitting(true)
    try {
      const order = await createStorefrontOrder(slug, {
        name,
        email,
        phone,
        items: items.map((item) => ({ variant: item.variantId, quantity: item.quantity })),
      })
      const { checkout_url } = await initiateStorefrontCheckout(order.public_reference, email)
      dispatch(clearCart())
      window.location.href = checkout_url
    } catch (err) {
      setError(err?.response?.data?.detail || 'Checkout failed. Please try again.')
      setIsSubmitting(false)
    }
  }

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
        <div className="text-center space-y-3">
          <p className="text-neutral-600">Your cart is empty.</p>
          <Link to={`/store/${slug}`} className="text-brand-700 underline">Back to shop</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50 px-4 py-8">
      <div className="max-w-md mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-brand-700">Checkout</h1>

        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.variantId} className="flex justify-between text-sm bg-white rounded p-3 border border-neutral-200">
              <span>{item.name} ({item.sku}) × {item.quantity}</span>
              <span>KES {(item.unitPrice * item.quantity).toFixed(2)}</span>
            </li>
          ))}
        </ul>
        <p className="text-right font-semibold text-neutral-800">Total: KES {total.toFixed(2)}</p>

        <form onSubmit={handleSubmit} className="space-y-4 bg-white rounded-lg border border-neutral-200 p-6 shadow-sm">
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-neutral-700">Full name</label>
            <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-neutral-700">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-neutral-700">Phone</label>
            <input id="phone" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} required
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <button type="submit" disabled={isSubmitting}
            className="w-full rounded-md bg-brand-700 py-2 text-white font-medium disabled:opacity-50">
            {isSubmitting ? 'Redirecting…' : 'Pay now'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default StorefrontCheckoutPage