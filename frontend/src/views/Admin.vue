<template>
  <div class="admin-layout">
    <!-- 左侧菜单栏 -->
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
          @click.prevent="currentMenu = 'users'"
          :class="['menu-item', { active: currentMenu === 'users' }]"
        >
          <span class="menu-icon">👥</span>
          <span class="menu-text">用户管理</span>
        </a>
        <a 
          v-if="user?.is_superuser"
          href="#" 
          @click.prevent="currentMenu = 'roles'"
          :class="['menu-item', { active: currentMenu === 'roles' }]"
        >
          <span class="menu-icon">🔐</span>
          <span class="menu-text">角色管理</span>
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

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 文章管理 -->
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
                  <span :class="['category-tag', 'cat-' + post.category]">{{ post.category || '其它' }}</span>
                </td>
                <td>
                  <div class="tags-list">
                    <span v-for="tag in parseTags(post.tags)" :key="tag" class="post-tag">{{ tag }}</span>
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
                  <!-- 自己的文章：完整权限 -->
                  <template v-if="post.author_id === user?.id">
                    <router-link :to="`/edit/${post.id}`" class="btn btn-sm btn-edit">编辑</router-link>
                    <button @click="handleDelete(post.id)" class="btn btn-sm btn-danger">删除</button>
                  </template>
                  <!-- 别人的文章：仅超级管理员可隐藏/显示 -->
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

      <!-- 用户管理（仅超级管理员可见） -->
      <div v-if="currentMenu === 'users' && user?.is_superuser" class="content-section">
        <div class="section-header">
          <h1 class="page-title">用户管理</h1>
          <button class="btn btn-primary" @click="showCreateUserModal = true">+ 新建用户</button>
        </div>
        
        <div v-if="usersLoading" class="loading">加载中...</div>
        <div v-else-if="usersError" class="error">{{ usersError }}</div>
        <div v-else class="users-table">
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

      <!-- 角色管理（仅超级管理员可见） -->
      <div v-if="currentMenu === 'roles' && user?.is_superuser" class="content-section">
        <div class="section-header">
          <h1 class="page-title">角色管理</h1>
          <button class="btn btn-primary" @click="openCreateRoleModal">+ 新建角色</button>
        </div>
        
        <div v-if="rolesLoading" class="loading">加载中...</div>
        <div v-else-if="rolesError" class="error">{{ rolesError }}</div>
        <div v-else class="roles-table">
          <table v-if="roles.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>角色名称</th>
                <th>角色标识</th>
                <th>描述</th>
                <th>用户数</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="role in roles" :key="role.id">
                <td>{{ role.id }}</td>
                <td>
                  <div class="role-name-cell">
                    <span class="role-icon-small">{{ role.icon }}</span>
                    <span>{{ role.name }}</span>
                  </div>
                </td>
                <td><code class="role-code">{{ role.key }}</code></td>
                <td>{{ role.description }}</td>
                <td>
                  <span class="user-count">{{ getRoleUserCount(role.key) }} 人</span>
                </td>
                <td class="actions">
                  <button @click="openEditRoleModal(role)" class="btn btn-sm btn-edit">编辑</button>
                  <button v-if="!role.is_system" @click="handleDeleteRole(role)" class="btn btn-sm btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-data">
            <p>暂无角色数据</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 创建用户弹窗 -->
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

    <!-- 创建/编辑角色弹窗 -->
    <div v-if="showCreateRoleModal || showEditRoleModal" class="modal-overlay" @click.self="showCreateRoleModal = false; showEditRoleModal = false">
      <div class="modal">
        <h3>{{ showEditRoleModal ? '编辑角色' : '新建角色' }}</h3>
        <form @submit.prevent="handleSaveRole">
          <div class="form-group">
            <label>角色名称 <span class="required">*</span></label>
            <input v-model="currentRole.name" type="text" required placeholder="请输入角色名称，如：编辑">
          </div>
          <div class="form-group">
            <label>角色标识 <span class="required">*</span></label>
            <input v-model="currentRole.key" type="text" required placeholder="请输入角色标识，如：editor">
            <small class="form-help">用于系统识别的唯一标识，只能包含英文字母和下划线</small>
          </div>
          <div class="form-group">
            <label>图标</label>
            <select v-model="currentRole.icon" class="icon-select">
              <option value="👤">👤 用户</option>
              <option value="🔐">🔐 管理员</option>
              <option value="✏️">✏️ 编辑</option>
              <option value="👁️">👁️ 访客</option>
              <option value="⭐">⭐ VIP</option>
              <option value="🛡️">🛡️ 安全</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="currentRole.description" rows="3" placeholder="请输入角色描述"></textarea>
          </div>
          <div v-if="currentRole.is_system" class="form-notice">
            <span class="notice-icon">⚠️</span>
            <span>系统角色不能删除</span>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingRole">
              {{ savingRole ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showCreateRoleModal = false; showEditRoleModal = false">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postApi } from '../api'

const router = useRouter()
const currentMenu = ref('posts')
const posts = ref([])
const users = ref([])
const loading = ref(true)
const usersLoading = ref(false)
const error = ref(null)
const usersError = ref(null)
const user = ref(null)
const showCreateUserModal = ref(false)
const showCreateRoleModal = ref(false)
const showEditRoleModal = ref(false)
const creatingUser = ref(false)
const savingRole = ref(false)
const rolesLoading = ref(false)
const rolesError = ref(null)
const newUser = ref({
  username: '',
  password: '',
  is_superuser: false
})

// 角色数据
const roles = ref([
  { id: 1, name: '超级管理员', key: 'superuser', icon: '🔐', description: '拥有系统的所有权限', is_system: true },
  { id: 2, name: '普通用户', key: 'user', icon: '👤', description: '只能管理自己的文章', is_system: true }
])

const currentRole = ref({
  id: null,
  name: '',
  key: '',
  icon: '👤',
  description: '',
  is_system: false
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

// 获取作者名称
const getAuthorName = (authorId) => {
  if (!authorId) return '未知'
  const author = users.value.find(u => u.id === authorId)
  return author ? author.username : `用户#${authorId}`
}

// 解析标签字符串为数组
const parseTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(',').filter(tag => tag.trim())
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

const loadUsers = async () => {
  if (!user.value?.is_superuser) return
  
  try {
    usersLoading.value = true
    usersError.value = null
    // 这里需要添加获取用户列表的 API
    // const response = await userApi.getUsers()
    // users.value = response.data
    // 临时使用本地数据演示
    users.value = [
      { id: 1, username: 'admin', is_superuser: true, is_active: true, created_at: new Date().toISOString() },
      { id: 2, username: 'user1', is_superuser: false, is_active: true, created_at: new Date().toISOString() }
    ]
  } catch (err) {
    usersError.value = '加载用户列表失败'
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

// 隐藏/显示文章（仅超级管理员可操作他人文章）
const handleToggleHidden = async (post) => {
  const action = post.is_hidden ? '显示' : '隐藏'
  if (!confirm(`确定要${action}这篇文章吗？`)) return
  
  try {
    await postApi.toggleHidden(post.id, !post.is_hidden)
    await loadPosts()
    alert(`${action}成功`)
  } catch (err) {
    if (err.response?.status === 403) {
      alert('权限不足，仅超级管理员可操作')
    } else {
      alert('操作失败')
    }
    console.error(err)
  }
}

const handleCreateUser = async () => {
  try {
    creatingUser.value = true
    // 这里需要添加创建用户的 API
    // await userApi.createUser(newUser.value)
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

// 获取角色用户数量
const getRoleUserCount = (roleKey) => {
  if (roleKey === 'superuser') {
    return users.value.filter(u => u.is_superuser).length
  }
  return users.value.filter(u => !u.is_superuser).length
}

// 打开创建角色弹窗
const openCreateRoleModal = () => {
  currentRole.value = {
    id: null,
    name: '',
    key: '',
    icon: '👤',
    description: '',
    is_system: false
  }
  showCreateRoleModal.value = true
}

// 打开编辑角色弹窗
const openEditRoleModal = (role) => {
  currentRole.value = { ...role }
  showEditRoleModal.value = true
}

// 保存角色（创建或编辑）
const handleSaveRole = async () => {
  if (!currentRole.value.name || !currentRole.value.key) {
    alert('请填写角色名称和标识')
    return
  }
  
  try {
    savingRole.value = true
    
    if (currentRole.value.id) {
      // 编辑角色
      const index = roles.value.findIndex(r => r.id === currentRole.value.id)
      if (index !== -1) {
        roles.value[index] = { ...currentRole.value }
      }
      alert('角色更新成功')
      showEditRoleModal.value = false
    } else {
      // 创建角色
      const newId = Math.max(...roles.value.map(r => r.id), 0) + 1
      roles.value.push({
        ...currentRole.value,
        id: newId,
        is_system: false
      })
      alert('角色创建成功')
      showCreateRoleModal.value = false
    }
  } catch (err) {
    alert('保存失败')
    console.error(err)
  } finally {
    savingRole.value = false
  }
}

// 删除角色
const handleDeleteRole = async (role) => {
  if (role.is_system) {
    alert('系统角色不能删除')
    return
  }
  
  if (!confirm(`确定要删除角色 "${role.name}" 吗？`)) return
  
  try {
    // 检查是否有用户使用该角色
    const userCount = getRoleUserCount(role.key)
    if (userCount > 0) {
      alert(`该角色下有 ${userCount} 个用户，不能删除`)
      return
    }
    
    roles.value = roles.value.filter(r => r.id !== role.id)
    alert('角色删除成功')
  } catch (err) {
    alert('删除失败')
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
  loadUsers()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: calc(100vh - 140px);
}

/* 侧边栏 */
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

/* 主内容区 */
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

/* 按钮样式 */
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

/* 表格样式 */
.posts-table, .users-table {
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

.summary-cell {
  color: #666;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 8px;
}

/* 角色和状态标签 */
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

/* 加载和空状态 */
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

/* 弹窗 */
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
.form-group input[type="password"] {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-actions .btn {
  flex: 1;
}

/* 角色管理样式 */
.roles-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

.info-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e9ecef;
}

.role-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.role-icon {
  font-size: 2rem;
  margin-right: 12px;
}

.role-title {
  flex: 1;
}

.role-title h3 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.role-key {
  display: inline-block;
  background: #e9ecef;
  color: #6c757d;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-family: monospace;
}

.info-card p {
  color: #666;
  margin-bottom: 12px;
}

.info-card ul {
  margin: 0 0 20px 0;
  padding-left: 20px;
  color: #555;
}

.info-card li {
  margin-bottom: 6px;
}

.role-users {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.role-users .label {
  color: #888;
  font-size: 0.9rem;
}

.user-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
}

/* 角色管理表格样式 */
.roles-table {
  overflow-x: auto;
}

.role-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-icon-small {
  font-size: 1.2rem;
}

.role-code {
  background: #f4f4f4;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85rem;
  color: #666;
}

.user-count {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 表单样式 */
.form-help {
  display: block;
  margin-top: 4px;
  color: #888;
  font-size: 0.8rem;
}

.required {
  color: #e74c3c;
}

.icon-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
}

textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
}

.form-notice {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #856404;
}

.notice-icon {
  font-size: 1.2rem;
}

/* 文章管理样式 */
.posts-table tr.is-hidden {
  background: #f5f5f5;
  opacity: 0.7;
}

.posts-table tr.is-hidden .title-cell,
.posts-table tr.is-hidden .summary-cell {
  text-decoration: line-through;
  color: #999;
}

.my-post-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  margin-left: 8px;
  font-weight: 500;
}

.status-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-tag.visible {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-tag.hidden {
  background: #ffebee;
  color: #c62828;
}

.btn-success {
  background: #2ecc71;
  color: white;
}

.btn-success:hover {
  background: #27ae60;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover {
  background: #e67e22;
}

/* 分类标签样式 */
.category-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.cat-前端 {
  background: #e3f2fd;
  color: #1976d2;
}

.cat-后端 {
  background: #f3e5f5;
  color: #7b1fa2;
}

.cat-数据库 {
  background: #e8f5e9;
  color: #388e3c;
}

.cat-其它 {
  background: #fff3e0;
  color: #f57c00;
}

/* 文章标签样式 */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.post-tag {
  padding: 2px 8px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.75rem;
  color: #666;
}
</style>
