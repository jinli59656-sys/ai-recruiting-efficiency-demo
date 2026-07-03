<template>
  <div class="resume-upload-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/resume' }">简历管理</el-breadcrumb-item>
      <el-breadcrumb-item>上传简历</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="upload-card" shadow="never">
      <el-upload
        ref="uploadRef"
        drag
        multiple
        :auto-upload="false"
        accept=".pdf,.docx"
        :limit="100"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">将文件拖到此处，或点击上传</div>
        <div class="upload-tip">支持 PDF、Word 格式，单个文件不超过10MB</div>
      </el-upload>

      <el-form label-width="120px" class="upload-config">
        <el-form-item label="关联岗位">
          <el-select v-model="uploadConfig.positionId" clearable placeholder="可选择关联的岗位" style="width: 320px">
            <el-option v-for="item in positionOptions" :key="item.id" :label="item.position_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="自动解析简历">
          <el-switch v-model="uploadConfig.autoParse" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="fileRows.length" class="file-card" shadow="never">
      <el-table :data="fileRows" border>
        <el-table-column prop="name" label="文件名" min-width="240" show-overflow-tooltip />
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">{{ formatFileSize(row.size) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-tag :type="getUploadStatusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress v-if="row.status === '上传中'" :percentage="row.progress" :stroke-width="14" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button v-if="row.status === '待上传'" link type="danger" @click="removeFile(row.uid)">删除</el-button>
            <el-button v-if="row.status === '失败'" link type="warning" @click="showError(row.error)">查看原因</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="footer-bar">
        <div class="summary-text" v-if="uploadFinished">
          成功 {{ summary.success }} 份，失败 {{ summary.failed }} 份
        </div>
        <div class="footer-actions">
          <el-button size="large" @click="clearList">清空列表</el-button>
          <el-button type="primary" size="large" :loading="uploading" @click="startUpload">开始上传</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadInstance, UploadFile } from 'element-plus'
import { getPositionListApi } from '@/api/position'
import { uploadResumesApi } from '@/api/resume'

const uploadRef = ref<UploadInstance>()
const positionOptions = ref<any[]>([])
const uploading = ref(false)
const uploadFinished = ref(false)

const uploadConfig = reactive({
  positionId: undefined as number | undefined,
  autoParse: true,
})

const summary = reactive({
  success: 0,
  failed: 0,
})

const fileRows = ref<any[]>([])

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const handleFileChange = (file: UploadFile) => {
  if (!file.raw) return

  const exists = fileRows.value.some((item) => item.uid === file.uid)
  if (exists) return

  fileRows.value.push({
    uid: file.uid,
    name: file.name,
    size: file.size || 0,
    raw: file.raw,
    progress: 0,
    status: '待上传',
    error: '',
  })
}

const removeFile = (uid: number | string) => {
  fileRows.value = fileRows.value.filter((item) => item.uid !== uid)
}

const formatFileSize = (size: number) => {
  if (!size) return '0KB'
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)}KB`
  return `${(size / 1024 / 1024).toFixed(1)}MB`
}

const getUploadStatusTagType = (status: string) => {
  if (status === '待上传') return 'info'
  if (status === '上传中') return 'primary'
  if (status === '解析中') return 'warning'
  if (status === '完成') return 'success'
  if (status === '失败') return 'danger'
  return 'info'
}

const showError = (message?: string) => {
  ElMessage.error(message || '上传失败')
}

const clearList = () => {
  if (uploading.value) return
  fileRows.value = []
  uploadFinished.value = false
  summary.success = 0
  summary.failed = 0
  uploadRef.value?.clearFiles()
}

const uploadSingleFile = async (row: any) => {
  const formData = new FormData()
  formData.append('files', row.raw)
  if (uploadConfig.positionId) {
    formData.append('position_id', String(uploadConfig.positionId))
  }

  row.status = '上传中'
  row.progress = 0
  row.error = ''

  try {
    const res = await uploadResumesApi(formData, {
      onUploadProgress: (event: any) => {
        if (!event.total) return
        row.progress = Math.min(100, Math.round((event.loaded / event.total) * 100))
      },
    })

    const payload = res.data?.data || {}
    const uploadResult = payload.results?.[0]

    if (uploadResult?.status === 'success') {
      row.resumeId = uploadResult.resume_id
      row.progress = 100
      row.status = uploadConfig.autoParse ? '解析中' : '完成'
      summary.success += 1
    } else {
      row.status = '失败'
      row.error = uploadResult?.error || '上传失败'
      summary.failed += 1
    }
  } catch (error: any) {
    row.status = '失败'
    row.error = error?.response?.data?.detail || '上传失败'
    summary.failed += 1
  }
}

const startUpload = async () => {
  const pendingRows = fileRows.value.filter((item) => item.status === '待上传')
  if (!pendingRows.length) {
    ElMessage.warning('没有待上传文件')
    return
  }

  uploading.value = true
  uploadFinished.value = false
  summary.success = 0
  summary.failed = 0

  try {
    for (const row of pendingRows) {
      await uploadSingleFile(row)
    }
    uploadFinished.value = true
    ElMessage.success('上传任务已完成')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  loadPositions()
})
</script>

<style scoped>
.resume-upload-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-card,
.file-card {
  border: none;
  border-radius: 12px;
}

.upload-card :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  border: 1px dashed #dcdfe6;
  border-radius: 12px;
  transition: border-color 0.2s ease;
}

.upload-card :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
}

.upload-icon {
  margin-top: 36px;
  font-size: 52px;
  color: #409eff;
}

.upload-text {
  margin-top: 12px;
  color: #303133;
  font-size: 18px;
}

.upload-tip {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.upload-config {
  margin-top: 24px;
}

.footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  gap: 16px;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.summary-text {
  color: #606266;
  font-size: 14px;
}
</style>
