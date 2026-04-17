<template>
  <div class="home">
    <div class="home-header">
      <h1 class="page-title">📝 最新文章</h1>
    </div>
    
    <div class="filter-section">
      <div class="filter-group">
        <label>分类筛选：</label>
        <select v-model="selectedCategory" @change="loadPosts" class="filter-select">
          <option :value="null">全部分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>标签筛选：</label>
        <select v-model="selectedTag" @change="loadPosts" class="filter-select">
          <option :value="null">全部标签</option>
          <option v-for="tag in tags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="posts-grid">
      <article v-for="post in posts" :key="post.id" class="post-card">
        <div v-if="post.cover_image" class="post-cover">
          <img :src="post.cover_image" :alt="post.title" />
        </div>
        <div class="post-header">
          <span v-if="post.category" :class="['category-badge', 'cat-' + post.category.id]">{{ post.category.name }}</span>
          <div class="post-tags">
            <span v-for="tag in post.tags" :key="tag.id" class="tag-item">{{ tag.name }}</span>
          </div>
        </div>
        <h2 class="post-title">
          <router-link :to="`/post/${post.id}`">{{ post.title }}</router-link>
        </h2>
        <p class="post-summary">{{ post.summary || truncateContent(post.content) }}</p>
        <div class="post-stats">
          <span class="stat-item">❤️ {{ post.like_count }}</span>
          <span class="stat-item">💬 {{ post.comment_count }}</span>
        </div>
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
import { ref, onMounted, computed } from 'vue'
import { postApi, categoryApi, tagApi } from '../api'

const posts = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(true)
const error = ref(null)
const selectedCategory = ref(null)
const selectedTag = ref(null)

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token')
})

const truncateContent = (content) => {
  if (!content) return ''
  const plainText = content.replace(/[#*`_[\]!()]/g, '')
  return plainText.length > 150 ? plainText.substring(0, 150) + '...' : plainText
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadCategories = async () => {
  try {
    const response = await categoryApi.getCategories()
    categories.value = response.data
  } catch (err) {
    console.error('加载分类失败', err)
  }
}

const loadTags = async () => {
  try {
    const response = await tagApi.getTags()
    tags.value = response.data
  } catch (err) {
    console.error('加载标签失败', err)
  }
}

const loadPosts = async () => {
  try {
    loading.value = true
    error.value = null
    const params = { limit: 20 }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (selectedTag.value) {
      params.tag_id = selectedTag.value
    }
    const response = await postApi.getPublicPosts(params)
    posts.value = response.data
  } catch (err) {
    error.value = '加载文章失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadTags()
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
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.filter-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
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
  height: 200px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem 0;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.cat-1 { background: #e3f2fd; color: #1976d2; }
.cat-2 { background: #f3e5f5; color: #7b1fa2; }
.cat-3 { background: #e8f5e9; color: #388e3c; }
.cat-4 { background: #fff3e0; color: #f57c00; }

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
  margin: 1rem 1.5rem;
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
  margin: 0 1.5rem 1rem;
  font-size: 1rem;
}

.post-stats {
  display: flex;
  gap: 1rem;
  padding: 0 1.5rem;
  margin-bottom: 1rem;
}

.stat-item {
  font-size: 0.9rem;
  color: #888;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888;
  font-size: 0.9rem;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #eee;
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
