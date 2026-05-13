import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getCourses as getCoursesApi,
  getMyCourses as getMyCoursesApi,
  getSchedule as getScheduleApi,
  enrollCourse as enrollCourseApi,
  withdrawCourse as withdrawCourseApi
} from '../api/course'

export const useCourseStore = defineStore('course', () => {
  const courseList = ref([])
  const myCourses = ref([])
  const myCourseIds = ref(new Set())
  const schedule = ref({})
  const loading = ref(false)

  const filters = ref({
    keyword: '',
    type: '',
    teacher: ''
  })

  const filteredCourses = computed(() => {
    return courseList.value.filter((course) => {
      const matchKeyword =
        !filters.value.keyword ||
        course.name?.includes(filters.value.keyword) ||
        course.teacher?.includes(filters.value.keyword) ||
        course.description?.includes(filters.value.keyword)
      const matchType =
        !filters.value.type || course.type === filters.value.type
      const matchTeacher =
        !filters.value.teacher || course.teacher?.includes(filters.value.teacher)
      return matchKeyword && matchType && matchTeacher
    })
  })

  async function fetchCourses(params) {
    loading.value = true
    try {
      const res = await getCoursesApi(params)
      if (res.success) {
        courseList.value = (res.data || []).map(c => ({
          ...c,
          isEnrolled: myCourseIds.value.has(c.id)
        }))
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchMyCourses() {
    try {
      const res = await getMyCoursesApi()
      if (res.success) {
        myCourses.value = res.data || []
        myCourseIds.value = new Set((res.data || []).map(e => e.course_id))
        courseList.value = courseList.value.map(c => ({
          ...c,
          isEnrolled: myCourseIds.value.has(c.id)
        }))
      }
    } catch (e) {
      console.error('获取已选课程失败:', e)
    }
  }

  async function fetchSchedule() {
    try {
      const res = await getScheduleApi()
      if (res.success) {
        schedule.value = res.data || {}
      }
    } catch (e) {
      console.error('获取课表失败:', e)
    }
  }

  async function enrollCourse(courseId) {
    const res = await enrollCourseApi(courseId)
    if (res.success) {
      await fetchMyCourses()
      await fetchCourses()
    } else {
      throw new Error(res.message || '选课失败')
    }
    return res
  }

  async function withdrawCourse(courseId) {
    const res = await withdrawCourseApi(courseId)
    if (res.success) {
      await fetchMyCourses()
      await fetchCourses()
    } else {
      throw new Error(res.message || '退课失败')
    }
    return res
  }

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {
      keyword: '',
      type: '',
      teacher: ''
    }
  }

  async function fetchAll() {
    await fetchMyCourses()
    await fetchCourses()
  }

  return {
    courseList,
    myCourses,
    myCourseIds,
    schedule,
    loading,
    filters,
    filteredCourses,
    fetchCourses,
    fetchMyCourses,
    fetchSchedule,
    fetchAll,
    enrollCourse,
    withdrawCourse,
    setFilters,
    resetFilters
  }
})
