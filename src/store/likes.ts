// store/likes.js
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'
import apiConfig from '../utils/api'

export const useLikeStore = defineStore('likeStore', {
  state: () => ({
    likedProjectIds: [],
  }),

  actions: {
    async fetchLikes() {
      const authStore = useAuthStore()
      try {
        const res = await axios.get(`${apiConfig.baseURL}/api/teams/likes/`, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        })
        this.likedProjectIds = res.data.map(like => like.team)
        localStorage.setItem('likedProjects', JSON.stringify(this.likedProjectIds))
      } catch (err) {
        console.error('Failed to fetch liked projects', err)
      }
    },

    async toggleLike(projectId) {
      const authStore = useAuthStore()
      try {
        await axios.post(`${apiConfig.baseURL}/api/teams/likes/toggle/${projectId}/`, {}, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        })
        
        if (this.likedProjectIds.includes(projectId)) {
          this.likedProjectIds = this.likedProjectIds.filter(id => id !== projectId)
        } else {
          this.likedProjectIds.push(projectId)
        }
        localStorage.setItem('likedProjects', JSON.stringify(this.likedProjectIds))
      } catch (err) {
        console.error('Error toggling like', err)
      }
    },
  },
})
