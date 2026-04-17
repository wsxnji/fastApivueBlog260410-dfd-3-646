<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="post" class="post-content">
      <div v-if="post.cover" class="post-cover">
        <img :src="post.cover" alt="文章封面" />
      </div>
      
      <div class="post-header">
        <span :class="['category-badge', 'cat-' + post.category_name]">{{ post.category_name || '其它' }}</span>
        <div class="post-tags">
          <span v-for="tag in parseTags(post.tags)" :key="tag" class="tag-item">{{ tag }}</span>
        </div>
      </div>
      
      <h1 class="post-title">{{ post.title }}</h1>
      
      <div class="post-meta">
        <div class="meta-left">
          <span class="post-author">👤 {{ post.author_name || '未知作者' }}</span>
          <span class="post-date">📅 发布于：{{ formatDate(post.created_at) }}</span>
          <span v-if="post.updated_at && post.updated_at !== post.created_at" class="update-date">
            🔄 更新于：{{ formatDate(post.updated_at) }}
          </span>
        </div>
        <div class="meta-right">
          <button 
            v-if="user"
            class="action-btn like-btn" 
            :class="{ active: post.is_liked, disabled: isAuthor }" 
            :disabled="isAuthor"
            @click="handleLike"
          >
            ❤️ {{ post.like_count }}
          </button>
          <span v-else class="action-btn like-btn disabled">
            ❤️ {{ post.like_count }}
          </span>
          <button 
            v-if="user"
            class="action-btn favorite-btn" 
            :class="{ active: post.is_favorited }" 
            @click="handleFavorite"
          >
            ⭐ {{ post.favorite_count }}
          </button>
          <span v-else class="action-btn favorite-btn disabled">
            ⭐ {{ post.favorite_count }}
          </span>
          <span class="action-btn comment-btn">💬 {{ post.comment_count }}</span>
        </div>
      </div>
      
      <div v-if="post.summary" class="post-summary">
        <p>{{ post.summary }}</p>
      </div>
      
      <div class="post-body markdown-body" v-html="renderedContent"></div>
      
      <div class="comments-section">
        <h3 class="comments-title">💬 评论区 ({{ comments.length }})</h3>
        
        <div v-if="user" class="comment-form">
          <textarea
            v-model="newComment"
            placeholder="写下你的评论..."
            rows="3"
            :disabled="isAuthor"
          ></textarea>
          <p v-if="isAuthor" class="author-note">⚠️ 作为文章作者，您不能直接发表评论，但可以回复他人评论</p>
          <button 
            class="btn btn-primary" 
            :disabled="!newComment.trim() || isAuthor"
            @click="submitComment"
          >
            发表评论
          </button>
        </div>
        <p v-else class="login-prompt">请先 <router-link to="/login">登录</router-link> 后发表评论</p>
        
        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-author">{{ comment.username }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="comment-text">{{ comment.content }}</p>
              <button v-if="user" class="reply-btn" @click="startReply(comment)">回复</button>
            </div>
            
            <div v-if="user && replyingTo === comment.id" class="reply-form">
              <textarea
                v-model="replyContent"
                placeholder="回复评论..."
                rows="2"
              ></textarea>
              <div class="reply-actions">
                <button class="btn btn-small" @click="cancelReply">取消</button>
                <button class="btn btn-primary btn-small" :disabled="!replyContent.trim()" @click="submitReply(comment)">回复</button>
              </div>
            </div>
            
            <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
              <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="comment-header">
                  <span class="comment-author">{{ reply.username }}</span>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                </div>
                <p class="comment-text">{{ reply.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="back-link">
        <router-link to="/">← 返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { postApi, commentApi } from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const newComment = ref('')
const replyingTo = ref(null)
const replyContent = ref('')

marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  const rawHtml = marked.parse(post.value.content)
  return DOMPurify.sanitize(rawHtml)
})

const isAuthor = computed(() => {
  return user.value && post.value && user.value.id === post.value.author_id
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

const parseTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(',').filter(tag => tag.trim())
}

const loadPost = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPost(route.params.id)
    post.value = response.data
    loadComments()
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = '文章不存在或已被删除'
    } else {
      error.value = '加载文章失败，请稍后重试'
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}

const loadComments = async () => {
  try {
    const response = await commentApi.getComments(route.params.id)
    comments.value = response.data
  } catch (err) {
    console.error('加载评论失败:', err)
  }
}

const handleLike = async () => {
  if (!user.value) {
    alert('请先登录')
    return
  }
  if (isAuthor.value) {
    alert('作者不能点赞自己的作品')
    return
  }
  try {
    const response = await postApi.toggleLike(post.value.id)
    post.value.is_liked = response.data.liked
    post.value.like_count = response.data.count
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
    console.error(err)
  }
}

const handleFavorite = async () => {
  if (!user.value) {
    alert('请先登录')
    return
  }
  try {
    const response = await postApi.toggleFavorite(post.value.id)
    post.value.is_favorited = response.data.favorited
    post.value.favorite_count = response.data.count
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
    console.error(err)
  }
}

const submitComment = async () => {
  try {
    await commentApi.createComment({
      post_id: post.value.id,
      content: newComment.value
    })
    newComment.value = ''
    loadComments()
  } catch (err) {
    alert(err.response?.data?.detail || '发表评论失败')
    console.error(err)
  }
}

const startReply = (comment) => {
  replyingTo.value = comment.id
  replyContent.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

const submitReply = async (parentComment) => {
  try {
    await commentApi.createComment({
      post_id: post.value.id,
      parent_id: parentComment.id,
      content: replyContent.value
    })
    cancelReply()
    loadComments()
  } catch (err) {
    alert(err.response?.data?.detail || '回复失败')
    console.error(err)
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.post-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.post-cover {
  width: 100%;
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.post-cover img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
}

.post-content {
  background: #fff;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.category-badge {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
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
  gap: 8px;
}

.tag-item {
  padding: 4px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 0.85rem;
  color: #666;
}

.post-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  line-height: 1.3;
  font-weight: 700;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.meta-left {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.meta-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.like-btn {
  background: #ffebee;
  color: #e53935;
}

.like-btn.active {
  background: #e53935;
  color: white;
}

.favorite-btn {
  background: #fff8e1;
  color: #f57c00;
}

.favorite-btn.active {
  background: #f57c00;
  color: white;
}

.comment-btn {
  background: #e3f2fd;
  color: #1976d2;
  cursor: default;
}

.action-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn:not(.disabled):not(.comment-btn):hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.post-author,
.post-date,
.update-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.post-summary {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border-left: 4px solid #667eea;
}

.post-summary p {
  margin: 0;
  color: #555;
  font-style: italic;
  line-height: 1.6;
}

.post-body {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #333;
}

:deep(.markdown-body h1) {
  font-size: 2rem;
  margin: 2rem 0 1rem;
  color: #2c3e50;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

:deep(.markdown-body h2) {
  font-size: 1.6rem;
  margin: 1.8rem 0 0.8rem;
  color: #2c3e50;
}

:deep(.markdown-body h3) {
  font-size: 1.3rem;
  margin: 1.5rem 0 0.6rem;
  color: #2c3e50;
}

:deep(.markdown-body h4),
:deep(.markdown-body h5),
:deep(.markdown-body h6) {
  font-size: 1.1rem;
  margin: 1.2rem 0 0.5rem;
  color: #2c3e50;
}

:deep(.markdown-body p) {
  margin: 1.2rem 0;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
  margin: 1.2rem 0;
  padding-left: 2rem;
}

:deep(.markdown-body li) {
  margin: 0.5rem 0;
}

:deep(.markdown-body code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  color: #e83e8c;
}

:deep(.markdown-body pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1.2rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.5rem 0;
}

:deep(.markdown-body pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 0.9rem;
}

:deep(.markdown-body blockquote) {
  border-left: 4px solid #667eea;
  margin: 1.5rem 0;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  color: #555;
  font-style: italic;
}

:deep(.markdown-body a) {
  color: #667eea;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.3s;
}

:deep(.markdown-body a:hover) {
  border-bottom-color: #667eea;
}

:deep(.markdown-body img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1.5rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

:deep(.markdown-body hr) {
  border: none;
  border-top: 2px solid #eee;
  margin: 2.5rem 0;
}

:deep(.markdown-body table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}

:deep(.markdown-body th),
:deep(.markdown-body td) {
  border: 1px solid #ddd;
  padding: 10px 14px;
  text-align: left;
}

:deep(.markdown-body th) {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

:deep(.markdown-body tr:nth-child(even)) {
  background: #f8f9fa;
}

:deep(.markdown-body strong) {
  color: #2c3e50;
  font-weight: 700;
}

:deep(.markdown-body em) {
  color: #555;
}

.comments-section {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid #eee;
}

.comments-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.comment-form textarea,
.reply-form textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1rem;
  transition: border-color 0.3s;
}

.comment-form textarea:focus,
.reply-form textarea:focus {
  outline: none;
  border-color: #667eea;
}

.comment-form textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.author-note {
  color: #e53935;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.login-prompt {
  color: #666;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.login-prompt a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.comments-list {
  margin-top: 2rem;
}

.comment-item {
  padding: 1.5rem;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.comment-author {
  font-weight: 600;
  color: #2c3e50;
}

.comment-date {
  font-size: 0.85rem;
  color: #888;
}

.comment-text {
  margin: 0;
  color: #444;
  line-height: 1.6;
}

.reply-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  padding: 0;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.reply-btn:hover {
  text-decoration: underline;
}

.reply-form {
  margin-top: 1rem;
  padding-left: 2rem;
}

.reply-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.replies-list {
  margin-top: 1rem;
  padding-left: 2rem;
  border-left: 2px solid #e0e0e0;
}

.reply-item {
  padding: 1rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.back-link {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.back-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.3s;
}

.back-link a:hover {
  color: #764ba2;
}

.loading, .error {
  text-align: center;
  padding: 4rem;
  color: #666;
  font-size: 1.1rem;
}

.error {
  color: #e74c3c;
  background: #fee;
  border-radius: 8px;
}
</style>