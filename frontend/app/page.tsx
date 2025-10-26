export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Quflux
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Your Social Media Management Platform
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded">
              Get Started
            </button>
            <button className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}