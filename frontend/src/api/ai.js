import request from './request'
import { useUserStore } from '@/stores/user'

export function chat(data) {
  const userStore = useUserStore()
  const student_id = userStore.studentId || ''
  return request({
    url: '/api/ai/chat',
    method: 'post',
    data: { ...data, student_id }
  })
}
