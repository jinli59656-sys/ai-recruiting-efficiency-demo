<template>
  <div class="comparison-page">
    <h2 class="page-title">候选人对比</h2>

    <el-card class="selector-card" shadow="never">
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="10">
            <el-form-item label="选择岗位">
              <el-select v-model="form.positionId" filterable clearable placeholder="请选择要对比的岗位" style="width: 100%" @change="handlePositionChange">
                <el-option v-for="item in positionOptions" :key="item.id" :label="item.position_name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="选择候选人">
              <el-select
                v-model="form.resumeIds"
                multiple
                filterable
                clearable
                :multiple-limit="5"
                placeholder="请选择候选人（2-5人）"
                style="width: 100%"
              >
                <el-option
                  v-for="item in resumeOptions"
                  :key="item.id"
                  :label="item.candidate_name || `简历${item.id}`"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4" class="align-bottom">
            <el-button type="primary" :disabled="form.resumeIds.length < 2 || !form.positionId" :loading="creating" @click="handleCreateCompare">
              开始对比
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="section-title">对比历史</div>
      </template>
      <el-table :data="historyList" size="small" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="岗位" min-width="180">
          <template #default="{ row }">{{ row.position?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="candidate_count" label="人数" width="80" align="center" />
        <el-table-column label="推荐人选" min-width="140">
          <template #default="{ row }">{{ row.best_choice || '-' }}</template>
        </el-table-column>
        <el-table-column label="第一名" min-width="140">
          <template #default="{ row }">{{ row.top_ranked_candidate || '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleLoadHistoryDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <template v-if="comparisonData">
      <el-card class="compare-card" shadow="never">
        <template #header>
          <div class="section-title">基础信息对比</div>
        </template>
        <el-table :data="basicComparisonRows" border stripe>
          <el-table-column prop="label" label="对比项" fixed width="120" />
          <el-table-column v-for="candidate in comparisonData.candidates" :key="candidate.resume_id" :label="candidate.name" min-width="180">
            <template #default="{ row }">
              <span>{{ row.values[candidate.resume_id] }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="compare-card" shadow="never">
        <template #header>
          <div class="chart-header">
            <span class="section-title">评分对比</span>
            <el-radio-group v-model="chartMode" size="small">
              <el-radio-button label="bar">柱状图</el-radio-button>
              <el-radio-button label="radar">雷达图</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="chartRef" class="chart-box"></div>
      </el-card>

      <el-card class="compare-card" shadow="never">
        <template #header>
          <div class="section-title">综合得分排名</div>
        </template>
        <div class="ranking-list">
          <div v-for="item in rankingList" :key="item.rank" class="ranking-item">
            <div class="ranking-left">
              <div class="ranking-badge">{{ item.rank }}</div>
              <div>
                <div class="ranking-name">{{ item.name }}</div>
                <div class="ranking-reason">{{ item.reason }}</div>
              </div>
            </div>
            <div class="ranking-score">{{ item.score }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="compare-card" shadow="never">
        <template #header>
          <div class="action-row">
            <span class="section-title">AI 对比分析</span>
            <div class="action-buttons">
              <el-button type="primary" :loading="analyzing" @click="handleAnalyze">AI分析</el-button>
              <el-button :disabled="!comparisonData.id" @click="handleExport">导出报告</el-button>
            </div>
          </div>
        </template>

        <el-empty v-if="!analysisData" description="请先点击 AI分析 生成对比结论" />

        <template v-else>
          <div class="analysis-summary">{{ analysisData.comparison_summary }}</div>

          <el-tabs v-model="activeAnalysisTab">
            <el-tab-pane
              v-for="item in analysisData.candidate_analysis || []"
              :key="item.name"
              :label="item.name"
              :name="item.name"
            >
              <div class="analysis-section">
                <div class="analysis-block">
                  <div class="analysis-title">优势</div>
                  <div class="tag-list">
                    <el-tag v-for="adv in item.advantages_over_others || []" :key="adv" type="success">{{ adv }}</el-tag>
                  </div>
                </div>
                <div class="analysis-block">
                  <div class="analysis-title">劣势</div>
                  <div class="tag-list">
                    <el-tag v-for="dis in item.disadvantages || []" :key="dis" type="warning">{{ dis }}</el-tag>
                  </div>
                </div>
                <div class="analysis-block"><strong>适合场景：</strong>{{ item.suitable_scenarios }}</div>
                <div class="analysis-block"><strong>风险点：</strong>{{ item.risk_points }}</div>
              </div>
            </el-tab-pane>
          </el-tabs>

          <el-card class="recommend-card" shadow="never">
            <div class="recommend-title">AI 推荐结论</div>
            <p><strong>最佳人选：</strong>{{ analysisData.recommendation?.best_choice || '-' }}</p>
            <p><strong>推荐理由：</strong>{{ analysisData.recommendation?.reason || '-' }}</p>
            <p><strong>备选人选：</strong>{{ analysisData.recommendation?.alternative || '-' }}</p>
            <p><strong>备选理由：</strong>{{ analysisData.recommendation?.alternative_reason || '-' }}</p>
            <p><strong>录用建议：</strong>{{ analysisData.hiring_advice || '-' }}</p>
          </el-card>
        </template>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getPositionListApi } from '@/api/position'
import { getResumeListApi } from '@/api/resume'
import { analyzeCompareApi, createCompareApi, exportCompareReportUrl, getCompareDetailApi, getCompareHistoryApi } from '@/api/compare'

const creating = ref(false)
const analyzing = ref(false)
const positionOptions = ref<any[]>([])
const resumeOptions = ref<any[]>([])
const comparisonData = ref<any>(null)
const analysisData = ref<any>(null)
const historyList = ref<any[]>([])
const chartMode = ref('bar')
const activeAnalysisTab = ref('')
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const form = reactive({
  positionId: undefined as number | undefined,
  resumeIds: [] as number[],
})

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const loadResumes = async () => {
  const res = await getResumeListApi({ page: 1, page_size: 100 })
  const payload = res.data?.data || {}
  resumeOptions.value = payload.data || []
}

const loadHistory = async () => {
  const res = await getCompareHistoryApi({ page: 1, page_size: 10, positionId: form.positionId || undefined })
  const payload = res.data?.data || {}
  historyList.value = payload.items || []
}

const handlePositionChange = async () => {
  form.resumeIds = []
  await loadHistory()
}

const handleCreateCompare = async () => {
  if (!form.positionId || form.resumeIds.length < 2) {
    ElMessage.warning('请选择岗位并至少选择两位候选人')
    return
  }

  creating.value = true
  try {
    const res = await createCompareApi({
      positionId: form.positionId,
      resumeIds: form.resumeIds,
    })
    comparisonData.value = res.data?.data || null
    analysisData.value = null
    await nextTick()
    renderChart()
    await loadHistory()
    ElMessage.success('候选人对比创建成功')
  } finally {
    creating.value = false
  }
}

const handleAnalyze = async () => {
  if (!comparisonData.value?.id) return
  analyzing.value = true
  try {
    const res = await analyzeCompareApi(comparisonData.value.id)
    analysisData.value = res.data?.data || null
    activeAnalysisTab.value = analysisData.value?.candidate_analysis?.[0]?.name || ''
    rankingList.value = analysisData.value?.ranking || rankingList.value
    ElMessage.success('AI对比分析完成')
  } finally {
    analyzing.value = false
  }
}

const handleLoadHistoryDetail = async (id: number) => {
  const res = await getCompareDetailApi(id)
  const payload = res.data?.data || {}

  comparisonData.value = {
    id: payload.id,
    position: payload.position,
    candidates: payload.candidates || [],
  }

  analysisData.value = payload.ai_analysis
    ? {
        ...payload.ai_analysis,
        ranking: payload.ranking || [],
      }
    : null

  activeAnalysisTab.value = analysisData.value?.candidate_analysis?.[0]?.name || ''
  await nextTick()
  renderChart()
  ElMessage.success('已加载历史对比详情')
}

const handleExport = () => {
  if (!comparisonData.value?.id) return
  window.open(exportCompareReportUrl(comparisonData.value.id), '_blank')
}

const rankingList = computed(() => {
  if (analysisData.value?.ranking?.length) return analysisData.value.ranking
  const candidates = comparisonData.value?.candidates || []
  return [...candidates]
    .sort((a, b) => (b.evaluation?.total_score || 0) - (a.evaluation?.total_score || 0))
    .map((item, index) => ({
      rank: index + 1,
      name: item.name,
      score: item.evaluation?.total_score || 0,
      reason: '基于当前综合得分排序',
    }))
})

const basicComparisonRows = computed(() => {
  const candidates = comparisonData.value?.candidates || []
  return [
    { label: '姓名', values: Object.fromEntries(candidates.map((c: any) => [c.resume_id, c.name || '-'])) },
    { label: '学历/院校', values: Object.fromEntries(candidates.map((c: any) => [c.resume_id, `${c.education || '-'} / ${c.school || '-'}`])) },
    { label: '工作年限', values: Object.fromEntries(candidates.map((c: any) => [c.resume_id, c.work_years ? `${c.work_years}年` : '-'])) },
    { label: '当前职位', values: Object.fromEntries(candidates.map((c: any) => [c.resume_id, c.current_position || '-'])) },
    { label: '技能标签', values: Object.fromEntries(candidates.map((c: any) => [c.resume_id, (c.skills || []).slice(0, 3).join('、') || '-'])) },
  ]
})

const renderChart = () => {
  if (!chartRef.value || !comparisonData.value?.candidates?.length) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  chartInstance.clear()

  const candidates = comparisonData.value.candidates
  const names = candidates.map((item: any) => item.name)

  if (chartMode.value === 'bar') {
    chartInstance.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: names },
      yAxis: { type: 'value', max: 100 },
      series: [
        {
          type: 'bar',
          data: candidates.map((item: any) => item.evaluation?.total_score || 0),
          itemStyle: { color: '#409EFF' },
        },
      ],
    })
    chartInstance.resize()
    return
  }

  chartInstance.setOption({
    tooltip: {},
    legend: { data: names },
    radar: {
      indicator: [
        { name: '专业', max: 100 },
        { name: '逻辑', max: 100 },
        { name: '沟通', max: 100 },
        { name: '学习', max: 100 },
        { name: '团队', max: 100 },
        { name: '文化', max: 100 },
      ],
    },
    series: [
      {
        type: 'radar',
        data: candidates.map((item: any) => ({
          name: item.name,
          value: [
            item.evaluation?.professional_score || 0,
            item.evaluation?.logic_score || 0,
            item.evaluation?.communication_score || 0,
            item.evaluation?.learning_score || 0,
            item.evaluation?.teamwork_score || 0,
            item.evaluation?.culture_score || 0,
          ],
        })),
      },
    ],
  })
  chartInstance.resize()
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

watch(chartMode, () => {
  nextTick(() => renderChart())
})

onMounted(async () => {
  await loadPositions()
  await loadResumes()
  await loadHistory()
})
</script>

<style scoped>
.comparison-page {
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

.selector-card,
.history-card,
.compare-card,
.recommend-card {
  border: none;
  border-radius: 12px;
}

.section-title {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.align-bottom {
  display: flex;
  align-items: flex-end;
}

.chart-header,
.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.chart-box {
  width: 100%;
  height: 400px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background: #fff;
}

.ranking-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ranking-badge {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.ranking-name {
  color: #303133;
  font-size: 15px;
  font-weight: 700;
}

.ranking-reason {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
}

.ranking-score {
  color: #409eff;
  font-size: 20px;
  font-weight: 700;
}

.analysis-summary {
  padding: 16px;
  border-radius: 10px;
  background: #f5f7fa;
  color: #606266;
  line-height: 1.9;
  margin-bottom: 16px;
}

.analysis-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-title {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
  font-weight: 700;
}

.analysis-block {
  color: #606266;
  line-height: 1.8;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recommend-card {
  margin-top: 16px;
  background: #f5faff;
}

.recommend-title {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}
</style>
