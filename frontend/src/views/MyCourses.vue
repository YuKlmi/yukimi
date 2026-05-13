<template>
  <div class="my-courses">
    <div class="page-header">
      <h2>我的选课</h2>
    </div>

    <el-table
      :data="courseStore.myCourses"
      v-loading="courseStore.loading"
      stripe
      style="width: 100%"
      empty-text="暂无选课记录"
    >
      <el-table-column label="课程名称" min-width="150">
        <template #default="{ row }">
          {{ row._course?.name || '未知课程' }}
        </template>
      </el-table-column>
      <el-table-column label="教师" width="100">
        <template #default="{ row }">
          {{ row._course?.teacher || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="80">
        <template #default="{ row }">
          {{ row._course?.type || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="学分" width="70">
        <template #default="{ row }">
          {{ row._course?.credits || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="上课时间" min-width="200">
        <template #default="{ row }">
          <div v-for="(slot, idx) in (row._course?.schedule || [])" :key="idx" class="schedule-slot">
            {{ slot.day }} 第{{ slot.start }}-{{ slot.end }}节 {{ slot.location }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="enrolled_at" label="选课时间" width="170" />
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-popconfirm
            title="确定要退选该课程吗？"
            confirm-button-text="确定退课"
            cancel-button-text="取消"
            @confirm="handleWithdraw(row)"
          >
            <template #reference>
              <el-button
                type="danger"
                size="small"
                :loading="withdrawingId === row.course_id"
              >
                退课
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()
const withdrawingId = ref(null)

async function handleWithdraw(row) {
  const courseId = row.course_id
  withdrawingId.value = courseId
  try {
    const result = await courseStore.withdrawCourse(courseId)
    ElMessage.success(result.message || `退课成功：${row._course?.name || ''}`)
  } catch (e) {
    ElMessage.error(e.message || '退课失败')
  } finally {
    withdrawingId.value = null
  }
}

onMounted(() => {
  courseStore.fetchMyCourses()
})
</script>

<style scoped>
.my-courses {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.page-header h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  color: #303133;
}

.schedule-slot {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}
</style>
