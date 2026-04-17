<template>
  <div id="app">
    <nav v-if="!isAdminRoute" class="navbar">
      <div class="container">
        <router-link to="/" class="logo">📝 我的博客</router-link>
        <div class="nav-links">
          <router-link to="/">首页</router-link>
          <template v-if="isLoggedIn">
            <router-link to="/admin">管理后台</router-link>
            <div class="user-info">
              <span class="user-name">👤 {{ currentUser?.username }}</span>
              <span v-if="currentUser?.is_superuser" class="user-badge">超级管理员</span>
              <a href="#" @click.prevent="logout" class="logout-link">退出</a>
            </div>
          </template>
          <router-link v-else to="/login">登录</router-link>
        </div>
      </div>
    </nav>
    <main :class="['main-content', { 'admin-content': isAdminRoute }]">
      <router-view />
    </main>
    <footer v-if="!isAdminRoute" class="footer">
      <div class="container">
        <p>🚀 基于 FastAPI + Vue 3 构建的个人博客系统</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const currentUser = ref(null)

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token')
})

const isAdminRoute = computed(() => {
  return route.path === '/admin'
})

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    currentUser.value = null
    router.push('/')
  }
}

// 监听路由变化，更新用户信息
watch(() => route.path, () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    currentUser.value = JSON.parse(userStr)
  } else {
    currentUser.value = null
  }
}, { immediate: true })
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: #f8f9fa;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
  transition: transform 0.3s;
}

.logo:hover {
  transform: scale(1.05);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-links a {
  padding: 8px 16px;
  color: rgba(255,255,255,0.9);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-links a:hover {
  background: rgba(255,255,255,0.15);
  color: white;
}

.nav-links a.router-link-active {
  background: rgba(255,255,255,0.2);
  color: white;
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
  padding-left: 16px;
  border-left: 1px solid rgba(255,255,255,0.2);
}

.user-name {
  color: white;
  font-weight: 500;
}

.user-badge {
  background: rgba(255,255,255,0.2);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.logout-link {
  cursor: pointer;
  color: rgba(255,255,255,0.8) !important;
}

.logout-link:hover {
  color: white !important;
  background: rgba(255,255,255,0.1) !important;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.main-content.admin-content {
  max-width: 100%;
  margin: 0;
  padding: 0;
}

.footer {
  background: #2c3e50;
  color: rgba(255,255,255,0.7);
  padding: 1.5rem 0;
  text-align: center;
  margin-top: auto;
}

.footer p {
  margin: 0;
  font-size: 0.9rem;
}
</style>
