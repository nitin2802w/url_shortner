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

  const totalClicks = stats?.total_clicks ?? stats?.clicks ?? 0
  const deviceEntries = Object.entries(stats?.device_breakdown || {})
  const browserEntries = Object.entries(stats?.top_browsers || {})

  return (
    <>
      <Header />

      <div className="stats-card">
        <h2 className="stats-title">/{shortCode}</h2>

        {loading && <p style={{ opacity: 0.5 }}>Loading stats...</p>}

        {error && (
          <div style={{ color: 'var(--pink)', fontWeight: 700, fontSize: 18 }}>
            <p>⚠ {error}</p>
          </div>
        )}

        {stats && (
          <>
            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-value">{totalClicks}</div>
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

            {/* Device & Browser Breakdowns */}
            <div className="stats-breakdown-row">
              <div className="breakdown-card">
                <h3 className="breakdown-title">DEVICE BREAKDOWN</h3>
                {deviceEntries.length === 0 ? (
                  <p className="no-data">No click data yet</p>
                ) : (
                  <div className="breakdown-list">
                    {deviceEntries.map(([device, count]) => {
                      const pct = totalClicks > 0 ? Math.round((count / totalClicks) * 100) : 0
                      return (
                        <div key={device} className="breakdown-item">
                          <div className="breakdown-label-row">
                            <span className="breakdown-name">{device.toUpperCase()}</span>
                            <span className="breakdown-count">{count} ({pct}%)</span>
                          </div>
                          <div className="bar-container">
                            <div className="bar-fill" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              <div className="breakdown-card">
                <h3 className="breakdown-title">TOP BROWSERS</h3>
                {browserEntries.length === 0 ? (
                  <p className="no-data">No click data yet</p>
                ) : (
                  <div className="breakdown-list">
                    {browserEntries.map(([browser, count]) => {
                      const pct = totalClicks > 0 ? Math.round((count / totalClicks) * 100) : 0
                      return (
                        <div key={browser} className="breakdown-item">
                          <div className="breakdown-label-row">
                            <span className="breakdown-name">{browser}</span>
                            <span className="breakdown-count">{count} ({pct}%)</span>
                          </div>
                          <div className="bar-container">
                            <div className="bar-fill pink" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
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
