import ProductList from '../features/inventory/ProductList'

function HomePage() {
  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col items-center py-12 px-4 gap-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-brand-700">KukujeshiStocker</h1>
        <p className="text-neutral-500">Live inventory from the Django API.</p>
      </div>
      <ProductList />
    </div>
  )
}

export default HomePage