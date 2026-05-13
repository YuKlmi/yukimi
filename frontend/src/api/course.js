import request from './request'
import { useUserStore } from '@/stores/user'

function getStudentId() {
  const userStore = useUserStore()
  return userStore.user?.id || ''
}

export function getCourses(params) {
  return request({
    url: '/api/courses',
    method: 'get',
    params
  })
}

export function getCourseDetail(id) {
  return request({
    url: `/api/courses/${id}`,
    method: 'get'
  })
}

export function enrollCourse(courseId) {
  const student_id = getStudentId()
  return request({
    url: '/api/enrollments',
    method: 'post',
    data: { student_id, course_id: courseId }
  })
}

export function withdrawCourse(courseId) {
  const student_id = getStudentId()
  return request({
    url: `/api/enrollments/${courseId}`,
    method: 'delete',
    params: { student_id }
  })
}

export function getMyCourses() {
  const student_id = getStudentId()
  return request({
    url: '/api/enrollments',
    method: 'get',
    params: { student_id }
  })
}

export function getSchedule() {
  const student_id = getStudentId()
  return request({
    url: '/api/enrollments/schedule',
    method: 'get',
    params: { student_id }
  })
}
