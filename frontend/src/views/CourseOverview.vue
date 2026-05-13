<template>
  <div class="course-overview">
    <div class="page-header">
      <h2>课程总览</h2>
    </div>

    <div class="filter-bar">
      <el-select
        v-model="courseStore.filters.type"
        placeholder="按类型筛选"
        clearable
        style="width: 150px"
      >
        <el-option label="必修" value="必修" />
        <el-option label="选修" value="选修" />
        <el-option label="通识" value="通识" />
      </el-select>
      <el-input
        v-model="courseStore.filters.keyword"
        placeholder="搜索课程名称/教师..."
        clearable
        style="width: 250px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <el-table
      :data="courseStore.filteredCourses"
      v-loading="courseStore.loading"
      stripe
      style="width: 100%"
      empty-text="暂无课程数据"
    >
      <el-table-column prop="name" label="课程名称" min-width="150" />
      <el-table-column prop="teacher" label="教师" width="100" />
      <el-table-column prop="type" label="类型" width="80" />
      <el-table-column prop="credits" label="学分" width="70" />
      <el-table-column label="容量/已选" width="170">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round((row.enrolled / row.capacity) * 100)"
            :status="row.enrolled >= row.capacity ? 'exception' : 'success'"
            :stroke-width="16"
            :text-inside="true"
          >
            {{ row.enrolled }}/{{ row.capacity }}
          </el-progress>
        </template>
      </el-table-column>
      <el-table-column label="上课时间" min-width="200">
        <template #default="{ row }">
          <div v-for="(slot, idx) in (row.schedule || [])" :key="idx" class="schedule-slot">
            {{ slot.day }} 第{{ slot.start }}-{{ slot.end }}节 {{ slot.location }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :disabled="row.enrolled >= row.capacity || row.isEnrolled"
            :loading="enrollingId === row.id"
            @click="handleEnroll(row)"
          >
            {{ row.isEnrolled ? '已选' : row.enrolled >= row.capacity ? '已满' : '选课' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()
const enrollingId = ref(null)

async function handleEnroll(course) {
  enrollingId.value = course.id
  try {
    const result = await courseStore.enrollCourse(course.id)
    ElMessage.success(result.message || `选课成功：${course.name}`)
  } catch (e) {
    ElMessage.error(e.message || '选课失败')
  } finally {
    enrollingId.value = null
  }
}

onMounted(() => {
  courseStore.fetchAll()
})
</script>

<style scoped>
.course-overview {
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

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.schedule-slot {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}
</style>
