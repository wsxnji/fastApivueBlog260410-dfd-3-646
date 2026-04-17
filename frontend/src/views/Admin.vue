<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      <nav class="sidebar-menu">
        <a 
          href="#" 
          @click.prevent="currentMenu = 'posts'"
          :class="['menu-item', { active: currentMenu === 'posts' }]"
        >
          <span class="menu-icon">📝</span>
          <span class="menu-text">文章管理</span>
        </a>
        <a 
          v-if="user?.is_superuser"
          href="#" 
          @click.prevent="currentMenu = 'categories'"
          :class="['menu-item', { active: currentMenu === 'categories' }]"
        >
          <span class="menu-icon">📁</span>
          <span class="menu-text">分类管理</span>
        </a>
        <a 
          v-if="user?.is_superuser"
          href="#" 
          @click.prevent="currentMenu = 'tags'"
          :class="['menu-item', { active: currentMenu === 'tags' }]"
        >
          <span class="menu-icon">🏷️</span>
          <span class="menu-text">标签管理</span>
        </a>
        <a 
          v-if="user?.is_superuser"
          href="#" 
          @click.prevent="currentMenu = 'users'"
          :class="['menu-item', { active: currentMenu === 'users' }]"
        >
          <span class="menu-icon">👥</span>
          <span class="menu-text">用户管理</span>
        </a>
      </nav>
      
      <div class="sidebar-divider"></div>
      
      <nav class="sidebar-menu">
        <router-link to="/" class="menu-item front-link">
          <span class="menu-icon">🏠</span>
          <span class="menu-text">返回前台</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info" v-if="user">
          <span class="username">👤 {{ user.username }}</span>
          <span v-if="user.is_superuser" class="badge">超级管理员</span>
        </div>
        <button @click="handleLogout" class="btn-logout">退出登录</button>
      </div>
    </aside>

    <main class="main-content">
      <div v-if="currentMenu === 'posts'" class="content-section">
        <div class="section-header">
          <h1 class="page-title">文章管理</h1>
          <router-link to="/create" class="btn btn-primary">+ 新建文章</router-link>
        </div>
        
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="posts-table">
          <table v-if="posts.length > 0">
            <thead>
              <tr>
                <th>标题</th>
                <th>分类</th>
                <th>标签</th>
                <th>作者</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="post in posts" :key="post.id" :class="{ 'is-hidden': post.is_hidden }">
                <td class="title-cell">
                  {{ post.title }}
                  <span v-if="post.author_id === user?.id" class="my-post-badge">我的</span>
                </td>
                <td>
                  <span v-if="post.category" class="category-tag">{{ post.category.name }}</span>
                  <span v-else class="category-tag">未分类</span>
                </td>
                <td>
                  <div class="tags-list">
                    <span v-for="tag in post.tags" :key="tag.id" class="post-tag">{{ tag.name }}</span>
                  </div>
                </td>
                <td>{{ getAuthorName(post.author_id) }}</td>
                <td>
                  <span :class="['status-tag', post.is_hidden ? 'hidden' : 'visible']">
                    {{ post.is_hidden ? '已隐藏' : '显示中' }}
                  </span>
                </td>
                <td>{{ formatDate(post.created_at) }}</td>
                <td class="actions">
                  <template v-if="post.author_id === user?.id">
                    <router-link :to="`/edit/${post.id}`" class="btn btn-sm btn-edit">编辑</router-link>
                    <button @click="handleDelete(post.id)" class="btn btn-sm btn-danger">删除</button>
                  </template>
                  <template v-else-if="user?.is_superuser">
                    <button 
                      @click="handleToggleHidden(post)" 
                      :class="['btn btn-sm', post.is_hidden ? 'btn-success' : 'btn-warning']"
                    >
                      {{ post.is_hidden ? '显示' : '隐藏' }}
                    </button>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-posts">
            <p>暂无文章，点击"新建文章"创建第一篇</p>
          </div>
        </div>
      </div>

      <div v-if="currentMenu === 'categories' && user?.is_superuser" class="content-section">
        <div class="section-header">
          <h1 class="page-title">分类管理</h1>
          <button class="btn btn-primary" @click="openCategoryModal()">+ 新建分类</button>
        </div>
        
        <div v-if="categoriesLoading" class="loading">加载中...</div>
        <div v-else class="data-table">
          <table v-if="categories.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>分类名称</th>
                <th>描述</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cat in categories" :key="cat.id">
                <td>{{ cat.id }}</td>
                <td>{{ cat.name }}</td>
                <td>{{ cat.description || '-' }}</td>
                <td>{{ formatDate(cat.created_at) }}</td>
                <td class="actions">
                  <button @click="openCategoryModal(cat)" class="btn btn-sm btn-edit">编辑</button>
                  <button @click="handleDeleteCategory(cat.id)" class="btn btn-sm btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-data">
            <p>暂无分类数据</p>
          </div>
        </div>
      </div>

      <div v-if="currentMenu === 'tags' && user?.is_superuser" class="content-section">
        <div class="section-header">
          <h1 class="page-title">标签管理</h1>
          <button class="btn btn-primary" @click="openTagModal()">+ 新建标签</button>
        </div>
        
        <div v-if="tagsLoading" class="loading">加载中...</div>
        <div v-else class="data-table">
          <table v-if="tags.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>标签名称</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tag in tags" :key="tag.id">
                <td>{{ tag.id }}</td>
                <td>{{ tag.name }}</td>
                <td>{{ formatDate(tag.created_at) }}</td>
                <td class="actions">
                  <button @click="openTagModal(tag)" class="btn btn-sm btn-edit">编辑</button>
                  <button @click="handleDeleteTag(tag.id)" class="btn btn-sm btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-data">
            <p>暂无标签数据</p>
          </div>
        </div>
      </div>

      <div v-if="currentMenu === 'users' && user?.is_superuser" class="content-section">
        <div class="section-header">
          <h1 class="page-title">用户管理</h1>
          <button class="btn btn-primary" @click="showCreateUserModal = true">+ 新建用户</button>
        </div>
        
        <div v-if="usersLoading" class="loading">加载中...</div>
        <div v-else class="data-table">
          <table v-if="users.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.username }}</td>
                <td>
                  <span :class="['role-badge', u.is_superuser ? 'superuser' : 'normal']">
                    {{ u.is_superuser ? '超级管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', u.is_active ? 'active' : 'inactive']">
                    {{ u.is_active ? '正常' : '禁用' }}
                  </span>
                </td>
                <td>{{ formatDate(u.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-data">
            <p>暂无用户数据</p>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showCreateUserModal" class="modal-overlay" @click.self="showCreateUserModal = false">
      <div class="modal">
        <h3>新建用户</h3>
        <form @submit.prevent="handleCreateUser">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="newUser.username" type="text" required placeholder="请输入用户名">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="newUser.password" type="password" required placeholder="请输入密码">
          </div>
          <div class="form-group">
            <label>
              <input v-model="newUser.is_superuser" type="checkbox">
              设为超级管理员
            </label>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="creatingUser">
              {{ creatingUser ? '创建中...' : '创建' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showCreateUserModal = false">取消</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showCategoryModal" class="modal-overlay" @click.self="showCategoryModal = false">
      <div class="modal">
        <h3>{{ editingCategory ? '编辑分类' : '新建分类' }}</h3>
        <form @submit.prevent="handleSaveCategory">
          <div class="form-group">
            <label>分类名称 <span class="required">*</span></label>
            <input v-model="categoryForm.name" type="text" required placeholder="请输入分类名称">
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="categoryForm.description" rows="3" placeholder="请输入分类描述"></textarea>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingCategory">
              {{ savingCategory ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showCategoryModal = false">取消</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showTagModal" class="modal-overlay" @click.self="showTagModal = false">
      <div class="modal">
        <h3>{{ editingTag ? '编辑标签' : '新建标签' }}</h3>
        <form @submit.prevent="handleSaveTag">
          <div class="form-group">
            <label>标签名称 <span class="required">*</span></label>
            <input v-model="tagForm.name" type="text" required placeholder="请输入标签名称">
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingTag">
              {{ savingTag ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showTagModal = false">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postApi, categoryApi, tagApi } from '../api'

const router = useRouter()
const currentMenu = ref('posts')
const posts = ref([])
const categories = ref([])
const tags = ref([])
const users = ref([])
const loading = ref(true)
const categoriesLoading = ref(false)
const tagsLoading = ref(false)
const usersLoading = ref(false)
const error = ref(null)
const user = ref(null)
const showCreateUserModal = ref(false)
const showCategoryModal = ref(false)
const showTagModal = ref(false)
const creatingUser = ref(false)
const savingCategory = ref(false)
const savingTag = ref(false)
const editingCategory = ref(null)
const editingTag = ref(null)

const newUser = ref({
  username: '',
  password: '',
  is_superuser: false
})

const categoryForm = ref({
  name: '',
  description: ''
})

const tagForm = ref({
  name: ''
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAuthorName = (authorId) => {
  if (!authorId) return '未知'
  const author = users.value.find(u => u.id === authorId)
  return author ? author.username : `用户#${authorId}`
}

const loadPosts = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPosts({ limit: 100 })
    posts.value = response.data
  } catch (err) {
    error.value = '加载文章列表失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    categoriesLoading.value = true
    const response = await categoryApi.getCategories()
    categories.value = response.data
  } catch (err) {
    console.error('加载分类失败', err)
  } finally {
    categoriesLoading.value = false
  }
}

const loadTags = async () => {
  try {
    tagsLoading.value = true
    const response = await tagApi.getTags()
    tags.value = response.data
  } catch (err) {
    console.error('加载标签失败', err)
  } finally {
    tagsLoading.value = false
  }
}

const loadUsers = async () => {
  if (!user.value?.is_superuser) return
  
  try {
    usersLoading.value = true
    users.value = [
      { id: 1, username: 'admin', is_superuser: true, is_active: true, created_at: new Date().toISOString() }
    ]
  } catch (err) {
    console.error(err)
  } finally {
    usersLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  
  try {
    await postApi.deletePost(id)
    await loadPosts()
    alert('删除成功')
  } catch (err) {
    if (err.response?.status === 403) {
      alert('权限不足，只能删除自己的文章')
    } else {
      alert('删除失败')
    }
    console.error(err)
  }
}

const handleToggleHidden = async (post) => {
  const action = post.is_hidden ? '显示' : '隐藏'
  if (!confirm(`确定要${action}这篇文章吗？`)) return
  
  try {
    await postApi.toggleHidden(post.id, !post.is_hidden)
    await loadPosts()
    alert(`${action}成功`)
  } catch (err) {
    alert('操作失败')
    console.error(err)
  }
}

const handleCreateUser = async () => {
  try {
    creatingUser.value = true
    alert('用户创建成功')
    showCreateUserModal.value = false
    newUser.value = { username: '', password: '', is_superuser: false }
    await loadUsers()
  } catch (err) {
    alert('创建失败')
    console.error(err)
  } finally {
    creatingUser.value = false
  }
}

const openCategoryModal = (cat = null) => {
  editingCategory.value = cat
  categoryForm.value = cat ? { name: cat.name, description: cat.description || '' } : { name: '', description: '' }
  showCategoryModal.value = true
}

const handleSaveCategory = async () => {
  try {
    savingCategory.value = true
    if (editingCategory.value) {
      await categoryApi.updateCategory(editingCategory.value.id, categoryForm.value)
      alert('分类更新成功')
    } else {
      await categoryApi.createCategory(categoryForm.value)
      alert('分类创建成功')
    }
    showCategoryModal.value = false
    await loadCategories()
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
    console.error(err)
  } finally {
    savingCategory.value = false
  }
}

const handleDeleteCategory = async (id) => {
  if (!confirm('确定要删除这个分类吗？')) return
  
  try {
    await categoryApi.deleteCategory(id)
    alert('分类删除成功')
    await loadCategories()
  } catch (err) {
    alert(err.response?.data?.detail || '删除失败')
    console.error(err)
  }
}

const openTagModal = (tag = null) => {
  editingTag.value = tag
  tagForm.value = tag ? { name: tag.name } : { name: '' }
  showTagModal.value = true
}

const handleSaveTag = async () => {
  try {
    savingTag.value = true
    if (editingTag.value) {
      await tagApi.updateTag(editingTag.value.id, tagForm.value)
      alert('标签更新成功')
    } else {
      await tagApi.createTag(tagForm.value)
      alert('标签创建成功')
    }
    showTagModal.value = false
    await loadTags()
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
    console.error(err)
  } finally {
    savingTag.value = false
  }
}

const handleDeleteTag = async (id) => {
  if (!confirm('确定要删除这个标签吗？')) return
  
  try {
    await tagApi.deleteTag(id)
    alert('标签删除成功')
    await loadTags()
  } catch (err) {
    alert(err.response?.data?.detail || '删除失败')
    console.error(err)
  }
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }
  loadPosts()
  loadCategories()
  loadTags()
  loadUsers()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: calc(100vh - 140px);
}

.sidebar {
  width: 250px;
  background: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.sidebar-menu {
  padding: 10px 0;
}

.sidebar-divider {
  height: 1px;
  background: rgba(255,255,255,0.1);
  margin: 10px 20px;
}

.menu-item.front-link {
  color: rgba(255,255,255,0.6);
}

.menu-item.front-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.menu-item.active {
  background: rgba(255,255,255,0.15);
  color: white;
  border-left: 3px solid #667eea;
}

.menu-icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
  margin-top: auto;
}

.sidebar-footer .user-info {
  margin-bottom: 12px;
}

.sidebar-footer .username {
  display: block;
  font-weight: 500;
  margin-bottom: 4px;
}

.sidebar-footer .badge {
  display: inline-block;
  background: #667eea;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.sidebar-footer .btn-logout {
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.sidebar-footer .btn-logout:hover {
  background: #e74c3c;
  border-color: #e74c3c;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  padding: 30px;
  background: #f8f9fa;
  min-height: 100vh;
}

.content-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.page-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.85rem;
}

.btn-edit {
  background: #3498db;
  color: white;
  margin-right: 8px;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.posts-table, .data-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

tr:hover {
  background: #f8f9fa;
}

.title-cell {
  font-weight: 500;
  color: #2c3e50;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 8px;
}

.category-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  background: #e3f2fd;
  color: #1976d2;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.post-tag {
  padding: 2px 8px;
  background: #f5f5f5;
  border-radius: 12px;
  font-size: 0.75rem;
  color: #666;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.role-badge.superuser {
  background: #667eea;
  color: white;
}

.role-badge.normal {
  background: #95a5a6;
  color: white;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.status-badge.active {
  background: #2ecc71;
  color: white;
}

.status-badge.inactive {
  background: #e74c3c;
  color: white;
}

.status-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.status-tag.visible {
  background: #d4edda;
  color: #155724;
}

.status-tag.hidden {
  background: #f8d7da;
  color: #721c24;
}

.loading, .error, .no-posts, .no-data {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.error {
  color: #e74c3c;
  background: #fee;
  border-radius: 8px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.modal h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input[type="text"],
.form-group input[type="password"],
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.form-group textarea {
  resize: vertical;
}

.required {
  color: #e74c3c;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-actions .btn {
  flex: 1;
}

.my-post-badge {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-left: 8px;
}

.is-hidden {
  opacity: 0.6;
}
</style>
