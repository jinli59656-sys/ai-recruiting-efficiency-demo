<template>
  <div class="summary-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/recording' }">录音管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试摘要</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="info-card" shadow="never" v-loading="loading">
      <div class="info-header">
        <div>
          <h2 class="candidate-name">{{ headerInfo.candidateName || '候选人' }}</h2>
          <el-tag type="primary">{{ headerInfo.positionName || '岗位待定' }}</el-tag>
        </div>
        <div class="header-meta">
          <div>面试日期：{{ headerInfo.interviewDate || '-' }}</div>
          <div>面试时长：{{ headerInfo.durationText || '-' }}</div>
        </div>
      </div>
    </el-card>

    <div class="content-area">
      <div class="main-panel">
        <el-card class="summary-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>面试概要</span>
              <el-button link type="primary" @click="toggleEdit('summary_overview')">{{ editStates.summary_overview ? '取消' : '编辑' }}</el-button>
            </div>
          </template>
          <div v-if="!editStates.summary_overview" class="summary-text-box">{{ summaryData.summary_overview || '-' }}</div>
          <el-input v-else v-model="editForm.summary_overview" type="textarea" :rows="6" />
        </el-card>

        <el-card class="summary-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>核心问答</span>
            </div>
          </template>
          <el-collapse>
            <el-collapse-item
              v-for="(item, index) in summaryData.key_qa || []"
              :key="index"
              :title="item.question"
              :name="String(index)"
            >
              <div class="qa-content">
                <div class="qa-answer">A：{{ item.answer_summary }}</div>
                <el-tag :type="getQualityTagType(item.answer_quality)">{{ item.answer_quality }}</el-tag>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <el-card class="summary-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>能力标签</span>
            </div>
          </template>
          <div class="tag-section">
            <div class="tag-title">技术能力</div>
            <div class="tag-list">
              <el-tag v-for="item in summaryData.technical_skills || []" :key="item" type="primary">{{ item }}</el-tag>
            </div>
          </div>
          <div class="tag-section">
            <div class="tag-title">软技能</div>
            <div class="tag-list">
              <el-tag v-for="item in summaryData.soft_skills || []" :key="item" type="success">{{ item }}</el-tag>
            </div>
          </div>
        </el-card>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-card class="summary-card" shadow="never">
              <template #header>
                <div class="card-header"><span>亮点</span></div>
              </template>
              <ul class="summary-list success-list">
                <li v-for="item in summaryData.highlights || []" :key="item">{{ item }}</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="summary-card" shadow="never">
              <template #header>
                <div class="card-header"><span>疑虑点</span></div>
              </template>
              <ul class="summary-list warning-list">
                <li v-for="item in summaryData.concerns || []" :key="item">{{ item }}</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="summary-card" shadow="never">
          <template #header>
            <div class="card-header"><span>候选人提问</span></div>
          </template>
          <div v-if="summaryData.candidate_questions?.length" class="summary-list plain-list">
            <div v-for="item in summaryData.candidate_questions" :key="item">{{ item }}</div>
          </div>
          <el-empty v-else description="候选人未提问" />
        </el-card>
      </div>

      <div class="action-panel">
        <el-card class="floating-card" shadow="never">
          <div class="action-list">
            <el-button type="primary" :loading="regenerating" @click="handleRegenerate">重新生成摘要</el-button>
            <el-button :loading="generatingEvaluation" @click="handleGenerateEvaluation">生成评价</el-button>
            <el-button @click="router.push('/recording')">返回录音</el-button>
          </div>
        </el-card>
      </div>
    </div>

    <div v-if="hasEditing" class="bottom-action-bar">
      <el-card shadow="never">
        <div class="bottom-actions">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getRecordingDetailApi } from '@/api/recording'
import { generateSummaryApi, getSummaryApi, regenerateSummaryApi, updateSummaryApi } from '@/api/summary'
import { generateEvaluationApi } from '@/api/evaluation'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const regenerating = ref(false)
const generatingEvaluation = ref(false)

const summaryData = reactive<any>({
  id: 0,
  recording_id: 0,
  resume_id: 0,
  summary_overview: '',
  key_qa: [],
  technical_skills: [],
  soft_skills: [],
  highlights: [],
  concerns: [],
  candidate_questions: [],
})

const headerInfo = reactive({
  candidateName: '',
  positionName: '',
  interviewDate: '',
  durationText: '',
})

const editStates = reactive({
  summary_overview: false,
})

const editForm = reactive({
  summary_overview: '',
})

const recordingId = computed(() => Number(route.params.recordingId || 0))
const hasEditing = computed(() => Object.values(editStates).some(Boolean))

const getQualityTagType = (quality: string) => {
  if (quality === '优秀') return 'success'
  if (quality === '良好') return 'primary'
  if (quality === '一般') return 'info'
  if (quality === '较差') return 'danger'
  return 'info'
}

const formatDuration = (seconds?: number) => {
  if (!seconds && seconds !== 0) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map((item) => String(item).padStart(2, '0')).join(':')
}

const loadRecordingDetail = async () => {
  const res = await getRecordingDetailApi(recordingId.value)
  const payload = res.data?.data || {}
  headerInfo.candidateName = payload.candidate_name || ''
  headerInfo.interviewDate = payload.interview_date || '-'
  headerInfo.durationText = formatDuration(payload.duration)
}

const loadSummary = async () => {
  loading.value = true
  try {
    const res = await getSummaryApi(recordingId.value)
    const payload = res.data?.data || {}
    Object.assign(summaryData, payload)
    editForm.summary_overview = payload.summary_overview || ''
  } catch (error: any) {
    if (error?.response?.status === 404) {
      await generateSummaryApi(recordingId.value)
      const res = await getSummaryApi(recordingId.value)
      const payload = res.data?.data || {}
      Object.assign(summaryData, payload)
      editForm.summary_overview = payload.summary_overview || ''
      return
    }
    throw error
  } finally {
    loading.value = false
  }
}

const toggleEdit = (field: 'summary_overview') => {
  editStates[field] = !editStates[field]
  if (editStates[field]) {
    editForm.summary_overview = summaryData.summary_overview || ''
  }
}

const cancelEdit = () => {
  editStates.summary_overview = false
  editForm.summary_overview = summaryData.summary_overview || ''
}

const handleSave = async () => {
  saving.value = true
  try {
    const res = await updateSummaryApi(summaryData.id, {
      summaryOverview: editForm.summary_overview,
    })
    const payload = res.data?.data || {}
    Object.assign(summaryData, payload)
    editForm.summary_overview = payload.summary_overview || ''
    editStates.summary_overview = false
    ElMessage.success('摘要保存成功')
  } finally {
    saving.value = false
  }
}

const handleRegenerate = async () => {
  regenerating.value = true
  try {
    const res = await regenerateSummaryApi(summaryData.id)
    const payload = res.data?.data || {}
    Object.assign(summaryData, payload)
    editForm.summary_overview = payload.summary_overview || ''
    ElMessage.success('摘要重新生成成功')
  } finally {
    regenerating.value = false
  }
}

const handleGenerateEvaluation = async () => {
  if (!summaryData.id || !summaryData.resume_id) {
    ElMessage.warning('当前摘要信息不完整，无法生成评价')
    return
  }

  generatingEvaluation.value = true
  try {
    await generateEvaluationApi(summaryData.id)
    ElMessage.success('面试评价生成成功')
    router.push(`/evaluation/${summaryData.resume_id}`)
  } finally {
    generatingEvaluation.value = false
  }
}

onMounted(async () => {
  await loadRecordingDetail()
  await loadSummary()
})
</script>

<style scoped>
.summary-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card,
.summary-card,
.floating-card {
  border: none;
  border-radius: 12px;
}

.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.candidate-name {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.header-meta {
  color: #606266;
  font-size: 14px;
  text-align: right;
  line-height: 1.8;
}

.content-area {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-panel {
  width: 260px;
}

.floating-card {
  position: sticky;
  top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.summary-text-box {
  padding: 16px;
  border-radius: 10px;
  background: #f5f7fa;
  color: #606266;
  line-height: 1.9;
}

.qa-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.qa-answer {
  color: #606266;
  line-height: 1.8;
}

.tag-section {
  margin-bottom: 16px;
}

.tag-section:last-child {
  margin-bottom: 0;
}

.tag-title {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
  font-weight: 700;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-list {
  margin: 0;
  padding-left: 20px;
  line-height: 1.9;
}

.success-list li {
  color: #67c23a;
}

.warning-list li {
  color: #e6a23c;
}

.plain-list {
  color: #606266;
  line-height: 1.9;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bottom-action-bar {
  position: sticky;
  bottom: 0;
}

.bottom-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 992px) {
  .content-area {
    flex-direction: column;
  }

  .action-panel {
    width: 100%;
  }
}
</style>
