<template>
  <div class="character-manager">
    <div class="header">
      <h2>角色管理</h2>
      <button @click="showCreateForm = true" class="new-character-btn">
        新建角色
      </button>
    </div>

    <div class="character-list">
      <div 
        v-for="character in characters" 
        :key="character.id"
        class="character-card"
      >
        <div class="character-info">
          <h3>{{ character.name }}</h3>
          <p>{{ character.description }}</p>
          <div class="character-params">
            <span>Temperature: {{ character.temperature }}</span>
            <span>Top P: {{ character.top_p }}</span>
            <span>Top K: {{ character.top_k }}</span>
          </div>
        </div>
        <div class="character-actions">
          <button @click="editCharacter(character)" class="edit-btn">
            编辑
          </button>
          <button @click="deleteCharacter(character.id)" class="delete-btn">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 角色编辑/创建对话框 -->
    <div v-if="showCreateForm" class="dialog-overlay">
      <div class="character-dialog">
        <h3>{{ editingCharacter.id ? '编辑角色' : '新建角色' }}</h3>
        
        <div class="form-group">
          <label>对话标题</label>
          <input v-model="editingCharacter.chat_title" placeholder="输入对话标题"/>
        </div>
        
        <div class="form-group">
          <label>角色名称</label>
          <input v-model="editingCharacter.name" placeholder="输入角色名称"/>
        </div>
        
        <div class="form-group">
          <label>角色描述</label>
          <textarea v-model="editingCharacter.description" placeholder="输入角色描述"/>
        </div>
        
        <div class="param-grid">
          <div class="param-item">
            <label>Temperature</label>
            <input type="range" v-model="editingCharacter.temperature" min="0" max="2" step="0.1"/>
            <span>{{ editingCharacter.temperature }}</span>
          </div>
          <div class="param-item">
            <label>Top P</label>
            <input type="range" v-model="editingCharacter.top_p" min="0" max="1" step="0.05"/>
            <span>{{ editingCharacter.top_p }}</span>
          </div>
          <div class="param-item">
            <label>Top K</label>
            <input type="range" v-model="editingCharacter.top_k" min="1" max="100" step="1"/>
            <span>{{ editingCharacter.top_k }}</span>
          </div>
        </div>

        <div class="dialog-actions">
          <button @click="showCreateForm = false">取消</button>
          <button @click="saveCharacter" :disabled="!editingCharacter.name.trim()">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const characters = ref([])
const showCreateForm = ref(false)
const editingCharacter = ref({
  id: '',
  name: '',
  description: '',
  temperature: 0.7,
  top_p: 0.9,
  top_k: 40,
  chat_title: ''
})

// 加载角色列表
async function loadCharacters() {
  try {
    const response = await fetch('http://localhost:8000/api/characters/')
    if (!response.ok) throw new Error('Failed to load characters')
    characters.value = await response.json()
  } catch (error) {
    console.error('Error loading characters:', error)
    alert('加载角色列表失败')
  }
}

// 保存角色
async function saveCharacter() {
  try {
    const url = editingCharacter.value.id 
      ? `http://localhost:8000/api/characters/${editingCharacter.value.id}/`
      : 'http://localhost:8000/api/characters/'
    
    const method = editingCharacter.value.id ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: editingCharacter.value.name,
        description: editingCharacter.value.description,
        temperature: editingCharacter.value.temperature,
        top_p: editingCharacter.value.top_p,
        top_k: editingCharacter.value.top_k,
        chat_title: editingCharacter.value.chat_title
      })
    })
    
    if (!response.ok) throw new Error('Failed to save character')
    
    await loadCharacters()
    showCreateForm.value = false
  } catch (error) {
    console.error('Error saving character:', error)
    alert('保存角色失败')
  }
}

// 编辑角色
function editCharacter(character) {
  editingCharacter.value = { ...character }
  showCreateForm.value = true
}

// 删除角色
async function deleteCharacter(id) {
  if (confirm('确定要删除这个角色吗？')) {
    try {
      const response = await fetch(`http://localhost:8000/api/characters/${id}/`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to delete character')
      
      await loadCharacters()
    } catch (error) {
      console.error('Error deleting character:', error)
      alert('删除角色失败')
    }
  }
}

onMounted(() => {
  loadCharacters()
})
</script>

<style scoped>
.character-manager {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.new-character-btn {
  background: var(--primary-color);
  color: #111;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.character-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.character-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.character-info h3 {
  margin-top: 0;
  color: var(--primary-color);
}

.character-params {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.character-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.character-actions button {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn {
  background: var(--secondary-color);
  color: white;
  border: none;
}

.delete-btn {
  background: #ff6b6b;
  color: white;
  border: none;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.character-dialog {
  background-color: var(--bg-color);
  padding: 1.5rem;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--secondary-color);
  border-radius: 4px;
  color: var(--text-color);
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1rem 0;
}

.param-item {
  display: flex;
  flex-direction: column;
}

.param-item input[type="range"] {
  width: 100%;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.dialog-actions button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.dialog-actions button:first-child {
  background: transparent;
  border: 1px solid var(--secondary-color);
}

.dialog-actions button:last-child {
  background: var(--primary-color);
  color: #111;
  border: none;
}
</style>
