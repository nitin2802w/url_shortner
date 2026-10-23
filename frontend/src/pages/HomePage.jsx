import { useState } from 'react'
import Header from '../components/Header'
import UrlForm from '../components/UrlForm'
import ResultCard from '../components/ResultCard'
import ErrorBanner from '../components/ErrorBanner'

export default function HomePage() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  return (
    <>
      <Header />
      <h1 className="headline">SHORTEN<br />IT. NOW.</h1>
      <UrlForm
        onSuccess={data => { setResult(data); setError('') }}
        onError={msg => { setError(msg); setResult(null) }}
        onClear={() => { setError(''); setResult(null) }}
      />
      <ErrorBanner message={error} />
      {result && <ResultCard data={result} />}
    </>
  )
}
