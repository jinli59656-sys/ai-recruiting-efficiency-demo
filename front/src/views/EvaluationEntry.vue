<template>
  <div class="evaluation-entry-page">
    <h2 class="page-title">面试评价</h2>

    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索候选人姓名"
            clearable
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="candidate_name" label="候选人姓名" min-width="160" />
        <el-table-column label="手机号" min-width="140">
          <template #default="{ row }">{{ maskPhone(row.phone) }}</template>
        </el-table-column>
        <el-table-column prop="education" label="学历" min-width="100" />
        <el-table-column label="工作年限" min-width="100">
          <template #default="{ row }">{{ formatYears(row.work_years) }}</template>
        </el-table-column>
        <el-table-column prop="current_company" label="当前公司" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" width="160" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="router.push(`/evaluation/${row.id}`)">查看评价</el-button>
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
import { Refresh, Search } from '@element-plus/icons-vue'
import { getResumeListApi } from '@/api/resume'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  keyword: '',
})

const maskPhone = (phone?: string) => {
  if (!phone) return '-'
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatYears = (years?: number) => (years || years === 0 ? `${years}年` : '-')

const loadResumeList = async () => {
  loading.value = true
  try {
    const res = await getResumeListApi({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchForm.keyword.trim() || undefined,
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
  currentPage.value = 1
  loadResumeList()
}

watch([currentPage, pageSize], () => {
  loadResumeList()
})

onMounted(() => {
  loadResumeList()
})
</script>

<style scoped>
.evaluation-entry-page {
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

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
