"use client";

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api, UserProfile } from './api'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: UserProfile | null
  isLoading: boolean

  login: (email: string, password: string) => Promise<boolean>
  register: (data: { email: string; password: string; first_name: string; last_name: string; phone?: string }) => Promise<{ success: boolean; message: string }>
  logout: () => void
  loadProfile: () => Promise<void>
  restoreSession: () => Promise<void>
  setUser: (user: UserProfile) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isLoading: true,

      login: async (email, password) => {
        const res = await api.login(email, password)
        if (res.status === 'success' && res.data) {
          api.setToken(res.data.access)
          set({
            accessToken: res.data.access,
            refreshToken: res.data.refresh,
          })
          await get().loadProfile()
          return true
        }
        return false
      },

      register: async (data) => {
        const res = await api.register(data)
        if (res.status === 'success') {
          return { success: true, message: 'Account created. Please log in.' }
        }
        return { success: false, message: res.message }
      },

      logout: () => {
        api.setToken(null)
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
        })
      },

      loadProfile: async () => {
        const res = await api.getProfile()
        if (res.status === 'success' && res.data) {
          set({ user: res.data })
        }
      },

      restoreSession: async () => {
        const { accessToken, refreshToken } = get()
        if (!accessToken) {
          set({ isLoading: false })
          return
        }

        api.setToken(accessToken)
        const profileRes = await api.getProfile()

        if (profileRes.status === 'success' && profileRes.data) {
          set({ user: profileRes.data, isLoading: false })
          return
        }

        // Access token expired, try refresh
        if (refreshToken) {
          const refreshRes = await api.refreshToken(refreshToken)
          if (refreshRes.status === 'success' && refreshRes.data) {
            api.setToken(refreshRes.data.access)
            set({ accessToken: refreshRes.data.access })
            const retryProfile = await api.getProfile()
            if (retryProfile.status === 'success' && retryProfile.data) {
              set({ user: retryProfile.data, isLoading: false })
              return
            }
          }
        }

        // Both failed, clear session
        api.setToken(null)
        set({ accessToken: null, refreshToken: null, user: null, isLoading: false })
      },

      setUser: (user) => set({ user }),
    }),
    {
      name: 'wela-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)
