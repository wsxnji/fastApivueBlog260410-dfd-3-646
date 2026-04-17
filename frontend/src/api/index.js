import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 token
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

// 响应拦截器 - 处理 401 错误
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

// 认证相关 API
export const authApi = {
  // 登录
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

  // 获取当前用户信息
  getMe() {
    return api.get('/auth/me')
  },
}

// 文章相关 API
export const postApi = {
  // 获取所有文章（需要登录，后台使用）
  getPosts(params) {
    return api.get('/posts', { params })
  },

  // 获取公开文章（无需登录，前台使用）
  getPublicPosts(params) {
    return api.get('/posts/public', { params })
  },

  // 获取单篇文章
  getPost(id) {
    return api.get(`/posts/${id}`)
  },

  // 创建文章
  createPost(data) {
    return api.post('/posts', data)
  },

  // 更新文章
  updatePost(id, data) {
    return api.put(`/posts/${id}`, data)
  },

  // 删除文章
  deletePost(id) {
    return api.delete(`/posts/${id}`)
  },

  // 隐藏/显示文章（仅超级管理员）
  toggleHidden(id, isHidden) {
    return api.patch(`/posts/${id}/hidden?is_hidden=${isHidden}`)
  },
}

export default api
