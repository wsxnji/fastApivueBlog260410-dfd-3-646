<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="post" class="post-content">
      <div class="post-header">
        <span :class="['category-badge', 'cat-' + post.category]">{{ post.category || '其它' }}</span>
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
      </div>
      <div v-if="post.summary" class="post-summary">
        <p>{{ post.summary }}</p>
      </div>
      <div class="post-body markdown-body" v-html="renderedContent"></div>
      <div class="back-link">
        <router-link to="/">← 返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { postApi } from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const error = ref(null)

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

// 解析标签字符串为数组
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

/* Markdown 样式 */
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
