<template>
  <div class="favorites">
    <div class="page-header">
      <h1 class="page-title">⭐ 我的收藏</h1>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="favorites.length > 0" class="posts-grid">
      <article v-for="fav in favorites" :key="fav.id" class="post-card">
        <div v-if="fav.cover" class="post-cover">
          <img :src="fav.cover" alt="封面" />
        </div>
        <div class="post-header">
          <span :class="['category-badge', 'cat-' + fav.category_name]">{{ fav.category_name || '其它' }}</span>
        </div>
        <h2 class="post-title">
          <router-link :to="`/post/${fav.id}`">{{ fav.title }}</router-link>
        </h2>
        <p class="post-summary">{{ fav.summary || '' }}</p>
        <div class="post-meta">
          <div class="meta-left">
            <span class="post-author">👤 {{ fav.author_name || '未知作者' }}</span>
            <span class="post-date">📅 {{ formatDate(fav.created_at) }}</span>
          </div>
          <router-link :to="`/post/${fav.id}`" class="read-more">阅读全文 →</router-link>
        </div>
      </article>
    </div>
    <div v-else class="no-favorites">
      <p>⭐ 暂无收藏文章</p>
      <router-link to="/" class="btn btn-primary">去发现文章</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { postApi } from '../api'

const favorites = ref([])
const loading = ref(true)
const error = ref(null)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadFavorites = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getMyFavorites()
    favorites.value = response.data
  } catch (err) {
    error.value = '加载收藏失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.posts-grid {
  display: grid;
  gap: 1.5rem;
}

.post-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.post-cover {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.post-header {
  padding: 1.5rem 1.5rem 0;
  margin-bottom: 1rem;
}

.category-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
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

.post-title {
  font-size: 1.4rem;
  margin: 0 1.5rem 1rem;
  line-height: 1.4;
}

.post-title a {
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.3s;
}

.post-title a:hover {
  color: #667eea;
}

.post-summary {
  color: #666;
  line-height: 1.7;
  margin: 0 1.5rem 1.5rem;
  font-size: 0.95rem;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem 1.5rem;
  color: #888;
  font-size: 0.9rem;
}

.meta-left {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.post-author,
.post-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.read-more {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.read-more:hover {
  color: #764ba2;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  background: #fee;
  border-radius: 8px;
}

.no-favorites {
  text-align: center;
  padding: 4rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 12px;
}

.no-favorites p {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s;
  font-size: 1rem;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}
</style>
