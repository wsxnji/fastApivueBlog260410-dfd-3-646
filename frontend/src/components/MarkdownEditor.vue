<template>
  <div class="markdown-editor">
    <div class="editor-tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'edit' }]" 
        @click="activeTab = 'edit'"
      >
        ✏️ 编辑
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'preview' }]" 
        @click="activeTab = 'preview'"
      >
        👁️ 预览
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'split' }]" 
        @click="activeTab = 'split'"
      >
        ↔️ 分屏
      </button>
    </div>
    
    <div class="editor-container" :class="`mode-${activeTab}`">
      <!-- 编辑区域 -->
      <div v-show="activeTab !== 'preview'" class="editor-pane">
        <textarea
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
          :placeholder="placeholder"
          class="markdown-textarea"
        ></textarea>
        <div class="editor-toolbar">
          <button @click="insertText('**', '**')" title="粗体">B</button>
          <button @click="insertText('*', '*')" title="斜体">I</button>
          <button @click="insertText('# ', '')" title="标题">H</button>
          <button @click="insertText('- ', '')" title="列表">•</button>
          <button @click="insertText('```\n', '\n```')" title="代码块">{ }</button>
          <button @click="insertText('[', '](url)')" title="链接">🔗</button>
          <button @click="insertText('![alt](', ')')" title="图片">🖼️</button>
          <button @click="insertText('> ', '')" title="引用">"</button>
          <button @click="insertText('---\n', '')" title="分割线">—</button>
        </div>
      </div>
      
      <!-- 预览区域 -->
      <div v-show="activeTab !== 'edit'" class="preview-pane">
        <div v-if="!modelValue" class="empty-preview">
          <p>📝 开始输入 Markdown 内容...</p>
        </div>
        <div v-else class="markdown-preview" v-html="renderedMarkdown"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入 Markdown 内容...'
  }
})

const emit = defineEmits(['update:modelValue'])

const activeTab = ref('split')

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

// 渲染 Markdown
const renderedMarkdown = computed(() => {
  if (!props.modelValue) return ''
  const rawHtml = marked.parse(props.modelValue)
  return DOMPurify.sanitize(rawHtml)
})

// 在光标位置插入文本
const insertText = (before, after) => {
  const textarea = document.querySelector('.markdown-textarea')
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = props.modelValue
  const beforeText = text.substring(0, start)
  const selectedText = text.substring(start, end)
  const afterText = text.substring(end)
  
  const newText = beforeText + before + selectedText + after + afterText
  emit('update:modelValue', newText)
  
  // 恢复光标位置
  setTimeout(() => {
    const newCursorPos = start + before.length + selectedText.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    textarea.focus()
  }, 0)
}
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.editor-tabs {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #e9ecef;
}

.tab-btn.active {
  background: #fff;
  color: #667eea;
  font-weight: 600;
  border-bottom: 2px solid #667eea;
}

.editor-container {
  display: flex;
  min-height: 400px;
}

.mode-edit .editor-pane,
.mode-preview .preview-pane {
  flex: 1;
}

.mode-split .editor-pane,
.mode-split .preview-pane {
  flex: 1;
  width: 50%;
}

.mode-split .editor-pane {
  border-right: 1px solid #e0e0e0;
}

.editor-pane {
  display: flex;
  flex-direction: column;
}

.markdown-textarea {
  flex: 1;
  width: 100%;
  padding: 16px;
  border: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
}

.editor-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

.editor-toolbar button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.editor-toolbar button:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.preview-pane {
  padding: 16px;
  overflow-y: auto;
  background: #fafafa;
}

.empty-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.markdown-preview {
  line-height: 1.8;
  color: #333;
}

.markdown-preview :deep(h1) {
  font-size: 2rem;
  margin: 1.5rem 0 1rem;
  color: #2c3e50;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

.markdown-preview :deep(h2) {
  font-size: 1.5rem;
  margin: 1.3rem 0 0.8rem;
  color: #2c3e50;
}

.markdown-preview :deep(h3) {
  font-size: 1.25rem;
  margin: 1.2rem 0 0.6rem;
  color: #2c3e50;
}

.markdown-preview :deep(p) {
  margin: 1rem 0;
}

.markdown-preview :deep(ul), 
.markdown-preview :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.markdown-preview :deep(li) {
  margin: 0.5rem 0;
}

.markdown-preview :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.markdown-preview :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-preview :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #667eea;
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  color: #666;
}

.markdown-preview :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.markdown-preview :deep(hr) {
  border: none;
  border-top: 2px solid #eee;
  margin: 2rem 0;
}

.markdown-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-preview :deep(th) {
  background: #f8f9fa;
  font-weight: 600;
}
</style>
