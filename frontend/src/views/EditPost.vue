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
          <label>封面图片（可选）</label>
          <div class="cover-tabs">
            <button 
              type="button"
              :class="['tab-btn', { active: coverType === 'url' }]"
              @click="coverType = 'url'"
            >
              🔗 URL链接
            </button>
            <button 
              type="button"
              :class="['tab-btn', { active: coverType === 'upload' }]"
              @click="coverType = 'upload'"
            >
              📁 上传图片
            </button>
          </div>
          
          <div v-if="coverType === 'url'" class="cover-input">
            <input
              v-model="form.cover_image"
              type="url"
              placeholder="请输入封面图片URL，如：https://example.com/image.jpg"
            />
            <small class="form-help">支持 jpg、png、gif、webp 等格式的图片链接</small>
          </div>
          
          <div v-else class="cover-upload">
            <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
              <input 
                ref="fileInput"
                type="file" 
                accept="image/jpeg,image/png,image/gif,image/webp"
                @change="handleFileSelect"
                style="display: none"
              />
              <div v-if="!uploading && !form.cover_image" class="upload-placeholder">
                <span class="upload-icon">📷</span>
                <p>点击或拖拽图片到此处上传</p>
                <small>支持 JPG、PNG、GIF、WEBP 格式</small>
              </div>
              <div v-else-if="uploading" class="uploading">
                <span class="spinner"></span>
                <p>上传中...</p>
              </div>
              <div v-else class="preview-container">
                <img :src="form.cover_image" alt="封面预览" class="cover-preview" />
                <button type="button" class="remove-btn" @click.stop="removeCover">✕</button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group form-group-half">
            <label for="category">文章分类</label>
            <select id="category" v-model="form.category_id">
              <option :value="null">请选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          
          <div class="form-group form-group-half">
            <label>文章标签</label>
            <div class="tags-selector">
              <label v-for="tag in tags" :key="tag.id" class="tag-checkbox">
                <input
                  type="checkbox"
                  :value="tag.id"
                  v-model="selectedTagIds"
                />
                <span class="tag-label">{{ tag.name }}</span>
              </label>
            </div>
          </div>
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
import { postApi, categoryApi, tagApi } from '../api'
import MarkdownEditor from '../components/MarkdownEditor.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const error = ref(null)
const submitting = ref(false)
const uploading = ref(false)
const categories = ref([])
const tags = ref([])
const coverType = ref('url')
const fileInput = ref(null)
const form = ref({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  category_id: null,
  tag_ids: []
})
const selectedTagIds = ref([])

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

const loadPost = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await postApi.getPost(route.params.id)
    post.value = response.data
    form.value = {
      title: response.data.title,
      summary: response.data.summary || '',
      content: response.data.content,
      cover_image: response.data.cover_image || '',
      category_id: response.data.category?.id || null,
      tag_ids: []
    }
    selectedTagIds.value = response.data.tags?.map(t => t.id) || []
    if (form.value.cover_image) {
      coverType.value = 'upload'
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

const triggerFileInput = () => {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    uploadFile(file)
  }
}

const handleDrop = (event) => {
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    uploadFile(file)
  }
}

const uploadFile = async (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    alert('只支持 JPG、PNG、GIF、WEBP 格式的图片')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  try {
    uploading.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    const token = localStorage.getItem('token')
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    })
    
    form.value.cover_image = response.data.url
  } catch (err) {
    alert(err.response?.data?.detail || '上传失败')
    console.error(err)
  } finally {
    uploading.value = false
  }
}

const removeCover = () => {
  form.value.cover_image = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleSubmit = async () => {
  if (!form.value.content.trim()) {
    alert('请输入文章内容')
    return
  }
  
  form.value.tag_ids = selectedTagIds.value
  
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
  loadCategories()
  loadTags()
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
input[type="url"],
textarea,
select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
  font-family: inherit;
  background: white;
}

input[type="text"]:focus,
input[type="url"]:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #667eea;
}

textarea {
  resize: vertical;
}

.form-help {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #888;
}

.cover-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #e8e8e8;
}

.tab-btn.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.cover-input input {
  margin-bottom: 0;
}

.upload-area {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.upload-placeholder {
  color: #888;
}

.upload-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.upload-placeholder p {
  margin: 0.5rem 0;
  color: #555;
}

.upload-placeholder small {
  color: #aaa;
}

.uploading {
  color: #667eea;
}

.spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-container {
  position: relative;
  width: 100%;
}

.cover-preview {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group-half {
  flex: 1;
}

.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.tag-checkbox input {
  display: none;
}

.tag-label {
  padding: 6px 14px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 0.9rem;
  color: #666;
  transition: all 0.3s;
}

.tag-checkbox input:checked + .tag-label {
  background: #667eea;
  border-color: #667eea;
  color: white;
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
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
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

.btn-secondary:hover {
  background: #d0d0d0;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #666;
}

.error {
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  background: #fee;
  border-radius: 8px;
}
</style>
