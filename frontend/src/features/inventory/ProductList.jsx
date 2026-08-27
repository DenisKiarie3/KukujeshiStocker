import { useProducts } from './useProducts'
import BuyButton from '../checkout/BuyButton'

function ProductList() {
  const { data: products, isLoading, isError, error } = useProducts()

  if (isLoading) {
    return <p className="text-neutral-500">Loading products…</p>
  }

  if (isError) {
    return (
      <p className="text-red-600">
        Couldn't load products: {error?.response?.data?.detail || error.message}
      </p>
    )
  }

  if (!products || products.length === 0) {
    return <p className="text-neutral-500">No products yet.</p>
  }

  return (
    <ul className="w-full max-w-md space-y-2">
      {products.map((product) => (
        <li key={product.id} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-medium text-neutral-800">{product.name}</span>
            <span className="text-brand-700">KES {product.base_price}</span>
          </div>
          {product.variants.length > 0 && (
            <p className="text-sm text-neutral-500 mt-1">
              {product.variants[0].sku} — {product.variants[0].stock_quantity} in stock
            </p>
          )}
          <BuyButton product={product} />
        </li>
      ))}
    </ul>
  )
}

export default ProductList