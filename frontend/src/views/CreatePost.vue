<template>
  <div class="create-post">
    <div class="page-header">
      <h1 class="page-title">📝 新建文章</h1>
      <router-link to="/admin" class="btn-back">← 返回管理</router-link>
    </div>
    
    <div class="form-container">
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
          <label for="cover_image">封面图片 URL（可选）</label>
          <input
            id="cover_image"
            v-model="form.cover_image"
            type="url"
            placeholder="请输入封面图片 URL"
          />
          <div v-if="form.cover_image" class="cover-preview">
            <img :src="form.cover_image" alt="封面预览" @error="handleImageError" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group form-group-half">
            <label for="category">文章分类</label>
            <select id="category" v-model="form.category_id">
              <option :value="null">请选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group form-group-half">
            <label>文章标签</label>
            <div class="tags-selector">
              <label v-for="tag in availableTags" :key="tag.id" class="tag-checkbox">
                <input
                  type="checkbox"
                  :value="tag.name"
                  v-model="selectedTags"
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
            {{ submitting ? '发布中...' : '✅ 发布文章' }}
          </button>
          <router-link to="/admin" class="btn btn-secondary">取消</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postApi, categoryApi, tagApi } from '../api'
import MarkdownEditor from '../components/MarkdownEditor.vue'

const router = useRouter()
const submitting = ref(false)
const categories = ref([])
const availableTags = ref([])
const form = ref({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  category_id: null,
  tags: ''
})

const selectedTags = ref([])

const loadCategories = async () => {
  try {
    const response = await categoryApi.getCategories()
    categories.value = response.data
  } catch (err) {
    console.error('加载分类失败:', err)
  }
}

const loadTags = async () => {
  try {
    const response = await tagApi.getTags()
    availableTags.value = response.data
  } catch (err) {
    console.error('加载标签失败:', err)
  }
}

const handleImageError = () => {
  alert('封面图片加载失败，请检查 URL 是否正确')
}

const handleSubmit = async () => {
  if (!form.value.content.trim()) {
    alert('请输入文章内容')
    return
  }

  // 将选中的标签转换为逗号分隔的字符串
  form.value.tags = selectedTags.value.join(',')

  try {
    submitting.value = true
    await postApi.createPost(form.value)
    alert('🎉 文章发布成功！')
    router.push('/admin')
  } catch (err) {
    if (err.response?.status === 401) {
      alert('请先登录')
      router.push('/login')
    } else if (err.response?.status === 403) {
      alert('权限不足')
    } else {
      alert('发布失败，请稍后重试')
    }
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.create-post {
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

.form-row {
  display: flex;
  gap: 1.5rem;
}

.form-group-half {
  flex: 1;
}

.cover-preview {
  margin-top: 1rem;
  max-width: 400px;
}

.cover-preview img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  background: #f5f5f5;
  border-radius: 20px;
  transition: all 0.2s;
}

.tag-checkbox:hover {
  background: #e8e8e8;
}

.tag-checkbox input {
  margin-right: 6px;
}

.tag-label {
  font-size: 0.9rem;
  color: #555;
}

.tag-checkbox input:checked + .tag-label {
  color: #667eea;
  font-weight: 500;
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
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.6;
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

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e8e8e8;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
