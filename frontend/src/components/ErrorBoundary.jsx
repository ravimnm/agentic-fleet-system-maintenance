import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded shadow max-w-md">
            <h1 className="text-lg font-semibold text-red-600">Application Error</h1>
            <p className="mt-2 text-slate-600 text-sm">{this.state.error?.message || 'Something went wrong'}</p>
            <button
              onClick={() => window.location.href = '/login'}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded"
            >
              Return to Login
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
