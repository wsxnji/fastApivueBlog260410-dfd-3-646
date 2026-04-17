<template>
  <div class="edit-post">
    <div class="page-header">
      <h1 class="page-title">✏️ 编辑文章</h1>
      <router-link to="/admin" class="btn-back">← 返回管理</router-link>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="post" class="form-container">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">文章标题</label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            placeholder="请输入文章标题"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="summary">文章摘要</label>
          <textarea
            id="summary"
            v-model="form.summary"
            placeholder="请输入文章摘要（可选，用于列表展示）"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>文章内容 (Markdown)</label>
          <MarkdownEditor v-model="form.content" placeholder="请输入文章内容，支持 Markdown 格式..." />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '保存中...' : '💾 保存修改' }}
          </button>
          <router-link to="/admin" class="btn btn-secondary">取消</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '../api'
import MarkdownEditor from '../components/MarkdownEditor.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const error = ref(null)
const submitting = ref(false)
const form = ref({
  title: '',
  summary: '',
  content: ''
})

const loadPost = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPost(route.params.id)
    post.value = response.data
    form.value = {
      title: response.data.title,
      summary: response.data.summary || '',
      content: response.data.content
    }
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = '文章不存在'
    } else {
      error.value = '加载文章失败'
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.content.trim()) {
    alert('请输入文章内容')
    return
  }
  
  try {
    submitting.value = true
    await postApi.updatePost(route.params.id, form.value)
    alert('🎉 文章更新成功！')
    router.push('/admin')
  } catch (err) {
    if (err.response?.status === 401) {
      alert('请先登录')
      router.push('/login')
    } else if (err.response?.status === 403) {
      alert('权限不足，只能编辑自己的文章')
    } else if (err.response?.status === 404) {
      alert('文章不存在')
    } else {
      alert('更新失败，请稍后重试')
    }
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.edit-post {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
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
  font-size: 1.8rem;
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

.form-container {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
  font-family: inherit;
}

input[type="text"]:focus,
textarea:focus {
  outline: none;
  border-color: #667eea;
}

textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
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
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #e74c3c;
}
</style>
