<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-left">
        <span class="header-title">选课系统</span>
      </div>
      <div class="header-right">
        <span class="user-info">
          <el-icon><User /></el-icon>
          {{ userStore.username }}
        </span>
        <el-button size="small" @click="dialogVisible = true">修改密码</el-button>
        <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <div class="layout-body">
      <!-- 左侧菜单 -->
      <aside class="layout-sidebar">
        <el-menu
          :default-active="activeMenu"
          router
          style="border-right: none"
        >
          <el-menu-item index="/courses">
            <el-icon><Reading /></el-icon>
            <span>课程总览</span>
          </el-menu-item>
          <el-menu-item index="/my-courses">
            <el-icon><Notebook /></el-icon>
            <span>我的选课</span>
          </el-menu-item>
          <el-menu-item index="/schedule">
            <el-icon><Calendar /></el-icon>
            <span>课表</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <!-- 内容区域 -->
      <main class="layout-content">
        <router-view />
      </main>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="dialogVisible" title="修改密码" width="400px" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-form-item label="原密码">
          <el-input v-model="form.oldPassword" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="form.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="form.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleChangePassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- AI 助手浮窗 -->
    <AIChatBox />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Reading, Notebook, Calendar } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import AIChatBox from '@/components/AIChatBox.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const dialogVisible = ref(false)
const submitting = ref(false)

const form = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

async function handleChangePassword() {
  if (!form.value.oldPassword) {
    ElMessage.warning('请输入原密码')
    return
  }
  if (!form.value.newPassword || form.value.newPassword.length < 4) {
    ElMessage.warning('新密码长度不能少于4位')
    return
  }
  if (form.value.newPassword !== form.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  submitting.value = true
  try {
    await userStore.changePassword(form.value.oldPassword, form.value.newPassword)
    ElMessage.success('密码修改成功')
    dialogVisible.value = false
    form.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '修改失败，请检查原密码是否正确')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.layout-body {
  display: flex;
  flex: 1;
}

.layout-sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  min-height: calc(100vh - 60px);
}

.layout-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
  overflow-y: auto;
}
</style>
