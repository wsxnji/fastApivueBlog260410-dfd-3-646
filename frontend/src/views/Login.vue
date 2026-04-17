<template>
  <div class="login-page">
    <div class="login-container">
      <h1 class="login-title">🔐 管理员登录</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div class="login-tips">
        <p>💡 测试账号：</p>
        <p>超级管理员：admin / admin</p>
        <p>普通用户：user1 / user1</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await authApi.login(form.value)
    const { access_token } = response.data
    
    // 保存 token
    localStorage.setItem('token', access_token)
    
    // 获取用户信息
    const userResponse = await authApi.getMe()
    localStorage.setItem('user', JSON.stringify(userResponse.data))
    
    // 跳转到管理后台
    router.push('/admin')
  } catch (err) {
    console.error('登录失败:', err)
    if (err.response?.status === 401) {
      error.value = '用户名或密码错误'
    } else {
      error.value = '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 8px;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.login-tips {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  text-align: center;
  color: #666;
  font-size: 0.85rem;
}

.login-tips p {
  margin: 0.3rem 0;
}
</style>
