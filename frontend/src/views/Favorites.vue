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
    <div v-else class="favorites-list">
      <div v-if="favorites.length > 0">
        <article v-for="fav in favorites" :key="fav.id" class="favorite-card">
          <div v-if="fav.post.cover_image" class="post-cover">
            <img :src="fav.post.cover_image" :alt="fav.post.title" />
          </div>
          <div class="post-content">
            <div class="post-header">
              <span v-if="fav.post.category" :class="['category-badge', 'cat-' + fav.post.category.id]">
                {{ fav.post.category.name }}
              </span>
              <div class="post-tags">
                <span v-for="tag in fav.post.tags" :key="tag.id" class="tag-item">{{ tag.name }}</span>
              </div>
            </div>
            <h2 class="post-title">
              <router-link :to="`/post/${fav.post.id}`">{{ fav.post.title }}</router-link>
            </h2>
            <p class="post-summary">{{ fav.post.summary || truncateContent(fav.post.content) }}</p>
            <div class="post-meta">
              <div class="meta-left">
                <span class="post-author">👤 {{ fav.post.author_name || '未知作者' }}</span>
                <span class="post-date">📅 收藏于：{{ formatDate(fav.created_at) }}</span>
              </div>
              <div class="meta-right">
                <span class="stat-item">❤️ {{ fav.post.like_count }}</span>
                <span class="stat-item">💬 {{ fav.post.comment_count }}</span>
                <button @click="removeFavorite(fav.post.id)" class="btn-remove">取消收藏</button>
              </div>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="no-favorites">
        <p>暂无收藏的文章</p>
        <router-link to="/" class="btn btn-primary">去浏览文章</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { favoriteApi, postApi } from '../api'

const favorites = ref([])
const loading = ref(true)
const error = ref(null)

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

const loadFavorites = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await favoriteApi.getFavorites()
    favorites.value = response.data
  } catch (err) {
    error.value = '加载收藏失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (postId) => {
  if (!confirm('确定要取消收藏吗？')) return
  
  try {
    await postApi.toggleFavorite(postId)
    favorites.value = favorites.value.filter(f => f.post.id !== postId)
  } catch (err) {
    alert('操作失败')
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

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.favorite-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
  display: flex;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid #f0f0f0;
}

.favorite-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.post-cover {
  width: 200px;
  min-height: 180px;
  flex-shrink: 0;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-content {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
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
  font-size: 1.3rem;
  margin-bottom: 0.75rem;
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
  margin-bottom: 1rem;
  font-size: 0.95rem;
  flex: 1;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888;
  font-size: 0.85rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.meta-left {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.meta-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stat-item {
  font-size: 0.85rem;
}

.btn-remove {
  background: none;
  border: 1px solid #e74c3c;
  color: #e74c3c;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.btn-remove:hover {
  background: #e74c3c;
  color: white;
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
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .favorite-card {
    flex-direction: column;
  }
  
  .post-cover {
    width: 100%;
    height: 180px;
  }
  
  .post-meta {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
