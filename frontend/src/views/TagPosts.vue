<template>
  <div class="tag-posts">
    <div class="page-header">
      <h1 class="page-title">
        🏷️ 标签：{{ tagName }}
      </h1>
      <router-link to="/" class="btn-back">← 返回首页</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="posts.length === 0" class="empty-state">
      <p>📝 该标签暂无文章</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
    <div v-else class="posts-grid">
      <article v-for="post in posts" :key="post.id" class="post-card">
        <div v-if="post.cover_image" class="post-cover">
          <img :src="post.cover_image" alt="文章封面" />
        </div>
        <div class="post-content-wrapper">
          <div class="post-header">
            <span v-if="post.category_name" class="category-badge">{{ post.category_name }}</span>
            <div v-if="post.tags" class="post-tags">
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
            <div class="meta-right">
              <span class="stat-item" title="点赞数">❤️ {{ post.likes_count || 0 }}</span>
              <span class="stat-item" title="评论数">💬 {{ post.comments_count || 0 }}</span>
              <span class="stat-item" title="收藏数">⭐ {{ post.favorites_count || 0 }}</span>
            </div>
          </div>
          <div class="post-actions">
            <router-link :to="`/post/${post.id}`" class="read-more">阅读全文 →</router-link>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { postApi } from '../api'

const route = useRoute()
const posts = ref([])
const loading = ref(true)
const error = ref(null)

const tagName = computed(() => route.params.tag)

const truncateContent = (content) => {
  if (!content) return ''
  const plainText = content.replace(/[#*`_[\]!()]/g, '')
  return plainText.length > 150 ? plainText.substring(0, 150) + '...' : plainText
}

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
    const params = { tag: tagName.value, limit: 20 }
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
  loadPosts()
})
</script>

<style scoped>
.tag-posts {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
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

.btn-back {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #764ba2;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
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
  padding: 2rem;
  color: #e74c3c;
  background: #fdf2f2;
  border-radius: 8px;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.empty-state p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  display: inline-block;
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
  transition: transform 0.3s;
}

.post-card:hover .post-cover img {
  transform: scale(1.05);
}

.post-content-wrapper {
  padding: 1.5rem;
}

.post-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.category-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.post-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-item {
  background: #f0f0f0;
  color: #666;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
}

.post-title {
  font-size: 1.5rem;
  margin: 0 0 0.75rem;
  line-height: 1.4;
}

.post-title a {
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.2s;
}

.post-title a:hover {
  color: #667eea;
}

.post-summary {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
  font-size: 0.875rem;
  color: #888;
}

.meta-left {
  display: flex;
  gap: 1rem;
}

.meta-right {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-actions {
  margin-top: 1rem;
}

.read-more {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.read-more:hover {
  color: #764ba2;
}
</style>
