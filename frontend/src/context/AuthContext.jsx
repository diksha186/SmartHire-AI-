/**
 * Global authentication state: stores the JWT + user object and exposes
 * login / register / logout to every component through useAuth().
 */
import { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('smarthire_user')
    const token = localStorage.getItem('smarthire_token')
    if (stored && token) setUser(JSON.parse(stored))
    setLoading(false)
  }, [])

  const persist = (data) => {
    localStorage.setItem('smarthire_token', data.access_token)
    localStorage.setItem('smarthire_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const login = async (email, password) => {
    const { data } = await authApi.login({ email, password })
    return persist(data)
  }

  const register = async (payload) => {
    const { data } = await authApi.register(payload)
    return persist(data)
  }

  const logout = () => {
    localStorage.removeItem('smarthire_token')
    localStorage.removeItem('smarthire_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

/** Where each role should land after logging in. */
export const homeForRole = (role) =>
  role === 'employer' ? '/employer' : role === 'admin' ? '/admin' : '/candidate'
