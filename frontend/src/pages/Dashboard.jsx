import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const [sensors, setSensors] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/dashboard/overview')
      setSensors(response.data.sensors)
      setStatistics(response.data.statistics)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>🌲 Forest Protection Dashboard</h2>
        </div>
        <div className="nav-links">
          <button onClick={() => navigate('/dashboard')} className="nav-link active">
            Overview
          </button>
          <button onClick={() => navigate('/alerts')} className="nav-link">
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

      <div className="dashboard-content">
        {statistics && (
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Sensors</h3>
              <p className="stat-number">{statistics.total_sensors}</p>
            </div>
            <div className="stat-card">
              <h3>Active Alerts</h3>
              <p className="stat-number alert">{statistics.unresolved_alerts}</p>
            </div>
            <div className="stat-card">
              <h3>Resolved Alerts</h3>
              <p className="stat-number resolved">{statistics.resolved_alerts}</p>
            </div>
            <div className="stat-card">
              <h3>Total Alerts</h3>
              <p className="stat-number">{statistics.total_alerts}</p>
            </div>
          </div>
        )}

        <div className="forest-map-container">
          <h2>Forest Overview</h2>
          <div className="forest-map">
            <div className="forest-background">
              <div className="forest-image-placeholder">
                <p>🌲🌳🌲</p>
                <p>Forest Area</p>
              </div>
              {sensors.map((sensor) => (
                <SensorIcon
                  key={sensor.sensor_id}
                  sensor={sensor}
                  onClick={() => navigate('/alerts')}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SensorIcon({ sensor, onClick }) {
  const statusClass = sensor.status === 'red' ? 'sensor-red' : 'sensor-green'
  
  return (
    <div
      className={`sensor-icon ${statusClass}`}
      style={{
        left: `${(sensor.longitude + 180) / 360 * 100}%`,
        top: `${(90 - sensor.latitude) / 180 * 100}%`,
      }}
      onClick={onClick}
      title={`${sensor.sensor_name} - ${sensor.status === 'red' ? 'Alert Active' : 'No Alerts'}`}
    >
      <div className="sensor-pulse"></div>
      <div className="sensor-core">🎤</div>
    </div>
  )
}

export default Dashboard


