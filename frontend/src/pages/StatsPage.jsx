import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { getStats } from '../services/api'

export default function StatsPage() {
  const { shortCode } = useParams()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats(shortCode)
      .then(setStats)
      .catch(err => {
        const msg = err?.detail || 'Stats not available yet.'
        setError(msg)
      })
      .finally(() => setLoading(false))
  }, [shortCode])

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    })
  }

  return (
    <>
      <Header />

      <div className="stats-card">
        <h2 className="stats-title">/{shortCode}</h2>

        {loading && <p style={{ opacity: 0.5 }}>Loading stats...</p>}

        {error && (
          <div style={{ color: 'var(--pink)', fontWeight: 700, fontSize: 18 }}>
            <p>⚠ {error}</p>
            <p style={{ opacity: 0.5, fontSize: 14, marginTop: 8, fontWeight: 500 }}>
              Full analytics coming in Module 5.
            </p>
          </div>
        )}

        {stats && (
          <>
            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-value">{stats.clicks ?? 0}</div>
                <div className="stat-label">TOTAL CLICKS</div>
              </div>
              <div className="stat-box">
                <div className="stat-value" style={{ fontSize: 28 }}>
                  {stats.created_at ? formatDate(stats.created_at) : '—'}
                </div>
                <div className="stat-label">CREATED ON</div>
              </div>
              <div className="stat-box">
                <div className="stat-value" style={{ fontSize: 28, color: 'var(--yellow)' }}>
                  {stats.custom_alias ? 'CUSTOM' : 'AUTO'}
                </div>
                <div className="stat-label">ALIAS TYPE</div>
              </div>
            </div>

            <div className="stats-url-row">
              <p className="stats-url-label">ORIGINAL URL</p>
              <a
                className="stats-url-value"
                href={stats.long_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {stats.long_url}
              </a>
            </div>
          </>
        )}

        <button className="btn-back" onClick={() => navigate('/')}>
          ← BACK
        </button>
      </div>
    </>
  )
}
