<template>
  <div class="home">
    <div class="home-header">
      <h1 class="page-title">📝 最新文章</h1>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="posts-grid">
      <article v-for="post in posts" :key="post.id" class="post-card">
        <div class="post-header">
          <span :class="['category-badge', 'cat-' + post.category]">{{ post.category || '其它' }}</span>
          <div class="post-tags">
            <span v-for="tag in parseTags(post.tags)" :key="tag" class="tag-item">{{ tag }}</span>
          </div>
        </div>
        <h2 class="post-title">
          <router-link :to="`/post/${post.id}`">{{ post.title }}</router-link>
        </h2>
        <p class="post-summary">{{ post.summary || truncateContent(post.content) }}</p>
        <div class="post-meta">
          <div class="meta-left">
            <span class="post-author">👤 {{ post.author_name || '未知作者' }}</span>
            <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
          </div>
          <router-link :to="`/post/${post.id}`" class="read-more">阅读全文 →</router-link>
        </div>
      </article>
    </div>
    <div v-if="posts.length === 0 && !loading" class="no-posts">
      <p>📝 暂无文章</p>
      <router-link v-if="isLoggedIn" to="/create" class="btn btn-primary">写第一篇文章</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { postApi } from '../api'

const posts = ref([])
const loading = ref(true)
const error = ref(null)

const truncateContent = (content) => {
  if (!content) return ''
  // 移除 Markdown 标记后截取
  const plainText = content.replace(/[#*`_[\]!()]/g, '')
  return plainText.length > 150 ? plainText.substring(0, 150) + '...' : plainText
}

// 解析标签字符串为数组
const parseTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(',').filter(tag => tag.trim())
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadPosts = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPublicPosts({ limit: 20 })
    posts.value = response.data
  } catch (err) {
    error.value = '加载文章失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-top: 1rem;
}

.posts-grid {
  display: grid;
  gap: 1.5rem;
}

.post-card {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid #f0f0f0;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
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

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  padding: 2px 10px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.75rem;
  color: #666;
}

.post-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
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
  margin-bottom: 1.5rem;
  font-size: 1rem;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.no-posts {
  text-align: center;
  padding: 4rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 12px;
}

.no-posts p {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}
</style>
