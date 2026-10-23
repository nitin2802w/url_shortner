import { useState } from 'react'
import { shortenUrl } from '../services/api'

export default function UrlForm({ onSuccess, onError, onClear }) {
  const [url, setUrl] = useState('')
  const [alias, setAlias] = useState('')
  const [showAlias, setShowAlias] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) return
    setLoading(true)
    onClear()
    try {
      const data = await shortenUrl(url.trim(), showAlias ? alias : null)
      onSuccess(data)
      setUrl('')
      setAlias('')
      setShowAlias(false)
    } catch (err) {
      const msg = extractError(err)
      onError(msg)
    } finally {
      setLoading(false)
    }
  }

  function extractError(err) {
    if (!err) return 'Something went wrong.'
    if (typeof err.detail === 'string') return err.detail
    if (Array.isArray(err.detail)) {
      // Pydantic 422 — show first validation message
      return err.detail[0]?.msg?.replace('Value error, ', '') || 'Validation error.'
    }
    return 'Something went wrong.'
  }

  return (
    <div className="url-form">
      <form className="url-box" onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="PASTE LONG URL"
          value={url}
          onChange={e => setUrl(e.target.value)}
          required
        />
        <button type="submit" className="go-btn" disabled={loading}>
          {loading ? <span className="spinner" /> : 'GO →'}
        </button>
      </form>

      <button
        type="button"
        className="alias-toggle"
        onClick={() => setShowAlias(v => !v)}
      >
        {showAlias ? '− Hide custom alias' : '+ Add custom alias'}
      </button>

      {showAlias && (
        <div className="alias-row">
          <span className="alias-prefix">localhost:8000/</span>
          <input
            className="alias-input"
            type="text"
            placeholder="my-link  (3–16 chars)"
            value={alias}
            onChange={e => setAlias(e.target.value)}
            maxLength={16}
          />
        </div>
      )}
    </div>
  )
}
