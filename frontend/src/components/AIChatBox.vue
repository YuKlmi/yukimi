<template>
  <div class="ai-chat-box">
    <!-- 悬浮按钮 -->
    <el-button
      class="chat-toggle-btn"
      :icon="ChatDotSquare"
      circle
      size="large"
      type="primary"
      @click="visible = !visible"
    />

    <!-- 聊天对话框 -->
    <Transition name="chat-slide">
      <div v-if="visible" class="chat-dialog">
        <div class="chat-header">
          <span>AI 助手</span>
          <el-button
            :icon="Close"
            text
            size="small"
            @click="visible = false"
          />
        </div>

        <!-- 消息列表 -->
        <div ref="messageListRef" class="chat-messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message-item', msg.role === 'user' ? 'message-user' : 'message-ai']"
          >
            <div class="message-bubble">
              {{ msg.content }}
            </div>
          </div>
          <div v-if="loading" class="message-item message-ai">
            <div class="message-bubble message-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              思考中...
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="chat-input-area">
          <el-input
            v-model="inputText"
            placeholder="输入消息，回车发送..."
            :disabled="loading"
            @keyup.enter="handleSend"
          />
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!inputText.trim()"
            @click="handleSend"
          >
            发送
          </el-button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { ChatDotSquare, Close, Loading } from '@element-plus/icons-vue'
import { chat } from '@/api/ai'

const STORAGE_KEY = 'ai-chat-history'

const visible = ref(false)
const inputText = ref('')
const loading = ref(false)
const messageListRef = ref(null)
const messages = ref(loadHistory())

function loadHistory() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : []
  } catch {
    return []
  }
}

function saveHistory() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
}

async function scrollToBottom() {
  await nextTick()
  const el = messageListRef.value
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

watch(visible, (val) => {
  if (val) {
    scrollToBottom()
  }
})

// 消息变化时自动滚动到底部
watch(messages, scrollToBottom, { deep: true })

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  inputText.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true

  try {
    const res = await chat({ message: text })
    const reply = res.message || JSON.stringify(res)
    messages.value.push({
      role: 'assistant',
      content: reply
    })
    saveHistory()
  } catch {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我暂时无法回复，请稍后再试。'
    })
  } finally {
    loading.value = false
    saveHistory()
  }
}
</script>

<style scoped>
.ai-chat-box {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chat-toggle-btn {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.chat-dialog {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 360px;
  height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  font-size: 15px;
  background: #f5f7fa;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
}

.message-user {
  justify-content: flex-end;
}

.message-ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.message-user .message-bubble {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 2px;
}

.message-ai .message-bubble {
  background: #f0f2f5;
  color: #303133;
  border-bottom-left-radius: 2px;
}

.message-loading {
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

/* 动画 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
