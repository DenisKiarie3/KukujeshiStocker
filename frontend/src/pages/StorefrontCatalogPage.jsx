import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useDispatch, useSelector } from 'react-redux'
import { getStoreProducts } from '../services/storefrontService'
import { addItem, selectCartItemCount } from '../features/storefrontCart/storefrontCartSlice'

function StorefrontCatalogPage() {
  const { slug } = useParams()
  const dispatch = useDispatch()
  const cartCount = useSelector(selectCartItemCount)

  const { data: products, isLoading, isError, error } = useQuery({
    queryKey: ['storefront-products', slug],
    queryFn: () => getStoreProducts(slug),
  })

  const handleAdd = (product, variant) => {
    dispatch(addItem({
      storeSlug: slug,
      variantId: variant.id,
      sku: variant.sku,
      name: product.name,
      unitPrice: parseFloat(variant.price),
      quantity: 1,
    }))
  }

  return (
    <div className="min-h-screen bg-neutral-50 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-brand-700">Shop</h1>
          <Link to={`/store/${slug}/checkout`} className="text-sm bg-brand-700 text-white rounded px-3 py-2">
            Cart ({cartCount})
          </Link>
        </div>

        {isLoading && <p className="text-neutral-500">Loading products…</p>}
        {isError && (
          <p className="text-red-600">
            Couldn't load this store: {error?.response?.data?.detail || error.message}
          </p>
        )}
        {!isLoading && !isError && products?.length === 0 && (
          <p className="text-neutral-500">This store has no products yet.</p>
        )}

        <ul className="space-y-3">
          {products?.map((product) => (
            <li key={product.id} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium text-neutral-800">{product.name}</span>
                <span className="text-brand-700">KES {product.base_price}</span>
              </div>
              {product.description && <p className="text-sm text-neutral-500 mt-1">{product.description}</p>}
              <div className="mt-2 space-y-1">
                {product.variants.map((variant) => (
                  <div key={variant.id} className="flex items-center justify-between text-sm">
                    <span className="text-neutral-600">{variant.sku} — KES {variant.price}</span>
                    {variant.in_stock ? (
                      <button
                        onClick={() => handleAdd(product, variant)}
                        className="text-xs bg-brand-700 text-white rounded px-2 py-1"
                      >
                        Add to cart
                      </button>
                    ) : (
                      <span className="text-xs text-neutral-400">Out of stock</span>
                    )}
                  </div>
                ))}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default StorefrontCatalogPage