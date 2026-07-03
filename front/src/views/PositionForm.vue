<template>
  <div class="position-form-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/position' }">岗位管理</el-breadcrumb-item>
      <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="form-card" shadow="never" v-loading="detailLoading">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
        class="position-form"
      >
        <el-form-item label="岗位名称" prop="position_name" required>
          <el-input
            v-model="form.position_name"
            placeholder="请输入岗位名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="所属部门" prop="department" required>
          <el-select v-model="form.department" placeholder="请选择部门" filterable style="width: 100%">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>

        <el-form-item label="工作地点">
          <el-input v-model="form.work_location" placeholder="请输入工作地点" />
        </el-form-item>

        <el-form-item label="招聘人数">
          <el-input-number v-model="form.headcount" :min="1" :max="100" :step="1" />
        </el-form-item>

        <el-form-item label="薪资范围">
          <div class="salary-range">
            <el-input v-model="form.salary_min" class="salary-input" placeholder="最低" />
            <span class="salary-separator">-</span>
            <el-input v-model="form.salary_max" class="salary-input" placeholder="最高" />
            <span class="salary-unit">K</span>
          </div>
        </el-form-item>

        <el-form-item label="岗位职责" prop="job_description" required>
          <el-input
            v-model="form.job_description"
            type="textarea"
            :rows="6"
            placeholder="请输入岗位职责描述"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="任职要求" prop="requirements" required>
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="6"
            placeholder="请输入任职要求"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="岗位状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">开放招聘</el-radio>
            <el-radio :value="2">暂停招聘</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createPositionApi, getPositionDetailApi, updatePositionApi } from '@/api/position'

interface PositionFormData {
  position_name: string
  department: string
  work_location: string
  headcount: number
  salary_min: string
  salary_max: string
  job_description: string
  requirements: string
  status: 1 | 2
}

interface PositionDetailResponse {
  id: number
  position_name: string
  department: string
  job_description: string
  requirements: string
  salary_range: string | null
  work_location: string | null
  headcount: number
  status: 1 | 2 | 3
}

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const detailLoading = ref(false)
const submitLoading = ref(false)

const departmentOptions = ['技术部', '产品部', '设计部', '市场部', '人力资源部', '财务部']

const form = reactive<PositionFormData>({
  position_name: '',
  department: '',
  work_location: '',
  headcount: 1,
  salary_min: '',
  salary_max: '',
  job_description: '',
  requirements: '',
  status: 1,
})

const rules: FormRules<PositionFormData> = {
  position_name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  job_description: [
    { required: true, message: '岗位职责不能少于10个字符', trigger: 'blur' },
    { min: 10, message: '岗位职责不能少于10个字符', trigger: 'blur' },
  ],
  requirements: [
    { required: true, message: '任职要求不能少于10个字符', trigger: 'blur' },
    { min: 10, message: '任职要求不能少于10个字符', trigger: 'blur' },
  ],
}

const positionId = computed(() => Number(route.params.id || 0))
const isEditMode = computed(() => Number.isFinite(positionId.value) && positionId.value > 0)
const pageTitle = computed(() => (isEditMode.value ? '编辑岗位' : '新建岗位'))

const handleCancel = () => {
  router.push('/position')
}

const fillForm = (data: PositionDetailResponse) => {
  const [salaryMin = '', salaryMaxRaw = ''] = (data.salary_range || '').split('-')
  const salaryMax = salaryMaxRaw.replace(/K$/i, '')

  form.position_name = data.position_name
  form.department = data.department
  form.work_location = data.work_location || ''
  form.headcount = data.headcount
  form.salary_min = salaryMin.replace(/K$/i, '')
  form.salary_max = salaryMax
  form.job_description = data.job_description
  form.requirements = data.requirements
  form.status = data.status === 2 ? 2 : 1
}

const getPositionDetail = async () => {
  if (!isEditMode.value) return

  detailLoading.value = true
  try {
    const res = await getPositionDetailApi(positionId.value)
    fillForm(res.data)
  } catch (_error) {
    ElMessage.error('未找到对应岗位信息')
    router.push('/position')
  } finally {
    detailLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      position_name: form.position_name.trim(),
      department: form.department,
      job_description: form.job_description.trim(),
      requirements: form.requirements.trim(),
      salary_range:
        form.salary_min && form.salary_max ? `${form.salary_min.trim()}-${form.salary_max.trim()}K` : null,
      work_location: form.work_location.trim() || null,
      headcount: form.headcount,
      status: form.status,
    }

    if (isEditMode.value) {
      await updatePositionApi(positionId.value, payload)
      ElMessage.success('岗位更新成功')
    } else {
      await createPositionApi(payload)
      ElMessage.success('岗位创建成功')
    }

    router.push('/position')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  getPositionDetail()
})
</script>

<style scoped>
.position-form-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-card {
  border: none;
  border-radius: 12px;
}

.form-card :deep(.el-card__body) {
  padding: 20px 40px;
}

.position-form {
  max-width: 800px;
  margin: 0 auto;
}

.salary-range {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.salary-input {
  width: 100px;
}

.salary-separator,
.salary-unit {
  color: #606266;
  font-size: 14px;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: center;
}

@media (max-width: 768px) {
  .form-card :deep(.el-card__body) {
    padding: 20px;
  }
}
</style>
