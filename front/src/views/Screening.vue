<template>
  <div class="screening-page">
    <h2 class="page-title">智能简历筛选</h2>

    <el-row :gutter="20">
      <el-col :span="8">
        <div class="left-panel">
          <el-card class="filter-card" shadow="never">
            <template #header>
              <div class="card-title">岗位选择</div>
            </template>
            <el-form label-position="top">
              <el-form-item required label="目标岗位">
                <el-select
                  v-model="form.positionId"
                  filterable
                  placeholder="请选择目标岗位"
                  style="width: 100%"
                  @change="handlePositionChange"
                >
                  <el-option
                    v-for="item in positionOptions"
                    :key="item.id"
                    :label="item.position_name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-form>
            <div v-if="selectedPosition" class="jd-summary">
              <div class="summary-title">JD 摘要</div>
              <div class="summary-text">{{ jdSummary }}</div>
            </div>
          </el-card>

          <el-card class="filter-card" shadow="never">
            <template #header>
              <div class="card-title">筛选数量</div>
            </template>
            <el-slider v-model="form.topN" :min="5" :max="50" :step="5" show-input />
          </el-card>

          <el-card class="filter-card" shadow="never">
            <template #header>
              <div class="card-title">附加条件</div>
            </template>
            <el-collapse>
              <el-collapse-item title="展开筛选条件" name="extra">
                <el-form label-position="top">
                  <el-form-item label="最低学历">
                    <el-select v-model="form.minEducation" clearable placeholder="不限" style="width: 100%">
                      <el-option label="大专" value="大专" />
                      <el-option label="本科" value="本科" />
                      <el-option label="硕士" value="硕士" />
                      <el-option label="博士" value="博士" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="最少工作年限">
                    <el-input-number v-model="form.minWorkYears" :min="0" :max="30" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="必须技能">
                    <el-select
                      v-model="form.requiredSkills"
                      multiple
                      filterable
                      allow-create
                      default-first-option
                      placeholder="输入并回车添加技能"
                      style="width: 100%"
                    >
                      <el-option v-for="item in skillOptions" :key="item" :label="item" :value="item" />
                    </el-select>
                  </el-form-item>
                </el-form>
              </el-collapse-item>
            </el-collapse>
          </el-card>

          <el-card class="filter-card" shadow="never">
            <template #header>
              <div class="card-title">自定义要求</div>
            </template>
            <el-input
              v-model="form.customQuery"
              type="textarea"
              :rows="3"
              placeholder="输入额外筛选要求，如：有电商行业经验优先"
            />
          </el-card>

          <el-button type="primary" size="large" class="start-btn" :loading="loading" @click="handleScreening">
            开始筛选
          </el-button>
        </div>
      </el-col>

      <el-col :span="16">
        <el-card class="result-card" shadow="never">
          <template #header>
            <div class="result-header">
              <span class="card-title">筛选结果</span>
            </div>
          </template>

          <el-skeleton v-if="loading" :rows="8" animated />

          <template v-else>
            <el-alert
              v-if="screened"
              type="info"
              :closable="false"
              class="result-alert"
              :title="`共匹配到 ${matchedCount} 份简历`"
            />

            <el-empty v-if="!screened" description="请选择岗位并点击开始筛选" />
            <el-empty v-else-if="!results.length" description="未找到匹配的简历" />

            <div v-else class="result-list">
              <el-card v-for="(item, index) in results" :key="`${item.resume_id}-${index}`" class="candidate-card" shadow="hover">
                <div class="candidate-card__top">
                  <div class="candidate-main">
                    <div class="candidate-name-row">
                      <span class="candidate-name">{{ item.candidate_name }}</span>
                      <el-tag :type="getRecommendationTagType(item.recommendation)">{{ item.recommendation }}</el-tag>
                    </div>
                    <div class="candidate-meta">
                      {{ item.education || '学历未知' }}
                      <span class="divider">|</span>
                      {{ item.work_years || 0 }}年经验
                      <span class="divider">|</span>
                      {{ item.current_position || '当前职位未知' }}
                    </div>
                  </div>
                  <div class="candidate-score">
                    <el-progress
                      type="circle"
                      :width="60"
                      :percentage="item.match_score"
                      :color="getScoreColor(item.match_score)"
                    />
                  </div>
                </div>

                <el-collapse @change="(activeName) => handleLoadAnalysis(activeName, item.resume_id)">
                  <el-collapse-item title="查看匹配分析" :name="String(item.resume_id)">
                    <div v-if="analysisLoadingMap[item.resume_id]" class="analysis-loading">
                      <el-skeleton :rows="4" animated />
                    </div>
                    <template v-else>
                    <div class="tag-block">
                      <div class="block-title">匹配优势</div>
                      <div class="tag-list">
                        <el-tag
                          v-for="advantage in analysisMap[item.resume_id]?.match_advantages || []"
                          :key="advantage"
                          type="success"
                        >
                          {{ advantage }}
                        </el-tag>
                      </div>
                    </div>

                    <div class="tag-block">
                      <div class="block-title">匹配短板</div>
                      <div class="tag-list">
                        <el-tag
                          v-for="weakness in analysisMap[item.resume_id]?.match_weaknesses || []"
                          :key="weakness"
                          type="warning"
                        >
                          {{ weakness }}
                        </el-tag>
                      </div>
                    </div>

                    <div class="comment-block">
                      <div class="block-title">AI 综合评语</div>
                      <p>{{ analysisMap[item.resume_id]?.overall_comment || '暂无评语' }}</p>
                    </div>
                    <div v-if="!analysisMap[item.resume_id]" class="analysis-placeholder">
                      点击展开后加载详细匹配分析
                    </div>
                    </template>
                  </el-collapse-item>
                </el-collapse>

                <div class="action-group">
                  <el-button-group>
                    <el-button @click="router.push(`/resume/${item.resume_id}`)">查看详情</el-button>
                    <el-button @click="router.push('/question')">生成面试题</el-button>
                    <el-button type="success" @click="handleMark(item.resume_id, 4)">标记通过</el-button>
                    <el-button type="danger" @click="handleMark(item.resume_id, 3)">标记不通过</el-button>
                  </el-button-group>
                </div>
              </el-card>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getPositionListApi } from '@/api/position'
import { batchMarkResumeApi, getPositionAnalysisApi, positionMatchApi } from '@/api/screening'

const router = useRouter()
const loading = ref(false)
const screened = ref(false)
const positionOptions = ref<any[]>([])
const results = ref<any[]>([])
const matchedCount = ref(0)
const analysisMap = reactive<Record<number, any>>({})
const analysisLoadingMap = reactive<Record<number, boolean>>({})

const form = reactive({
  positionId: undefined as number | undefined,
  topN: 10,
  minEducation: '',
  minWorkYears: 0,
  requiredSkills: [] as string[],
  customQuery: '',
})

const skillOptions = ['Java', 'Spring Cloud', 'MySQL', 'Redis', 'Kafka', 'Vue', 'Python']

const selectedPosition = computed(() =>
  positionOptions.value.find((item) => item.id === form.positionId)
)

const jdSummary = computed(() => {
  const text = selectedPosition.value?.job_description || ''
  if (!text) return '暂无岗位说明'
  return text.length > 200 ? `${text.slice(0, 200)}...` : text
})

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const normalizeScreeningResponse = (responseData: any) => {
  const payload =
    responseData?.data?.data ??
    responseData?.data ??
    responseData ??
    {}

  const rawResults =
    payload.results ??
    payload.data?.results ??
    []

  const results = Array.isArray(rawResults)
    ? rawResults.map((item) => ({
        resume_id: item.resume_id ?? item.resumeId ?? null,
        candidate_name: item.candidate_name ?? item.candidateName ?? '未知候选人',
        education: item.education ?? '',
        work_years: item.work_years ?? item.workYears ?? 0,
        current_position: item.current_position ?? item.currentPosition ?? '',
        match_score: Number(item.match_score ?? item.matchScore ?? 0),
        similarity: Number(item.similarity ?? 0),
        recommendation: item.recommendation ?? '一般',
        match_analysis: item.match_analysis ?? item.matchAnalysis ?? {
          match_advantages: [],
          match_weaknesses: [],
          overall_comment: '',
          interview_suggestions: [],
        },
      }))
    : []

  const totalMatched = Number(payload.total_matched ?? payload.totalMatched ?? results.length) || results.length

  return {
    results,
    totalMatched,
  }
}

const handlePositionChange = () => {
  results.value = []
  screened.value = false
  Object.keys(analysisMap).forEach((key) => delete analysisMap[Number(key)])
  Object.keys(analysisLoadingMap).forEach((key) => delete analysisLoadingMap[Number(key)])
}

const handleScreening = async () => {
  if (!form.positionId) {
    ElMessage.warning('请先选择目标岗位')
    return
  }

  loading.value = true
  screened.value = true

  try {
    const res = await positionMatchApi({
      positionId: form.positionId,
      topN: form.topN,
      minEducation: form.minEducation || undefined,
      minWorkYears: form.minWorkYears > 0 ? form.minWorkYears : undefined,
      requiredSkills: form.requiredSkills.length ? form.requiredSkills : undefined,
    })

    const normalized = normalizeScreeningResponse(res.data)
    results.value = normalized.results
    matchedCount.value = normalized.totalMatched
    Object.keys(analysisMap).forEach((key) => delete analysisMap[Number(key)])
    Object.keys(analysisLoadingMap).forEach((key) => delete analysisLoadingMap[Number(key)])

    if (!results.value.length) {
      ElMessage.info('当前条件下未找到匹配简历')
    }
  } catch (error: any) {
    results.value = []
    matchedCount.value = 0
    console.error('智能筛选失败原始错误：', error)
    console.error('智能筛选失败响应数据：', error?.response?.data)
    ElMessage.error(
      error?.code === 'ECONNABORTED'
        ? '智能筛选耗时较长，请稍后重试'
        :
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      '智能筛选失败，请稍后重试'
    )
  } finally {
    loading.value = false
  }
}

const handleLoadAnalysis = async (activeName: string | string[], resumeId: number) => {
  const isOpen = Array.isArray(activeName)
    ? activeName.includes(String(resumeId))
    : activeName === String(resumeId)

  if (!isOpen || analysisMap[resumeId] || analysisLoadingMap[resumeId] || !form.positionId) {
    return
  }

  analysisLoadingMap[resumeId] = true

  try {
    const res = await getPositionAnalysisApi(resumeId, form.positionId)
    const payload = res.data?.data || {}
    analysisMap[resumeId] = payload.result || null
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || error?.response?.data?.detail || '加载匹配分析失败')
  } finally {
    analysisLoadingMap[resumeId] = false
  }
}

const handleMark = async (resumeId: number, mark: number) => {
  await batchMarkResumeApi([resumeId], mark)
  ElMessage.success(mark === 4 ? '已标记通过' : '已标记不通过')
}

const getScoreColor = (score: number) => {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 60) return '#909399'
  return '#F56C6C'
}

const getRecommendationTagType = (recommendation: string) => {
  if (recommendation.includes('强烈')) return 'success'
  if (recommendation.includes('推荐')) return 'primary'
  return 'info'
}

onMounted(() => {
  loadPositions()
})
</script>

<style scoped>
.screening-page {
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

.left-panel,
.result-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card,
.result-card {
  border: none;
  border-radius: 12px;
}

.card-title {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.jd-summary {
  margin-top: 12px;
  padding: 12px;
  border-radius: 10px;
  background: #f5f7fa;
}

.summary-title {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
  font-weight: 600;
}

.summary-text {
  color: #606266;
  font-size: 13px;
  line-height: 1.8;
}

.start-btn {
  width: 100%;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-alert {
  margin-bottom: 12px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.candidate-card {
  border: none;
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.candidate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

.candidate-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.candidate-main {
  flex: 1;
}

.candidate-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.candidate-name {
  color: #303133;
  font-size: 18px;
  font-weight: 700;
}

.candidate-meta {
  color: #909399;
  font-size: 14px;
}

.divider {
  margin: 0 8px;
}

.tag-block,
.comment-block {
  margin-bottom: 14px;
}

.block-title {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
  font-weight: 700;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.comment-block p {
  margin: 0;
  color: #606266;
  line-height: 1.8;
}

.analysis-loading,
.analysis-placeholder {
  margin-top: 8px;
}

.analysis-placeholder {
  color: #909399;
  font-size: 13px;
}

.action-group {
  margin-top: 12px;
}

@media (max-width: 992px) {
  .candidate-card__top {
    align-items: flex-start;
    flex-direction: column;
  }

  .action-group :deep(.el-button-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
