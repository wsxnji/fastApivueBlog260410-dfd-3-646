import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login(credentials) {
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    return api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  getMe() {
    return api.get('/auth/me')
  },
}

export const postApi = {
  getPosts(params) {
    return api.get('/posts', { params })
  },

  getPublicPosts(params) {
    return api.get('/posts/public', { params })
  },

  getPost(id) {
    return api.get(`/posts/${id}`)
  },

  createPost(data) {
    return api.post('/posts', data)
  },

  updatePost(id, data) {
    return api.put(`/posts/${id}`, data)
  },

  deletePost(id) {
    return api.delete(`/posts/${id}`)
  },

  toggleHidden(id, isHidden) {
    return api.patch(`/posts/${id}/hidden?is_hidden=${isHidden}`)
  },

  toggleLike(id) {
    return api.post(`/posts/${id}/like`)
  },

  toggleFavorite(id) {
    return api.post(`/posts/${id}/favorite`)
  },
}

export const categoryApi = {
  getCategories() {
    return api.get('/categories')
  },

  createCategory(data) {
    return api.post('/categories', data)
  },

  updateCategory(id, data) {
    return api.put(`/categories/${id}`, data)
  },

  deleteCategory(id) {
    return api.delete(`/categories/${id}`)
  },
}

export const tagApi = {
  getTags() {
    return api.get('/tags')
  },

  createTag(data) {
    return api.post('/tags', data)
  },

  updateTag(id, data) {
    return api.put(`/tags/${id}`, data)
  },

  deleteTag(id) {
    return api.delete(`/tags/${id}`)
  },
}

export const commentApi = {
  getComments(postId) {
    return api.get(`/posts/${postId}/comments`)
  },

  createComment(postId, data) {
    return api.post(`/posts/${postId}/comments`, data)
  },

  updateComment(commentId, data) {
    return api.put(`/comments/${commentId}`, data)
  },

  deleteComment(commentId) {
    return api.delete(`/comments/${commentId}`)
  },
}

export const favoriteApi = {
  getFavorites() {
    return api.get('/favorites')
  },
}

export default api
