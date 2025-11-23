import { useState } from 'react'
import api from '../services/api'
import './ResolveAlertModal.css'

function ResolveAlertModal({ alert, onClose, onSuccess }) {
  const [threatType, setThreatType] = useState('')
  const [details, setDetails] = useState('')
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!threatType) {
      setError('Please select threat type')
      return
    }

    if (!details.trim()) {
      setError('Please enter details')
      return
    }

    if (!file) {
      setError('Please upload an image')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('threat_type', threatType)
      formData.append('details', details)
      formData.append('file', file)

      await api.post(`/api/alerts/${alert.id}/resolve`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resolve alert. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.type.startsWith('image/')) {
        setFile(selectedFile)
        setError('')
      } else {
        setError('Please upload an image file')
        setFile(null)
      }
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Resolve Alert #{alert.id}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit} className="resolve-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="threatType">Threat Type *</label>
            <select
              id="threatType"
              value={threatType}
              onChange={(e) => setThreatType(e.target.value)}
              required
            >
              <option value="">Select threat type</option>
              <option value="real">Real Threat</option>
              <option value="false">False Threat</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="details">Details *</label>
            <textarea
              id="details"
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              required
              rows="5"
              placeholder="Enter details about the alert and what actions were taken..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="file">Upload Image *</label>
            <input
              type="file"
              id="file"
              accept="image/*"
              onChange={handleFileChange}
              required
            />
            {file && (
              <div className="file-preview">
                <p>Selected: {file.name}</p>
              </div>
            )}
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-button">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Resolving...' : 'Resolve Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ResolveAlertModal


