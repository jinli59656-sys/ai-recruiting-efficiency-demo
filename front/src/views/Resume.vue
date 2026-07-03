<template>
  <div class="resume-page">
    <h2 class="page-title">简历管理</h2>

    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索候选人姓名"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.positionId"
            placeholder="全部岗位"
            clearable
            style="width: 180px"
          >
            <el-option label="全部岗位" value="" />
            <el-option
              v-for="item in positionOptions"
              :key="item.id"
              :label="item.position_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.education"
            placeholder="学历"
            clearable
            style="width: 140px"
          >
            <el-option label="全部" value="" />
            <el-option label="大专" value="大专" />
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <div class="year-range">
            <el-input-number v-model="searchForm.workYearsMin" :min="0" :max="50" :controls="false" style="width: 80px" />
            <span class="range-separator">-</span>
            <el-input-number v-model="searchForm.workYearsMax" :min="0" :max="50" :controls="false" style="width: 80px" />
          </div>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" value="" />
            <el-option label="待筛选" :value="1" />
            <el-option label="初筛通过" :value="2" />
            <el-option label="已淘汰" :value="3" />
            <el-option label="已录用" :value="4" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Upload" @click="router.push('/resume/upload')">上传简历</el-button>
        <el-button :icon="Download" :disabled="!selectedRows.length" @click="handleBatchDownload">批量下载</el-button>
        <el-button type="danger" :icon="Delete" :disabled="!selectedRows.length" @click="handleBatchDelete">批量删除</el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="候选人" min-width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/resume/${row.id}`)">{{ row.candidate_name || '-' }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="手机号" min-width="120">
          <template #default="{ row }">{{ maskPhone(row.phone) }}</template>
        </el-table-column>
        <el-table-column prop="education" label="学历" min-width="90" />
        <el-table-column label="工作年限" min-width="90">
          <template #default="{ row }">{{ formatYears(row.work_years) }}</template>
        </el-table-column>
        <el-table-column prop="current_company" label="当前公司" min-width="160" show-overflow-tooltip />
        <el-table-column label="关联岗位" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ positionNameMap[row.position_id] || '未关联' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ row.status_name || statusTextMap[row.status] || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="解析状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getParseStatusTagType(row.parse_status)">{{ row.parse_status_name || parseStatusTextMap[row.parse_status] || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传时间" min-width="120">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="220" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/resume/${row.id}`)">查看详情</el-button>
            <el-button link type="primary" @click="handleDownload(row.id)">下载</el-button>
            <el-button link type="warning" @click="handleReparse(row.id)">重新解析</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Download, Refresh, Search, Upload } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getPositionListApi } from '@/api/position'
import {
  batchDownloadResumeApi,
  deleteResumeApi,
  downloadResumeApi,
  getResumeListApi,
  reparseResumeApi,
} from '@/api/resume'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedRows = ref<any[]>([])
const positionOptions = ref<any[]>([])

const searchForm = reactive({
  keyword: '',
  positionId: '',
  education: '',
  workYearsMin: undefined as number | undefined,
  workYearsMax: undefined as number | undefined,
  status: '' as number | '',
})

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

const positionNameMap = computed(() => {
  return positionOptions.value.reduce((map: Record<number, string>, item: any) => {
    map[item.id] = item.position_name
    return map
  }, {})
})

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

const formatYears = (years?: number) => (years || years === 0 ? `${years}年` : '-')
const formatDate = (value?: string) => (value ? value.slice(0, 10) : '-')

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

const loadPositionOptions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const loadResumeList = async () => {
  loading.value = true
  try {
    const res = await getResumeListApi({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchForm.keyword.trim() || undefined,
      positionId: searchForm.positionId || undefined,
      education: searchForm.education || undefined,
      workYearsMin: searchForm.workYearsMin,
      workYearsMax: searchForm.workYearsMax,
      status: searchForm.status === '' ? undefined : searchForm.status,
    })

    const payload = res.data?.data || {}
    tableData.value = payload.data || []
    total.value = payload.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadResumeList()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.positionId = ''
  searchForm.education = ''
  searchForm.workYearsMin = undefined
  searchForm.workYearsMax = undefined
  searchForm.status = ''
  currentPage.value = 1
  loadResumeList()
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const handleDownload = async (id: number) => {
  const res = await downloadResumeApi(id)
  downloadBlob(res.data, `resume_${id}.pdf`)
}

const handleBatchDownload = async () => {
  if (!selectedRows.value.length) return
  const ids = selectedRows.value.map((item) => item.id)
  const res = await batchDownloadResumeApi(ids)
  downloadBlob(res.data, 'resume_batch.zip')
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该简历吗？', '删除确认', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })
    await deleteResumeApi(id)
    ElMessage.success('删除成功')
    await loadResumeList()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 份简历吗？`, '批量删除确认', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })
    await Promise.all(selectedRows.value.map((item) => deleteResumeApi(item.id)))
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    await loadResumeList()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}

const handleReparse = async (id: number) => {
  await reparseResumeApi(id)
  ElMessage.success('重新解析任务已提交')
  await loadResumeList()
}

watch([currentPage, pageSize], () => {
  loadResumeList()
})

onMounted(async () => {
  await loadPositionOptions()
  await loadResumeList()
})
</script>

<style scoped>
.resume-page {
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

.search-card,
.table-card {
  border: none;
  border-radius: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.year-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
