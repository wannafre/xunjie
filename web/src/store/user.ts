import { defineStore } from 'pinia'
import request from '../utils/request'

export interface UserState {
  token: string | null
  username: string
  roles: string[]
  avatar: string
  introduction: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token'),
    username: '',
    roles: [],
    avatar: '',
    introduction: ''
  }),
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    clearToken() {
      this.token = null
      this.username = ''
      this.roles = []
      this.avatar = ''
      this.introduction = ''
      localStorage.removeItem('token')
    },
    async login(loginForm: { username: string; password: string }) {
      const res: any = await request.post('/auth/login', loginForm)
      if (res.access_token) {
        this.setToken(res.access_token)
        return res
      }
      throw new Error('Login failed')
    },
    async getInfo() {
      const res: any = await request.get('/auth/info')
      this.username = res.username
      this.roles = res.roles
      this.avatar = res.avatar
      this.introduction = res.introduction
      return res
    },
    async logout() {
      try {
        await request.post('/auth/logout')
      } finally {
        this.clearToken()
      }
    }
  }
})
