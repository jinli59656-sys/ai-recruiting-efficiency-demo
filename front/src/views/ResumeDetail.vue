<template>
  <div class="resume-detail-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/resume' }">简历管理</el-breadcrumb-item>
      <el-breadcrumb-item>简历详情</el-breadcrumb-item>
    </el-breadcrumb>

    <el-row :gutter="20">
      <el-col :span="17">
        <div class="left-panel">
          <el-card class="detail-card" shadow="never" v-loading="loading">
            <template #header>
              <div class="card-title">基本信息</div>
            </template>

            <div class="base-info">
              <el-avatar :size="80">{{ detail.candidate_name?.[0] || '简' }}</el-avatar>
              <div class="base-info__content">
                <div class="name-row">
                  <h2>{{ detail.candidate_name || '未知候选人' }}</h2>
                  <span class="position-text">{{ detail.current_position || '-' }}</span>
                </div>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="手机号">{{ maskPhone(detail.phone) }}</el-descriptions-item>
                  <el-descriptions-item label="邮箱">{{ detail.email || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="学历">{{ detail.education || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="工作年限">{{ detail.work_years ?? '-' }}{{ detail.work_years || detail.work_years === 0 ? '年' : '' }}</el-descriptions-item>
                  <el-descriptions-item label="所在城市">-</el-descriptions-item>
                  <el-descriptions-item label="关联岗位">{{ detail.position?.name || '未关联' }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">工作经历</div>
            </template>
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in detail.work_experience || []"
                :key="index"
                :timestamp="`${item.start_date || ''} - ${item.end_date || '至今'}`"
              >
                <div class="timeline-main-title">{{ item.company || '-' }}</div>
                <div class="timeline-sub-title">{{ item.position || '-' }}</div>
                <div class="timeline-desc">{{ item.description || '-' }}</div>
              </el-timeline-item>
            </el-timeline>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">项目经验</div>
            </template>
            <el-collapse>
              <el-collapse-item
                v-for="(item, index) in detail.project_experience || []"
                :key="index"
                :title="item.project_name || `项目 ${index + 1}`"
                :name="String(index)"
              >
                <p><strong>角色：</strong>{{ item.role || '-' }}</p>
                <p><strong>项目描述：</strong>{{ item.description || '-' }}</p>
              </el-collapse-item>
            </el-collapse>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">教育经历</div>
            </template>
            <div class="education-list">
              <div v-for="(item, index) in detail.education_experience || []" :key="index" class="education-item">
                <div class="timeline-main-title">{{ item.school || '-' }}</div>
                <div class="timeline-sub-title">{{ item.major || '-' }} / {{ item.degree || '-' }}</div>
                <div class="timeline-desc">{{ item.start_date || '' }} - {{ item.end_date || '' }}</div>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">技能标签</div>
            </template>
            <div class="skills-wrap">
              <el-tag v-for="skill in detail.skills || []" :key="skill" class="skill-tag">{{ skill }}</el-tag>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :span="7">
        <div class="right-panel">
          <el-card class="side-card" shadow="never">
            <template #header>
              <div class="card-title">简历状态</div>
            </template>
            <div class="status-current">
              <el-tag :type="getStatusTagType(statusForm.status)" size="large">{{ statusTextMap[statusForm.status] || detail.status_name || '未知' }}</el-tag>
            </div>
            <el-form label-position="top">
              <el-form-item label="状态变更">
                <el-select v-model="statusForm.status" style="width: 100%">
                  <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="关联岗位">
                <el-select v-model="statusForm.positionId" clearable placeholder="请选择岗位" style="width: 100%">
                  <el-option v-for="item in positionOptions" :key="item.id" :label="item.position_name" :value="item.id" />
                </el-select>
              </el-form-item>
              <el-button type="primary" style="width: 100%" :loading="saving" @click="handleSaveStatus">保存</el-button>
            </el-form>
          </el-card>

          <el-card class="side-card" shadow="never">
            <template #header>
              <div class="card-title">解析状态</div>
            </template>
            <div class="parse-status-wrap">
              <el-tag :type="getParseStatusTagType(detail.parse_status)" size="large">{{ detail.parse_status_name || parseStatusTextMap[detail.parse_status] || '未知' }}</el-tag>
              <el-button type="warning" plain :loading="reparsing" @click="handleReparse">重新解析</el-button>
            </div>
          </el-card>

          <el-card class="side-card" shadow="never">
            <template #header>
              <div class="card-title">AI 简历摘要</div>
            </template>
            <div class="summary-box">{{ detail.resume_summary || '暂无 AI 摘要' }}</div>
          </el-card>

          <el-card class="side-card" shadow="never">
            <template #header>
              <div class="card-title">快捷操作</div>
            </template>
            <div class="action-list">
              <el-button type="primary" @click="ElMessage.info('生成功能待接入')">生成面试题</el-button>
              <el-button @click="ElMessage.info('匹配功能待接入')">智能匹配岗位</el-button>
              <el-button :loading="downloading" @click="handleDownload">下载原文件</el-button>
              <el-button type="danger" @click="handleDelete">删除简历</el-button>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPositionListApi } from '@/api/position'
import {
  bindResumePositionApi,
  deleteResumeApi,
  downloadResumeApi,
  getResumeDetailApi,
  reparseResumeApi,
  updateResumeStatusApi,
} from '@/api/resume'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const downloading = ref(false)
const reparsing = ref(false)
const positionOptions = ref<any[]>([])

const detail = reactive<any>({
  candidate_name: '',
  phone: '',
  email: '',
  education: '',
  school: '',
  major: '',
  work_years: null,
  current_company: '',
  current_position: '',
  skills: [],
  work_experience: [],
  project_experience: [],
  education_experience: [],
  resume_summary: '',
  position: null,
  status: 1,
  status_name: '',
  parse_status: 0,
  parse_status_name: '',
  created_at: '',
})

const statusForm = reactive({
  status: 1,
  positionId: undefined as number | undefined,
})

const statusOptions = [
  { label: '待筛选', value: 1 },
  { label: '初筛通过', value: 2 },
  { label: '已淘汰', value: 3 },
  { label: '已录用', value: 4 },
]

const statusTextMap: Record<number, string> = {
  1: '待筛选',
  2: '初筛通过',
  3: '已淘汰',
  4: '已录用',
}

const parseStatusTextMap: Record<number, string> = {
  0: '待解析',
  1: '解析中',
  2: '已完成',
  3: '解析失败',
}

const resumeId = computed(() => Number(route.params.id || 0))

const getStatusTagType = (status: number) => {
  if (status === 1) return 'info'
  if (status === 2) return 'success'
  if (status === 3) return 'danger'
  if (status === 4) return 'success'
  return 'info'
}

const getParseStatusTagType = (status: number) => {
  if (status === 0) return 'info'
  if (status === 1) return 'warning'
  if (status === 2) return 'success'
  if (status === 3) return 'danger'
  return 'info'
}

const maskPhone = (phone?: string) => {
  if (!phone) return '-'
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await getResumeDetailApi(resumeId.value)
    const payload = res.data?.data || {}
    Object.assign(detail, payload)
    statusForm.status = payload.status || 1
    statusForm.positionId = payload.position?.id
  } finally {
    loading.value = false
  }
}

const handleSaveStatus = async () => {
  saving.value = true
  try {
    await updateResumeStatusApi(resumeId.value, statusForm.status)
    if (statusForm.positionId) {
      await bindResumePositionApi(resumeId.value, statusForm.positionId)
    }
    ElMessage.success('保存成功')
    await loadDetail()
  } finally {
    saving.value = false
  }
}

const handleDownload = async () => {
  downloading.value = true
  try {
    const res = await downloadResumeApi(resumeId.value)
    downloadBlob(res.data, `resume_${resumeId.value}.pdf`)
  } finally {
    downloading.value = false
  }
}

const handleReparse = async () => {
  reparsing.value = true
  try {
    await reparseResumeApi(resumeId.value)
    ElMessage.success('重新解析任务已提交')
    await loadDetail()
  } finally {
    reparsing.value = false
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确认删除该简历吗？', '删除确认', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })
    await deleteResumeApi(resumeId.value)
    ElMessage.success('删除成功')
    router.push('/resume')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}

onMounted(async () => {
  await loadPositions()
  await loadDetail()
})
</script>

<style scoped>
.resume-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card,
.side-card {
  border: none;
  border-radius: 12px;
}

.right-panel {
  position: sticky;
  top: 20px;
}

.card-title {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.base-info {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.base-info__content {
  flex: 1;
}

.name-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.name-row h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.position-text {
  color: #909399;
  font-size: 14px;
}

.timeline-main-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.timeline-sub-title {
  margin-top: 4px;
  color: #606266;
  font-size: 14px;
}

.timeline-desc {
  margin-top: 8px;
  color: #909399;
  line-height: 1.7;
}

.education-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.education-item {
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f2f5;
}

.education-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.skills-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  margin: 0;
}

.status-current {
  margin-bottom: 16px;
}

.parse-status-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-box {
  padding: 14px;
  border-radius: 10px;
  background: #f5f7fa;
  color: #606266;
  line-height: 1.8;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
