import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      
      const token = response.data.access_token
      localStorage.setItem('token', token)
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      await fetchUser()
      return response.data
    } catch (error) {
      // Log the full error for debugging
      console.error('Login error:', error)
      console.error('Error response:', error.response)
      throw error
    }
  }

  const signup = async (userData) => {
    try {
      const response = await api.post('/api/auth/register', userData)
      return response.data
    } catch (error) {
      // Log the full error for debugging
      console.error('Signup error:', error)
      console.error('Error response:', error.response)
      // Re-throw with more details
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}


