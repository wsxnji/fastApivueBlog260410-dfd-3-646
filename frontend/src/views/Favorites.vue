<template>
  <div class="favorites-page">
    <div class="page-header">
      <h1 class="page-title">⭐ 我的收藏</h1>
      <router-link to="/" class="btn-back">← 返回首页</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="favorites.length === 0" class="empty-state">
      <p>📝 暂无收藏文章</p>
      <router-link to="/" class="btn btn-primary">去浏览文章</router-link>
    </div>
    <div v-else class="posts-grid">
      <article v-for="favorite in favorites" :key="favorite.id" class="post-card">
        <div v-if="favorite.post?.cover_image" class="post-cover">
          <img :src="favorite.post.cover_image" alt="文章封面" />
        </div>
        <div class="post-content-wrapper">
          <div class="post-header">
            <span v-if="favorite.post?.category_name" class="category-badge">{{ favorite.post.category_name }}</span>
            <div v-if="favorite.post?.tags" class="post-tags">
              <span v-for="tag in parseTags(favorite.post.tags)" :key="tag" class="tag-item">{{ tag }}</span>
            </div>
          </div>
          <h2 class="post-title">
            <router-link :to="`/post/${favorite.post?.id}`">{{ favorite.post?.title }}</router-link>
          </h2>
          <p class="post-summary">{{ favorite.post?.summary || truncateContent(favorite.post?.content) }}</p>
          <div class="post-meta">
            <div class="meta-left">
              <span class="post-author">👤 {{ favorite.post?.author_name || '未知作者' }}</span>
              <span class="post-date">📅 {{ formatDate(favorite.post?.created_at) }}</span>
            </div>
            <div class="meta-right">
              <span class="stat-item">❤️ {{ favorite.post?.likes_count || 0 }}</span>
              <span class="stat-item">💬 {{ favorite.post?.comments_count || 0 }}</span>
            </div>
          </div>
          <div class="post-actions">
            <router-link :to="`/post/${favorite.post?.id}`" class="read-more">阅读全文 →</router-link>
            <button @click="unfavorite(favorite.post?.id)" class="unfavorite-btn">取消收藏</button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { favoriteApi } from '../api'

const favorites = ref([])
const loading = ref(true)
const error = ref(null)

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
  if (!dateString) return ''
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
    const response = await favoriteApi.getFavorites()
    favorites.value = response.data
  } catch (err) {
    error.value = '加载收藏列表失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const unfavorite = async (postId) => {
  if (!confirm('确定要取消收藏这篇文章吗？')) return
  try {
    await favoriteApi.unfavoritePost(postId)
    favorites.value = favorites.value.filter(f => f.post?.id !== postId)
  } catch (err) {
    alert('取消收藏失败')
  }
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
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

.btn-back {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.btn-back:hover {
  color: #764ba2;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 3rem;
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
  color: #e74c3c;
}

.empty-state {
  color: #888;
}

.btn-primary {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-top: 1rem;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
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
  background: #e3f2fd;
  color: #1976d2;
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
  line-height: 1.6;
  margin-bottom: 1rem;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.meta-left {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.unfavorite-btn {
  background: none;
  border: 1px solid #e74c3c;
  color: #e74c3c;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.unfavorite-btn:hover {
  background: #e74c3c;
  color: white;
}
</style>
