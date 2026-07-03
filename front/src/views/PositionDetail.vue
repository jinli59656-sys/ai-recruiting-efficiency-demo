<template>
  <div class="position-detail-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/position' }">岗位管理</el-breadcrumb-item>
      <el-breadcrumb-item>岗位详情</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="detail-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="detail-header">
          <div>
            <h2 class="page-title">{{ detail.position_name || '岗位详情' }}</h2>
            <p class="page-subtitle">{{ detail.department || '未设置部门' }}</p>
          </div>
          <div class="header-actions">
            <el-button @click="handleBack">返回列表</el-button>
            <el-button type="primary" @click="handleEdit">编辑岗位</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="岗位名称">{{ detail.position_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属部门">{{ detail.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工作地点">{{ detail.work_location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="招聘人数">{{ detail.headcount ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="薪资范围">{{ detail.salary_range || '-' }}</el-descriptions-item>
        <el-descriptions-item label="岗位状态">
          <el-tag :type="getStatusTagType(detail.status)">
            {{ detail.status_name || statusTextMap[detail.status] || '-' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDateTime(detail.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="岗位职责" :span="2">
          <div class="long-text">{{ detail.job_description || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="任职要求" :span="2">
          <div class="long-text">{{ detail.requirements || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPositionDetailApi } from '@/api/position'

interface PositionDetail {
  id?: number
  position_name: string
  department: string
  job_description: string
  requirements: string
  salary_range: string | null
  work_location: string | null
  headcount: number | null
  status: number
  status_name: string
  created_at: string
  updated_at: string
}

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const positionId = computed(() => Number(route.params.id || 0))

const detail = reactive<PositionDetail>({
  position_name: '',
  department: '',
  job_description: '',
  requirements: '',
  salary_range: null,
  work_location: null,
  headcount: null,
  status: 1,
  status_name: '',
  created_at: '',
  updated_at: '',
})

const statusTextMap: Record<number, string> = {
  1: '开放招聘',
  2: '暂停招聘',
  3: '已关闭',
}

const getStatusTagType = (status: number) => {
  if (status === 1) return 'success'
  if (status === 2) return 'warning'
  return 'info'
}

const formatDateTime = (value: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

const loadDetail = async () => {
  if (!positionId.value) {
    ElMessage.error('岗位ID无效')
    router.push('/position')
    return
  }

  loading.value = true
  try {
    const res = await getPositionDetailApi(positionId.value)
    Object.assign(detail, res.data)
  } catch (_error) {
    ElMessage.error('获取岗位详情失败')
    router.push('/position')
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.push('/position')
}

const handleEdit = () => {
  router.push(`/position/${positionId.value}/edit`)
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.position-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card {
  border: none;
  border-radius: 12px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-title {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 700;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.long-text {
  white-space: pre-wrap;
  line-height: 1.8;
}

@media (max-width: 768px) {
  .detail-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
