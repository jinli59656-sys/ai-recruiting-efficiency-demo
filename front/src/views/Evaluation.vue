<template>
  <div class="evaluation-page">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/summary/1' }">面试摘要</el-breadcrumb-item>
      <el-breadcrumb-item>面试评价</el-breadcrumb-item>
    </el-breadcrumb>

    <el-empty v-if="!evaluationData && !loading" description="暂无评价数据，请先从摘要页生成面试评价" />

    <el-row v-else :gutter="20">
      <el-col :span="10">
        <el-card class="score-card" shadow="never" v-loading="loading">
          <div class="candidate-header">
            <h2>{{ candidateName }}</h2>
            <el-tag type="primary">面试评价</el-tag>
          </div>

          <div class="total-score-wrap">
            <el-progress type="circle" :width="150" :percentage="evaluationData?.total_score || 0" :color="getScoreColor(evaluationData?.total_score || 0)" />
            <div class="total-score-text">{{ evaluationData?.total_score || 0 }}</div>
            <el-tag :type="getRecommendationTagType(evaluationData?.recommendation)">{{ evaluationData?.recommendation || '待定' }}</el-tag>
          </div>

          <div class="score-list">
            <div v-for="item in dimensionItems" :key="item.key" class="score-row">
              <div class="score-label">{{ item.label }}</div>
              <el-progress :percentage="item.value" :stroke-width="12" :color="getScoreColor(item.value)" />
              <div class="score-value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <div class="right-panel">
          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">AI 综合评语</div>
            </template>
            <div class="comment-box">{{ evaluationData?.ai_comment || '暂无 AI 评语' }}</div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">各维度详细评价</div>
            </template>
            <el-collapse>
              <el-collapse-item v-for="item in dimensionItems" :key="item.key" :title="`${item.label}（${item.value}分）`" :name="item.key">
                <div class="dimension-comment">{{ item.comment || '暂无评价' }}</div>
              </el-collapse-item>
            </el-collapse>
          </el-card>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-card class="detail-card" shadow="never">
                <template #header>
                  <div class="card-title">核心优势</div>
                </template>
                <ul class="summary-list success-list">
                  <li v-for="item in evaluationData?.key_strengths || []" :key="item">{{ item }}</li>
                </ul>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="detail-card" shadow="never">
                <template #header>
                  <div class="card-title">待提升领域</div>
                </template>
                <ul class="summary-list warning-list">
                  <li v-for="item in evaluationData?.improvement_areas || []" :key="item">{{ item }}</li>
                </ul>
              </el-card>
            </el-col>
          </el-row>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">HR 补充评价</div>
            </template>
            <el-input v-model="hrComment" type="textarea" :rows="4" placeholder="请输入 HR 补充评价" />
            <div class="hr-action">
              <el-button type="primary" :loading="savingHrComment" @click="handleSaveHrComment">保存</el-button>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">录用建议</div>
            </template>
            <div class="comment-box">{{ evaluationData?.hiring_suggestion || '暂无录用建议' }}</div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header>
              <div class="card-title">评价历史记录</div>
            </template>
            <div v-if="evaluationHistory.length" class="history-list">
              <div
                v-for="item in evaluationHistory"
                :key="item.id"
                class="history-item"
                :class="{ active: item.id === evaluationData?.id }"
              >
                <div class="history-main">
                  <div class="history-title">评价 #{{ item.id }}</div>
                  <div class="history-meta">
                    <span>综合分：{{ item.total_score }}</span>
                    <span class="divider">|</span>
                    <span>推荐：{{ item.recommendation }}</span>
                    <span class="divider">|</span>
                    <span>{{ formatDateTime(item.created_at) }}</span>
                  </div>
                </div>
                <el-button link type="primary" @click="loadEvaluationById(item.id)">查看</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无历史评价" />
          </el-card>
        </div>
      </el-col>
    </el-row>

    <div v-if="evaluationData" class="bottom-action-bar">
      <el-card shadow="never">
        <div class="bottom-actions">
          <el-button type="success" size="large" @click="ElMessage.success('已标记通过')">通过</el-button>
          <el-button type="warning" size="large" @click="ElMessage.info('已标记待定')">待定</el-button>
          <el-button type="danger" size="large" @click="ElMessage.error('已标记淘汰')">淘汰</el-button>
          <el-button size="large" @click="ElMessage.info('导出评价报告接口当前后端未提供')">导出评价报告</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { addHrCommentApi, getEvaluationApi, getEvaluationHistoryApi } from '@/api/evaluation'

const route = useRoute()
const loading = ref(false)
const savingHrComment = ref(false)
const evaluationData = ref<any>(null)
const evaluationHistory = ref<any[]>([])
const hrComment = ref('')
const candidateName = ref('候选人')

const resumeId = computed(() => Number(route.params.resumeId || 0))

const dimensionItems = computed(() => {
  const scores = evaluationData.value?.scores || {}
  return [
    { key: 'professional', label: '专业能力', value: scores.professional?.score || 0, comment: scores.professional?.comment || '' },
    { key: 'logic', label: '逻辑思维', value: scores.logic?.score || 0, comment: scores.logic?.comment || '' },
    { key: 'communication', label: '沟通表达', value: scores.communication?.score || 0, comment: scores.communication?.comment || '' },
    { key: 'learning', label: '学习能力', value: scores.learning?.score || 0, comment: scores.learning?.comment || '' },
    { key: 'teamwork', label: '团队协作', value: scores.teamwork?.score || 0, comment: scores.teamwork?.comment || '' },
    { key: 'culture_fit', label: '文化匹配', value: scores.culture_fit?.score || 0, comment: scores.culture_fit?.comment || '' },
  ]
})

const getScoreColor = (score: number) => {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 60) return '#909399'
  return '#F56C6C'
}

const getRecommendationTagType = (recommendation?: string) => {
  if (!recommendation) return 'info'
  if (recommendation.includes('强烈')) return 'success'
  if (recommendation.includes('推荐')) return 'primary'
  if (recommendation.includes('不')) return 'danger'
  return 'info'
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

const loadEvaluationById = async (evaluationId: number) => {
  const detailRes = await getEvaluationApi(evaluationId)
  evaluationData.value = detailRes.data?.data || null
  hrComment.value = evaluationData.value?.hr_comment || ''
}

const loadEvaluation = async () => {
  if (!resumeId.value) return

  loading.value = true
  try {
    const historyRes = await getEvaluationHistoryApi(resumeId.value)
    const history = historyRes.data?.data || []
    evaluationHistory.value = Array.isArray(history) ? history : []

    if (evaluationHistory.value.length) {
      await loadEvaluationById(evaluationHistory.value[0].id)
    } else {
      evaluationData.value = null
    }
  } finally {
    loading.value = false
  }
}

const handleSaveHrComment = async () => {
  if (!evaluationData.value?.id) return
  savingHrComment.value = true
  try {
    await addHrCommentApi(evaluationData.value.id, hrComment.value)
    ElMessage.success('HR补充评价保存成功')
  } finally {
    savingHrComment.value = false
  }
}

onMounted(() => {
  loadEvaluation()
})
</script>

<style scoped>
.evaluation-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-card,
.detail-card {
  border: none;
  border-radius: 12px;
}

.candidate-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.candidate-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.total-score-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.total-score-text {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.score-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-row {
  display: grid;
  grid-template-columns: 90px 1fr 50px;
  gap: 12px;
  align-items: center;
}

.score-label,
.score-value {
  color: #606266;
  font-size: 14px;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-title {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.comment-box,
.dimension-comment {
  color: #606266;
  line-height: 1.9;
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

.hr-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
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

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.history-item.active {
  border-color: #409eff;
  background: #f5faff;
}

.history-main {
  flex: 1;
}

.history-title {
  margin-bottom: 6px;
  color: #303133;
  font-size: 14px;
  font-weight: 700;
}

.history-meta {
  color: #909399;
  font-size: 13px;
}

.divider {
  margin: 0 8px;
}
</style>
