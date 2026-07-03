<template>
  <div class="recording-page">
    <h2 class="page-title">录音管理</h2>

    <div class="toolbar">
      <el-button type="primary" :icon="Upload" @click="uploadDialogVisible = true">上传录音</el-button>
      <div class="toolbar-filters">
        <el-select v-model="filters.candidateName" clearable placeholder="全部候选人" style="width: 180px">
          <el-option v-for="item in candidateOptions" :key="item.id" :label="item.candidate_name || `简历${item.id}`" :value="item.candidate_name" />
        </el-select>
        <el-select v-model="filters.status" clearable placeholder="转写状态" style="width: 160px">
          <el-option label="全部" value="" />
          <el-option label="未转写" value="未转写" />
          <el-option label="转写中" value="转写中" />
          <el-option label="已完成" value="已完成" />
          <el-option label="失败" value="失败" />
        </el-select>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="filteredTableData" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="关联候选人" min-width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="ElMessage.info('当前后端录音列表未返回简历ID，仅显示候选人姓名')">
              {{ row.candidate_name || '-' }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="时长" width="120">
          <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
        </el-table-column>
        <el-table-column label="转写状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTranscriptTagType(row.transcript_status_name)">{{ row.transcript_status_name || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面试官" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.interviewer || '-' }}</template>
        </el-table-column>
        <el-table-column label="面试日期" min-width="120">
          <template #default="{ row }">{{ formatDate(row.interview_date) }}</template>
        </el-table-column>
        <el-table-column label="上传时间" min-width="140">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="260" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handlePlay(row)">播放</el-button>
            <el-button
              v-if="row.transcript_status_name === '未转写' || row.transcript_status_name === '失败'"
              link
              type="primary"
              @click="handleTranscribe(row.id)"
            >
              转写
            </el-button>
            <el-button
              v-if="row.transcript_status_name === '已完成' || row.transcript_status_name === '转写中'"
              link
              type="primary"
              @click="handleViewTranscript(row.id)"
            >
              查看文字稿
            </el-button>
            <el-button
              v-if="row.transcript_status_name === '已完成'"
              link
              type="primary"
              @click="handleSummary(row.id)"
            >
              摘要
            </el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[10, 20, 50]"
          :total="total"
        />
      </div>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="上传面试录音" width="520px">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :show-file-list="true"
        :limit="1"
        accept=".mp3,.wav,.m4a,.aac"
        :on-change="handleUploadFileChange"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">将文件拖到此处，或点击上传</div>
        <div class="upload-tip">支持 MP3、WAV、M4A、AAC 格式</div>
      </el-upload>

      <el-form label-position="top" class="upload-form">
        <el-form-item label="关联候选人" required>
          <el-select v-model="uploadForm.resumeId" filterable placeholder="请选择候选人" style="width: 100%">
            <el-option v-for="item in candidateOptions" :key="item.id" :label="item.candidate_name || `简历${item.id}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联岗位">
          <el-select v-model="uploadForm.positionId" clearable placeholder="请选择岗位" style="width: 100%">
            <el-option v-for="item in positionOptions" :key="item.id" :label="item.position_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="面试日期">
          <el-date-picker v-model="uploadForm.interviewDate" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="面试官">
          <el-input v-model="uploadForm.interviewer" placeholder="请输入面试官姓名" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="audioDialogVisible" title="播放录音" width="560px" @closed="handleCloseAudioDialog">
      <div class="audio-info" v-if="currentAudioInfo">
        <div><strong>候选人：</strong>{{ currentAudioInfo.candidate_name || '-' }}</div>
        <div><strong>时长：</strong>{{ formatDuration(currentAudioInfo.duration) }}</div>
        <div><strong>面试官：</strong>{{ currentAudioInfo.interviewer || '-' }}</div>
      </div>
      <audio v-if="audioUrl" class="audio-player" :src="audioUrl" controls preload="metadata"></audio>
      <template #footer>
        <el-button @click="audioDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="transcriptDialogVisible" title="文字稿" width="70%">
      <div class="transcript-header" v-if="transcriptData">
        <span>状态：{{ transcriptData.transcript_status_name }}</span>
        <span>字数：{{ transcriptData.word_count }}</span>
        <span>更新时间：{{ transcriptData.updated_at }}</span>
      </div>
      <el-input v-model="transcriptText" type="textarea" :rows="20" :readonly="!transcriptEditMode" />
      <template #footer>
        <el-button @click="transcriptDialogVisible = false">关闭</el-button>
        <el-button v-if="!transcriptEditMode" type="primary" @click="transcriptEditMode = true">编辑</el-button>
        <el-button v-else @click="transcriptEditMode = false">取消</el-button>
        <el-button v-if="transcriptEditMode" type="primary" :loading="savingTranscript" @click="handleSaveTranscript">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import type { UploadFile, UploadInstance } from 'element-plus'
import { getPositionListApi } from '@/api/position'
import { getResumeListApi } from '@/api/resume'
import {
  deleteRecordingApi,
  getRecordingListApi,
  getRecordingStreamUrl,
  getRecordingTranscriptApi,
  startTranscribeApi,
  updateRecordingTranscriptApi,
  uploadRecordingApi,
} from '@/api/recording'
import { generateSummaryApi, getSummaryApi } from '@/api/summary'

const router = useRouter()
const loading = ref(false)
const uploading = ref(false)
const transcriptDialogVisible = ref(false)
const transcriptEditMode = ref(false)
const savingTranscript = ref(false)
const audioDialogVisible = ref(false)
const uploadDialogVisible = ref(false)
const uploadRef = ref<UploadInstance>()
const tableData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const candidateOptions = ref<any[]>([])
const positionOptions = ref<any[]>([])
const currentTranscriptId = ref<number | null>(null)
const transcriptData = ref<any>(null)
const transcriptText = ref('')
const uploadFile = ref<File | null>(null)
const currentAudioInfo = ref<any>(null)
const audioUrl = ref('')

const filters = reactive({
  candidateName: '',
  status: '',
})

const uploadForm = reactive({
  resumeId: undefined as number | undefined,
  positionId: undefined as number | undefined,
  interviewDate: '',
  interviewer: '',
})

const filteredTableData = computed(() => {
  return tableData.value.filter((item) => {
    const matchCandidate = !filters.candidateName || item.candidate_name === filters.candidateName
    const matchStatus = !filters.status || item.transcript_status_name === filters.status
    return matchCandidate && matchStatus
  })
})

const loadCandidates = async () => {
  const res = await getResumeListApi({ page: 1, page_size: 100 })
  const payload = res.data?.data || {}
  candidateOptions.value = payload.data || []
}

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const loadRecordingList = async () => {
  loading.value = true
  try {
    const res = await getRecordingListApi({ page: currentPage.value, page_size: pageSize.value })
    const payload = res.data?.data || {}
    tableData.value = payload.results || []
    total.value = payload.total || 0
  } finally {
    loading.value = false
  }
}

const handleUploadFileChange = (file: UploadFile) => {
  uploadFile.value = file.raw || null
}

const handleUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请先选择录音文件')
    return
  }
  if (!uploadForm.resumeId) {
    ElMessage.warning('请选择关联候选人')
    return
  }

  const formData = new FormData()
  formData.append('file', uploadFile.value)
  formData.append('resume_id', String(uploadForm.resumeId))
  if (uploadForm.positionId) formData.append('position_id', String(uploadForm.positionId))
  if (uploadForm.interviewDate) formData.append('interview_date', uploadForm.interviewDate)
  if (uploadForm.interviewer) formData.append('interviewer', uploadForm.interviewer)

  uploading.value = true
  try {
    await uploadRecordingApi(formData)
    ElMessage.success('录音上传成功')
    uploadDialogVisible.value = false
    uploadRef.value?.clearFiles()
    uploadFile.value = null
    uploadForm.resumeId = undefined
    uploadForm.positionId = undefined
    uploadForm.interviewDate = ''
    uploadForm.interviewer = ''
    await loadRecordingList()
  } finally {
    uploading.value = false
  }
}

const handlePlay = (row: any) => {
  currentAudioInfo.value = row
  audioUrl.value = getRecordingStreamUrl(row.id)
  audioDialogVisible.value = true
}

const handleCloseAudioDialog = () => {
  audioUrl.value = ''
  currentAudioInfo.value = null
}

const handleTranscribe = async (id: number) => {
  await startTranscribeApi(id)
  ElMessage.success('开始转写成功')
  await loadRecordingList()
}

const handleViewTranscript = async (id: number) => {
  const res = await getRecordingTranscriptApi(id)
  transcriptData.value = res.data?.data || null
  transcriptText.value = transcriptData.value?.transcript || ''
  currentTranscriptId.value = id
  transcriptEditMode.value = false
  transcriptDialogVisible.value = true
}

const handleSaveTranscript = async () => {
  if (!currentTranscriptId.value) return
  savingTranscript.value = true
  try {
    const res = await updateRecordingTranscriptApi(currentTranscriptId.value, transcriptText.value)
    transcriptData.value = res.data?.data || transcriptData.value
    transcriptText.value = transcriptData.value?.transcript || transcriptText.value
    transcriptEditMode.value = false
    ElMessage.success('文字稿更新成功')
    await loadRecordingList()
  } finally {
    savingTranscript.value = false
  }
}

const handleSummary = async (recordingId: number) => {
  try {
    await getSummaryApi(recordingId)
    router.push(`/summary/${recordingId}`)
  } catch (error: any) {
    const statusCode = error?.response?.status

    if (statusCode === 404) {
      await generateSummaryApi(recordingId)
      ElMessage.success('面试摘要生成成功')
      router.push(`/summary/${recordingId}`)
      return
    }

    ElMessage.error(error?.response?.data?.message || error?.response?.data?.detail || '获取摘要失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该录音吗？', '删除确认', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })
    await deleteRecordingApi(id)
    ElMessage.success('删除成功')
    await loadRecordingList()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}

const formatDuration = (seconds?: number) => {
  if (!seconds && seconds !== 0) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map((item) => String(item).padStart(2, '0')).join(':')
}

const formatDate = (value?: string) => {
  if (!value) return '-'
  return value.slice(0, 10)
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

const getTranscriptTagType = (statusName?: string) => {
  if (statusName === '未转写') return 'info'
  if (statusName === '转写中') return 'primary'
  if (statusName === '已完成') return 'success'
  if (statusName === '失败') return 'danger'
  return 'info'
}

watch([currentPage, pageSize], () => {
  loadRecordingList()
})

onMounted(async () => {
  await loadCandidates()
  await loadPositions()
  await loadRecordingList()
})
</script>

<style scoped>
.recording-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-title {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 700;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toolbar-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.table-card,
.filter-card {
  border: none;
  border-radius: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.upload-icon {
  margin-top: 16px;
  font-size: 48px;
  color: #409eff;
}

.upload-text {
  margin-top: 10px;
  color: #303133;
  font-size: 16px;
}

.upload-tip {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.upload-form {
  margin-top: 20px;
}

.transcript-header {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  color: #606266;
  font-size: 13px;
}

.audio-info {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
  color: #606266;
  font-size: 14px;
}

.audio-player {
  width: 100%;
}
</style>
