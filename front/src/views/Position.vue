<template>
  <div class="position-page">
    <h2 class="page-title">岗位管理</h2>

    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="岗位名称">
          <el-input
            v-model="searchForm.position_name"
            placeholder="请输入岗位名称"
            clearable
          />
        </el-form-item>

        <el-form-item label="部门">
          <el-select
            v-model="searchForm.department"
            placeholder="全部部门"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部"
            style="width: 160px"
          >
            <el-option label="全部" :value="''" />
            <el-option label="开放招聘" :value="1" />
            <el-option label="暂停招聘" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="handleCreate">
        新建岗位
      </el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        class="position-table"
      >
        <el-table-column prop="position_name" label="岗位名称" width="200" show-overflow-tooltip />
        <el-table-column prop="department" label="所属部门" width="120" />
        <el-table-column prop="headcount" label="招聘人数" width="100" align="center" />
        <el-table-column prop="salary_range" label="薪资范围" width="120" />
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ row.status_name || statusTextMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_at"
          label="创建时间"
          width="120"
          :formatter="formatDate"
        />
        <el-table-column label="操作" fixed="right" width="180" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
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
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Search, View } from '@element-plus/icons-vue'
import { deletePositionApi, getDepartmentOptionsApi, getPositionListApi } from '@/api/position'

interface PositionItem {
  id: number
  position_name: string
  department: string
  headcount: number
  salary_range: string
  status: number
  status_name?: string
  created_at: string
}

interface DepartmentOption {
  label: string
  value: string
}

const router = useRouter()
const loading = ref(false)
const tableData = ref<PositionItem[]>([])
const departmentOptions = ref<DepartmentOption[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const statusTextMap: Record<number, string> = {
  1: '开放招聘',
  2: '暂停招聘',
  3: '已关闭',
}

const searchForm = reactive<{
  position_name: string
  department: string
  status: number | ''
}>({
  position_name: '',
  department: '',
  status: '',
})

const getDepartmentOptions = async () => {
  const res = await getDepartmentOptionsApi()
  departmentOptions.value = res.data
}

const getPositionList = async () => {
  loading.value = true
  try {
    const res = await getPositionListApi({
      page: currentPage.value,
      page_size: pageSize.value,
      position_name: searchForm.position_name.trim() || undefined,
      department: searchForm.department || undefined,
      status: searchForm.status === '' ? undefined : searchForm.status,
    })
    tableData.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getPositionList()
}

const handleReset = () => {
  searchForm.position_name = ''
  searchForm.department = ''
  searchForm.status = ''
  currentPage.value = 1
  getPositionList()
}

const handleCreate = () => {
  router.push('/position/create')
}

const handleView = (row: PositionItem) => {
  router.push(`/position/${row.id}`)
}

const handleEdit = (row: PositionItem) => {
  router.push(`/position/${row.id}/edit`)
}

const handleDelete = async (row: PositionItem) => {
  try {
    await ElMessageBox.confirm(`确认删除岗位“${row.position_name}”吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })

    await deletePositionApi(row.id)
    ElMessage.success('删除成功')
    await getPositionList()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}

const getStatusTagType = (status: number) => {
  if (status === 1) return 'success'
  if (status === 2) return 'warning'
  return 'info'
}

const formatDate = (_row: PositionItem, _column: unknown, value: string) => value.slice(0, 10)

watch([currentPage, pageSize], () => {
  getPositionList()
})

onMounted(async () => {
  await getDepartmentOptions()
  await getPositionList()
})
</script>

<style scoped>
.position-page {
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
  justify-content: flex-end;
}

.position-table :deep(.el-table__row:hover > td) {
  background-color: #f5faff !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
