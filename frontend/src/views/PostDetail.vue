<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="post" class="post-content">
      <div v-if="post.cover_image" class="post-cover">
        <img :src="post.cover_image" :alt="post.title" />
      </div>
      
      <div class="post-header">
        <span v-if="post.category" :class="['category-badge', 'cat-' + post.category.id]">{{ post.category.name }}</span>
        <div class="post-tags">
          <span v-for="tag in post.tags" :key="tag.id" class="tag-item">{{ tag.name }}</span>
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
      </div>
      
      <div v-if="post.summary" class="post-summary">
        <p>{{ post.summary }}</p>
      </div>
      
      <div class="post-body markdown-body" v-html="renderedContent"></div>
      
      <div class="post-actions">
        <button 
          @click="handleLike" 
          :class="['action-btn', 'like-btn', { active: post.is_liked }]"
          :disabled="!isLoggedIn || isAuthor"
          :title="isAuthor ? '不能点赞自己的文章' : !isLoggedIn ? '请先登录' : ''"
        >
          {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count }}
        </button>
        <button 
          @click="handleFavorite" 
          :class="['action-btn', 'favorite-btn', { active: post.is_favorited }]"
          :disabled="!isLoggedIn"
          :title="!isLoggedIn ? '请先登录' : ''"
        >
          {{ post.is_favorited ? '⭐' : '☆' }} {{ post.is_favorited ? '已收藏' : '收藏' }}
        </button>
      </div>
      
      <div class="comments-section">
        <h3 class="comments-title">💬 评论 ({{ post.comment_count }})</h3>
        
        <div v-if="isLoggedIn && !isAuthor" class="comment-form">
          <textarea 
            v-model="newComment" 
            placeholder="写下你的评论..."
            rows="3"
          ></textarea>
          <button @click="submitComment" class="btn btn-primary" :disabled="!newComment.trim() || submittingComment">
            {{ submittingComment ? '提交中...' : '发表评论' }}
          </button>
        </div>
        <div v-else-if="!isLoggedIn" class="login-tip">
          <router-link to="/login">登录</router-link> 后参与评论
        </div>
        <div v-else-if="isAuthor" class="author-tip">
          作者可以回复他人的评论，但不能直接评论自己的文章
        </div>
        
        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">👤 {{ comment.author.username }}</span>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-actions">
              <button @click="replyTo(comment)" class="reply-btn">回复</button>
            </div>
            
            <div v-if="replyingTo === comment.id" class="reply-form">
              <textarea 
                v-model="replyContent" 
                :placeholder="`回复 ${comment.author.username}...`"
                rows="2"
              ></textarea>
              <div class="reply-actions">
                <button @click="submitReply(comment.id)" class="btn btn-sm btn-primary" :disabled="!replyContent.trim() || submittingComment">
                  回复
                </button>
                <button @click="cancelReply" class="btn btn-sm btn-secondary">取消</button>
              </div>
            </div>
            
            <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
              <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="comment-header">
                  <span class="comment-author">👤 {{ reply.author.username }}</span>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="comment-content">{{ reply.content }}</div>
              </div>
            </div>
          </div>
          
          <div v-if="comments.length === 0" class="no-comments">
            暂无评论，快来抢沙发吧！
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
import { useRoute, useRouter } from 'vue-router'
import { postApi, commentApi } from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const newComment = ref('')
const replyingTo = ref(null)
const replyContent = ref('')
const submittingComment = ref(false)

marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token')
})

const currentUser = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

const isAuthor = computed(() => {
  return post.value && currentUser.value && post.value.author_id === currentUser.value.id
})

const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  const rawHtml = marked.parse(post.value.content)
  return DOMPurify.sanitize(rawHtml)
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

const loadPost = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPost(route.params.id)
    post.value = response.data
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
    console.error('加载评论失败', err)
  }
}

const handleLike = async () => {
  if (!isLoggedIn.value || isAuthor.value) return
  
  try {
    const response = await postApi.toggleLike(post.value.id)
    post.value.is_liked = response.data.liked
    post.value.like_count += response.data.liked ? 1 : -1
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  }
}

const handleFavorite = async () => {
  if (!isLoggedIn.value) return
  
  try {
    const response = await postApi.toggleFavorite(post.value.id)
    post.value.is_favorited = response.data.favorited
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    submittingComment.value = true
    await commentApi.createComment(post.value.id, { content: newComment.value })
    newComment.value = ''
    await loadComments()
    post.value.comment_count++
  } catch (err) {
    alert(err.response?.data?.detail || '评论失败')
  } finally {
    submittingComment.value = false
  }
}

const replyTo = (comment) => {
  replyingTo.value = comment.id
  replyContent.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

const submitReply = async (parentId) => {
  if (!replyContent.value.trim()) return
  
  try {
    submittingComment.value = true
    await commentApi.createComment(post.value.id, { 
      content: replyContent.value,
      parent_id: parentId 
    })
    replyContent.value = ''
    replyingTo.value = null
    await loadComments()
    post.value.comment_count++
  } catch (err) {
    alert(err.response?.data?.detail || '回复失败')
  } finally {
    submittingComment.value = false
  }
}

onMounted(() => {
  loadPost()
  loadComments()
})
</script>

<style scoped>
.post-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.post-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.post-cover {
  width: 100%;
  max-height: 400px;
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
  padding: 1.5rem 2rem 0;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.category-badge {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
}

.cat-1 { background: #e3f2fd; color: #1976d2; }
.cat-2 { background: #f3e5f5; color: #7b1fa2; }
.cat-3 { background: #e8f5e9; color: #388e3c; }
.cat-4 { background: #fff3e0; color: #f57c00; }

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
  margin: 1rem 2rem;
  line-height: 1.3;
  font-weight: 700;
}

.post-meta {
  color: #888;
  font-size: 0.9rem;
  margin: 0 2rem 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.meta-left {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
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
  margin: 0 2rem 2rem;
  border-radius: 8px;
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
  padding: 0 2rem;
}

.post-actions {
  display: flex;
  gap: 1rem;
  padding: 2rem;
  margin-top: 2rem;
  border-top: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.action-btn:hover:not(:disabled) {
  border-color: #667eea;
  background: #f8f9ff;
}

.action-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.action-btn.active {
  border-color: #667eea;
  background: #f0f3ff;
}

.comments-section {
  padding: 2rem;
  background: #f8f9fa;
}

.comments-title {
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.comment-form {
  margin-bottom: 2rem;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #555;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.login-tip, .author-tip {
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  color: #666;
}

.login-tip a {
  color: #667eea;
  font-weight: 500;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.comment-author {
  font-weight: 600;
  color: #2c3e50;
}

.comment-date {
  font-size: 0.85rem;
  color: #888;
}

.comment-content {
  color: #555;
  line-height: 1.6;
}

.comment-actions {
  margin-top: 0.5rem;
}

.reply-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
}

.reply-btn:hover {
  text-decoration: underline;
}

.reply-form {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.reply-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.reply-actions {
  display: flex;
  gap: 0.5rem;
}

.replies-list {
  margin-top: 1rem;
  padding-left: 1.5rem;
  border-left: 2px solid #e0e0e0;
}

.reply-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.no-comments {
  text-align: center;
  padding: 2rem;
  color: #888;
}

.back-link {
  padding: 2rem;
  text-align: center;
}

.back-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.back-link a:hover {
  text-decoration: underline;
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
</style>
