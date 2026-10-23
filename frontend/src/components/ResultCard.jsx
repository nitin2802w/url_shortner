import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ResultCard({ data }) {
  const [copied, setCopied] = useState(false)
  const navigate = useNavigate()

  function handleCopy() {
    navigator.clipboard.writeText(data.short_url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="result-card">
      <p className="result-label">YOUR SHORT LINK</p>

      <a
        className="result-link"
        href={data.short_url}
        target="_blank"
        rel="noopener noreferrer"
      >
        {data.short_url}
      </a>

      <p className="result-original">↳ {data.long_url}</p>

      <div className="result-actions">
        <button
          className={`btn-copy ${copied ? 'copied' : ''}`}
          onClick={handleCopy}
        >
          {copied ? '✓ COPIED!' : 'COPY LINK'}
        </button>

        <button
          className="btn-stats"
          onClick={() => navigate(`/stats/${data.short_code}`)}
        >
          VIEW STATS →
        </button>
      </div>
    </div>
  )
}
