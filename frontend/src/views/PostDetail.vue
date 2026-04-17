<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="post" class="post-content">
      <div v-if="post.cover_image" class="post-cover">
        <img :src="post.cover_image" alt="文章封面" />
      </div>
      <div class="post-header">
        <span v-if="post.category_name" class="category-badge">{{ post.category_name }}</span>
        <div v-if="post.tags" class="post-tags">
          <router-link v-for="tag in parseTags(post.tags)" :key="tag" :to="`/tag/${tag}`" class="tag-item">{{ tag }}</router-link>
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

      <!-- 点赞和收藏按钮 -->
      <div class="post-actions-bar">
        <button
          @click="handleLike"
          :class="['action-btn', 'like-btn', { liked: post.is_liked_by_me, disabled: isAuthor }]"
          :disabled="isAuthor || likeLoading"
          :title="isAuthor ? '不能点赞自己的文章' : ''"
        >
          <span class="action-icon">❤️</span>
          <span class="action-count">{{ post.likes_count || 0 }}</span>
          <span class="action-text">{{ post.is_liked_by_me ? '已点赞' : '点赞' }}</span>
        </button>
        <button
          @click="handleFavorite"
          :class="['action-btn', 'favorite-btn', { favorited: post.is_favorited_by_me }]"
          :disabled="favoriteLoading"
        >
          <span class="action-icon">⭐</span>
          <span class="action-count">{{ post.favorites_count || 0 }}</span>
          <span class="action-text">{{ post.is_favorited_by_me ? '已收藏' : '收藏' }}</span>
        </button>
      </div>

      <div class="back-link">
        <router-link to="/">← 返回首页</router-link>
      </div>

      <!-- 评论区域 -->
      <div class="comments-section">
        <h3 class="comments-title">💬 评论 ({{ comments.length }})</h3>

        <!-- 评论表单 -->
        <div v-if="isLoggedIn" class="comment-form">
          <div v-if="replyTo" class="reply-info">
            回复 <strong>{{ replyTo.author?.username }}</strong> 的评论
            <button @click="cancelReply" class="cancel-reply">取消</button>
          </div>
          <textarea
            v-model="commentContent"
            :placeholder="replyTo ? '请输入回复内容...' : '请输入评论内容...'"
            rows="4"
            :disabled="commentLoading"
          ></textarea>
          <div class="comment-form-actions">
            <span v-if="isAuthor && !replyTo" class="author-hint">文章作者不能直接评论自己的文章，但可以回复他人评论</span>
            <button
              @click="submitComment"
              class="btn btn-primary"
              :disabled="commentLoading || !commentContent.trim() || (isAuthor && !replyTo)"
            >
              {{ commentLoading ? '提交中...' : (replyTo ? '回复' : '发表评论') }}
            </button>
          </div>
        </div>
        <div v-else class="login-hint">
          <router-link to="/login">登录</router-link> 后即可发表评论
        </div>

        <!-- 评论列表 -->
        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">👤 {{ comment.author?.username }}</span>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-actions">
              <button v-if="isLoggedIn" @click="replyComment(comment)" class="reply-btn">回复</button>
              <button v-if="canDeleteComment(comment)" @click="deleteComment(comment.id)" class="delete-btn">删除</button>
            </div>

            <!-- 回复列表 -->
            <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
              <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="comment-header">
                  <span class="comment-author">👤 {{ reply.author?.username }}</span>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="comment-content">{{ reply.content }}</div>
                <div class="comment-actions">
                  <button v-if="canDeleteComment(reply)" @click="deleteComment(reply.id)" class="delete-btn">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="comments.length === 0" class="no-comments">
          暂无评论，快来发表第一条评论吧！
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { postApi, commentApi, likeApi, favoriteApi } from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const commentContent = ref('')
const commentLoading = ref(false)
const likeLoading = ref(false)
const favoriteLoading = ref(false)
const replyTo = ref(null)

const currentUser = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const isAuthor = computed(() => currentUser.value && post.value && currentUser.value.id === post.value.author_id)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

// 渲染 Markdown 内容
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
  if (isAuthor.value) return
  likeLoading.value = true
  try {
    if (post.value.is_liked_by_me) {
      await likeApi.unlikePost(post.value.id)
      post.value.is_liked_by_me = false
      post.value.likes_count--
    } else {
      await likeApi.likePost(post.value.id)
      post.value.is_liked_by_me = true
      post.value.likes_count++
    }
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  } finally {
    likeLoading.value = false
  }
}

const handleFavorite = async () => {
  favoriteLoading.value = true
  try {
    if (post.value.is_favorited_by_me) {
      await favoriteApi.unfavoritePost(post.value.id)
      post.value.is_favorited_by_me = false
      post.value.favorites_count--
    } else {
      await favoriteApi.favoritePost(post.value.id)
      post.value.is_favorited_by_me = true
      post.value.favorites_count++
    }
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  } finally {
    favoriteLoading.value = false
  }
}

const replyComment = (comment) => {
  replyTo.value = comment
  commentContent.value = ''
}

const cancelReply = () => {
  replyTo.value = null
  commentContent.value = ''
}

const submitComment = async () => {
  if (!commentContent.value.trim()) return
  if (isAuthor.value && !replyTo.value) {
    alert('文章作者不能直接评论自己的文章')
    return
  }

  commentLoading.value = true
  try {
    await commentApi.createComment(post.value.id, {
      content: commentContent.value,
      parent_id: replyTo.value ? replyTo.value.id : null
    })
    commentContent.value = ''
    replyTo.value = null
    await loadComments()
    post.value.comments_count++
  } catch (err) {
    alert(err.response?.data?.detail || '发表评论失败')
  } finally {
    commentLoading.value = false
  }
}

const canDeleteComment = (comment) => {
  if (!currentUser.value) return false
  return currentUser.value.is_superuser || currentUser.value.id === comment.author_id
}

const deleteComment = async (commentId) => {
  if (!confirm('确定要删除这条评论吗？')) return
  try {
    await commentApi.deleteComment(commentId)
    await loadComments()
    post.value.comments_count--
  } catch (err) {
    alert(err.response?.data?.detail || '删除评论失败')
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
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.post-cover {
  width: 100%;
  height: 300px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 2rem;
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
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.category-badge {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  background: #e3f2fd;
  color: #1976d2;
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
  text-decoration: none;
  transition: all 0.2s;
}

.tag-item:hover {
  background: #e8e8e8;
  color: #667eea;
}

.post-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  line-height: 1.3;
  font-weight: 700;
}

.post-meta {
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
  font-style: italic;
  color: #555;
}

.post-summary p {
  margin: 0;
}

.post-body {
  line-height: 1.8;
  color: #333;
  font-size: 1.1rem;
}

.post-body :deep(h1),
.post-body :deep(h2),
.post-body :deep(h3),
.post-body :deep(h4) {
  color: #2c3e50;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.post-body :deep(p) {
  margin-bottom: 1.2rem;
}

.post-body :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.post-body :deep(pre) {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.5rem 0;
}

.post-body :deep(pre code) {
  background: none;
  padding: 0;
}

.post-body :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1rem;
  margin: 1.5rem 0;
  color: #666;
  font-style: italic;
}

.post-body :deep(ul),
.post-body :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.post-body :deep(li) {
  margin-bottom: 0.5rem;
}

.post-body :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.post-body :deep(a:hover) {
  text-decoration: underline;
}

.post-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 1rem 0;
}

.post-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.post-body :deep(th),
.post-body :deep(td) {
  border: 1px solid #ddd;
  padding: 0.75rem;
  text-align: left;
}

.post-body :deep(th) {
  background: #f8f9fa;
  font-weight: 600;
}

/* 点赞和收藏按钮 */
.post-actions-bar {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  padding: 1.5rem 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 24px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.action-btn:hover:not(:disabled) {
  border-color: #667eea;
  background: #f8f9ff;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.liked {
  background: #ffebee;
  border-color: #ef5350;
  color: #c62828;
}

.action-btn.favorited {
  background: #fff8e1;
  border-color: #ffc107;
  color: #f57f17;
}

.action-icon {
  font-size: 1.2rem;
}

.action-count {
  font-weight: 600;
}

.back-link {
  margin-top: 2rem;
}

.back-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.back-link a:hover {
  color: #764ba2;
}

/* 评论区域 */
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

.comment-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.reply-info {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #e3f2fd;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cancel-reply {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  text-decoration: underline;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #667eea;
}

.comment-form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.author-hint {
  color: #888;
  font-size: 0.9rem;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-hint {
  text-align: center;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 2rem;
  color: #666;
}

.login-hint a {
  color: #667eea;
  text-decoration: none;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-item {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.comment-author {
  font-weight: 600;
  color: #2c3e50;
}

.comment-date {
  color: #888;
  font-size: 0.85rem;
}

.comment-content {
  color: #333;
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.comment-actions {
  display: flex;
  gap: 1rem;
}

.reply-btn,
.delete-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: underline;
}

.delete-btn {
  color: #e74c3c;
}

.replies-list {
  margin-top: 1rem;
  padding-left: 1.5rem;
  border-left: 3px solid #ddd;
}

.reply-item {
  padding: 1rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}

.reply-item:last-child {
  margin-bottom: 0;
}

.no-comments {
  text-align: center;
  padding: 3rem;
  color: #888;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
}

.error {
  color: #e74c3c;
}
</style>
