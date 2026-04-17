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
        
        <div class="form-row">
          <div class="form-group form-group-half">
            <label for="category">文章分类</label>
            <select id="category" v-model="form.category" required>
              <option value="前端">前端</option>
              <option value="后端">后端</option>
              <option value="数据库">数据库</option>
              <option value="其它">其它</option>
            </select>
          </div>
          
          <div class="form-group form-group-half">
            <label>文章标签</label>
            <div class="tags-selector">
              <label v-for="tag in availableTags" :key="tag" class="tag-checkbox">
                <input
                  type="checkbox"
                  :value="tag"
                  v-model="selectedTags"
                />
                <span class="tag-label">{{ tag }}</span>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { postApi } from '../api'
import MarkdownEditor from '../components/MarkdownEditor.vue'

const router = useRouter()
const submitting = ref(false)
const form = ref({
  title: '',
  summary: '',
  content: '',
  category: '其它',
  tags: ''
})

// 可选标签列表
const availableTags = ['JS', 'Node', 'Java', 'Python', 'Go', 'Vue', 'React']
const selectedTags = ref([])

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
  margin-bottom: 1.5rem;
}

.form-group-half {
  flex: 1;
  margin-bottom: 0;
}

.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin: 0;
}

.tag-checkbox input[type="checkbox"] {
  display: none;
}

.tag-label {
  padding: 6px 14px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 0.85rem;
  transition: all 0.3s;
  font-weight: 500;
}

.tag-checkbox input[type="checkbox"]:checked + .tag-label {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
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
</style>
