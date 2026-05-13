<template>
  <div class="schedule-view">
    <div class="page-header">
      <h2>我的课表</h2>
    </div>

    <div class="schedule-grid">
      <div class="schedule-header">
        <div class="time-header">节次</div>
        <div v-for="day in dayNames" :key="day" class="day-header">{{ day }}</div>
      </div>

      <div v-for="period in periods" :key="period" class="schedule-row">
        <div class="time-cell">{{ period }}</div>
        <div
          v-for="day in dayNames"
          :key="day"
          class="course-cell"
          :class="{ 'has-course': getCourseAt(day, period) }"
          :rowspan="getRowspan(day, period)"
        >
          <div v-if="isStartOfCourse(day, period)" class="course-block">
            <el-tag
              type="success"
              effect="dark"
              class="course-tag"
            >
              <div class="course-name">{{ getCourseAt(day, period).course_name }}</div>
              <div class="course-location">{{ getCourseAt(day, period).location }}</div>
              <div class="course-teacher">{{ getCourseAt(day, period).teacher }}</div>
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!courseStore.loading && Object.keys(courseStore.schedule).length === 0" class="empty-hint">
      <el-empty description="暂无课表数据，请先选课" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()

const dayNames = ['周一', '周二', '周三', '周四', '周五']
const periods = Array.from({ length: 12 }, (_, i) => `第${i + 1}节`)

function getCourseAt(day, periodText) {
  const periodNum = parseInt(periodText.replace('第', '').replace('节', ''))
  const dayCourses = courseStore.schedule[day] || []
  return dayCourses.find(c => c.start <= periodNum && c.end >= periodNum)
}

function isStartOfCourse(day, periodText) {
  const periodNum = parseInt(periodText.replace('第', '').replace('节', ''))
  const dayCourses = courseStore.schedule[day] || []
  return dayCourses.some(c => c.start === periodNum)
}

function getRowspan(day, periodText) {
  const course = getCourseAt(day, periodText)
  if (course && isStartOfCourse(day, periodText)) {
    return course.end - course.start + 1
  }
  return 1
}

onMounted(() => {
  courseStore.fetchSchedule()
})
</script>

<style scoped>
.schedule-view {
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

.schedule-grid {
  display: grid;
  grid-template-columns: 60px repeat(5, 1fr);
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.schedule-header {
  display: contents;
}

.time-header, .day-header {
  padding: 10px;
  background: #f5f7fa;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
}

.schedule-row {
  display: contents;
}

.time-cell {
  padding: 8px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  border-right: 1px solid #e4e7ed;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.course-cell {
  padding: 2px;
  min-height: 36px;
  border-right: 1px solid #e4e7ed;
  border-bottom: 1px solid #ebeef5;
  vertical-align: top;
}

.course-cell:last-child {
  border-right: none;
}

.course-cell.has-course {
  background: #f0f9eb;
}

.course-tag {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  white-space: normal;
  line-height: 1.4;
  border: none;
}

.course-name {
  font-weight: 600;
  font-size: 13px;
}

.course-location {
  font-size: 11px;
  opacity: 0.9;
}

.course-teacher {
  font-size: 10px;
  opacity: 0.7;
}

.empty-hint {
  margin-top: 20px;
}
</style>
