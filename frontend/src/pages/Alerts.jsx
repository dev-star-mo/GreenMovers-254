import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import ResolveAlertModal from '../components/ResolveAlertModal'
import './Alerts.css'

function Alerts() {
  const [unresolvedAlerts, setUnresolvedAlerts] = useState([])
  const [resolvedAlerts, setResolvedAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [showResolveModal, setShowResolveModal] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchAlerts = async () => {
    try {
      const [unresolvedRes, resolvedRes] = await Promise.all([
        api.get('/api/alerts?resolved=false'),
        api.get('/api/alerts?resolved=true')
      ])
      setUnresolvedAlerts(unresolvedRes.data)
      setResolvedAlerts(resolvedRes.data)
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResolve = (alert) => {
    setSelectedAlert(alert)
    setShowResolveModal(true)
  }

  const handleResolveSuccess = () => {
    setShowResolveModal(false)
    setSelectedAlert(null)
    fetchAlerts()
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return <div className="loading">Loading alerts...</div>
  }

  return (
    <div className="alerts-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>🌲 Forest Protection Dashboard</h2>
        </div>
        <div className="nav-links">
          <button onClick={() => navigate('/dashboard')} className="nav-link">
            Overview
          </button>
          <button onClick={() => navigate('/alerts')} className="nav-link active">
            Alerts
          </button>
          <div className="nav-user">
            <span>Welcome, {user?.full_name}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="alerts-content">
        <h1>Alert Management</h1>

        <div className="alerts-section">
          <h2>Unresolved Alerts</h2>
          {unresolvedAlerts.length === 0 ? (
            <div className="empty-state">
              <p>No unresolved alerts</p>
            </div>
          ) : (
            <div className="alerts-grid">
              {unresolvedAlerts.map((alert) => (
                <div key={alert.id} className="alert-card unresolved">
                  <div className="alert-header">
                    <span className="alert-id">Alert #{alert.id}</span>
                    <span className="alert-status-badge unresolved-badge">Active</span>
                  </div>
                  <div className="alert-details">
                    <p><strong>Sensor ID:</strong> {alert.sensor_id}</p>
                    <p><strong>Sensor Name:</strong> {alert.sensor_name}</p>
                    <p><strong>Alert Time:</strong> {formatDate(alert.alert_time)}</p>
                  </div>
                  <button
                    onClick={() => handleResolve(alert)}
                    className="resolve-button"
                  >
                    Resolve Alert
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="alerts-section">
          <h2>Resolved Alerts</h2>
          {resolvedAlerts.length === 0 ? (
            <div className="empty-state">
              <p>No resolved alerts</p>
            </div>
          ) : (
            <div className="alerts-grid">
              {resolvedAlerts.map((alert) => (
                <div key={alert.id} className="alert-card resolved">
                  <div className="alert-header">
                    <span className="alert-id">Alert #{alert.id}</span>
                    <span className="alert-status-badge resolved-badge">Resolved</span>
                  </div>
                  <div className="alert-details">
                    <p><strong>Sensor ID:</strong> {alert.sensor_id}</p>
                    <p><strong>Sensor Name:</strong> {alert.sensor_name}</p>
                    <p><strong>Alert Time:</strong> {formatDate(alert.alert_time)}</p>
                    <p><strong>Resolved At:</strong> {formatDate(alert.resolved_at)}</p>
                    <p><strong>Threat Type:</strong> {alert.threat_type === 'real' ? 'Real Threat' : 'False Threat'}</p>
                    {alert.resolution_details && (
                      <p><strong>Details:</strong> {alert.resolution_details}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showResolveModal && (
        <ResolveAlertModal
          alert={selectedAlert}
          onClose={() => setShowResolveModal(false)}
          onSuccess={handleResolveSuccess}
        />
      )}
    </div>
  )
}

export default Alerts


