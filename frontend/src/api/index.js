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

// 分类相关 API
export const categoryApi = {
  // 获取分类列表
  getCategories() {
    return api.get('/categories')
  },

  // 创建分类（仅超级管理员）
  createCategory(data) {
    return api.post('/categories', data)
  },

  // 更新分类（仅超级管理员）
  updateCategory(id, data) {
    return api.put(`/categories/${id}`, data)
  },

  // 删除分类（仅超级管理员）
  deleteCategory(id) {
    return api.delete(`/categories/${id}`)
  },
}

// 标签相关 API
export const tagApi = {
  // 获取标签列表
  getTags() {
    return api.get('/tags')
  },

  // 创建标签（仅超级管理员）
  createTag(data) {
    return api.post('/tags', data)
  },

  // 更新标签（仅超级管理员）
  updateTag(id, data) {
    return api.put(`/tags/${id}`, data)
  },

  // 删除标签（仅超级管理员）
  deleteTag(id) {
    return api.delete(`/tags/${id}`)
  },
}

// 评论相关 API
export const commentApi = {
  // 获取文章评论列表
  getComments(postId) {
    return api.get(`/posts/${postId}/comments`)
  },

  // 创建评论
  createComment(postId, data) {
    return api.post(`/posts/${postId}/comments`, data)
  },

  // 删除评论
  deleteComment(commentId) {
    return api.delete(`/comments/${commentId}`)
  },
}

// 点赞相关 API
export const likeApi = {
  // 点赞文章
  likePost(postId) {
    return api.post(`/posts/${postId}/like`)
  },

  // 取消点赞
  unlikePost(postId) {
    return api.delete(`/posts/${postId}/like`)
  },

  // 检查点赞状态
  checkLikeStatus(postId) {
    return api.get(`/posts/${postId}/like/status`)
  },
}

// 收藏相关 API
export const favoriteApi = {
  // 收藏文章
  favoritePost(postId) {
    return api.post(`/posts/${postId}/favorite`)
  },

  // 取消收藏
  unfavoritePost(postId) {
    return api.delete(`/posts/${postId}/favorite`)
  },

  // 检查收藏状态
  checkFavoriteStatus(postId) {
    return api.get(`/posts/${postId}/favorite/status`)
  },

  // 获取用户收藏列表
  getFavorites() {
    return api.get('/favorites')
  },
}

// 用户相关 API
export const userApi = {
  // 获取用户列表（仅超级管理员）
  getUsers(params) {
    return api.get('/users', { params })
  },

  // 创建用户（仅超级管理员）
  createUser(data, isSuperuser = false) {
    return api.post('/users', data, { params: { is_superuser: isSuperuser } })
  },
}

export default api
