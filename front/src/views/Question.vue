<template>
  <div class="question-page">
    <h2 class="page-title">面试题生成</h2>

    <el-card class="config-card" shadow="never">
      <div class="card-title">生成配置</div>

      <el-form label-position="top" class="config-form">
        <el-form-item label="生成模式">
          <el-radio-group v-model="form.mode" size="large">
            <el-radio-button label="基于岗位生成" value="position" />
            <el-radio-button label="基于简历生成" value="resume" />
            <el-radio-button label="岗位+简历混合生成" value="hybrid" />
          </el-radio-group>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12" v-if="showPositionSelect">
            <el-form-item label="选择岗位">
              <el-select v-model="form.positionId" filterable clearable placeholder="请选择岗位" style="width: 100%">
                <el-option
                  v-for="item in positionOptions"
                  :key="item.id"
                  :label="item.position_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-if="showResumeSelect">
            <el-form-item label="选择候选人">
              <el-select v-model="form.resumeId" filterable clearable placeholder="请选择候选人" style="width: 100%">
                <el-option
                  v-for="item in resumeOptions"
                  :key="item.id"
                  :label="item.candidate_name || `简历${item.id}`"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="题目类型">
          <el-checkbox-group v-model="form.questionTypes">
            <el-checkbox label="技术类" value="technical" />
            <el-checkbox label="行为类" value="behavioral" />
            <el-checkbox label="情景类" value="situational" />
            <el-checkbox label="开放类" value="open" />
          </el-checkbox-group>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="难度等级">
              <el-radio-group v-model="form.difficulty">
                <el-radio label="初级" value="junior" />
                <el-radio label="中级" value="middle" />
                <el-radio label="高级" value="senior" />
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="生成数量">
              <el-input-number v-model="form.count" :min="3" :max="20" :step="1" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="参考答案">
              <el-switch v-model="form.withAnswer" active-text="生成参考答案" inactive-text="不生成参考答案" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="config-actions">
          <el-button type="primary" size="large" :loading="generating" @click="handleGenerate">开始生成</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card class="result-card" shadow="never">
      <div class="card-title">生成结果</div>

      <el-skeleton v-if="generating" :rows="10" animated />

      <template v-else>
        <el-empty v-if="!questions.length" description="暂无生成结果，请先完成配置并点击开始生成" />

        <template v-else>
          <el-tabs v-model="activeTab">
            <el-tab-pane
              v-for="group in groupedQuestions"
              :key="group.key"
              :label="`${group.label}（${group.items.length}）`"
              :name="group.key"
            >
              <div class="question-list">
                <el-card v-for="(item, index) in group.items" :key="item.id" class="question-card" shadow="hover">
                  <div class="question-head">
                    <span class="question-order">题目 {{ index + 1 }}</span>
                    <el-tag :type="getDifficultyTagType(item.difficulty)" size="small">{{ formatDifficulty(item.difficulty) }}</el-tag>
                  </div>

                  <div class="question-content">{{ item.question }}</div>

                  <el-collapse>
                    <el-collapse-item title="查看参考答案" name="answer">
                      <div class="collapse-content">{{ item.reference_answer || '暂无参考答案' }}</div>
                    </el-collapse-item>
                    <el-collapse-item title="评分要点" name="scoring">
                      <ol class="scoring-list">
                        <li v-for="point in item.scoring_points || []" :key="point">{{ point }}</li>
                      </ol>
                    </el-collapse-item>
                  </el-collapse>

                  <div class="question-actions">
                    <el-button link type="primary" @click="openEditDialog(item)">编辑</el-button>
                    <el-button link type="danger" @click="handleDelete(item.id)">删除</el-button>
                    <el-button link type="primary" @click="copyQuestion(item)">复制题目</el-button>
                    <el-button
                      v-if="item.is_saved === 0"
                      link
                      type="success"
                      @click="handleSaveSingleToBank(item.id)"
                    >
                      保存到题库
                    </el-button>
                    <el-tag v-else type="success" size="small">已入题库</el-tag>
                  </div>
                </el-card>
              </div>
            </el-tab-pane>
          </el-tabs>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :page-sizes="[10, 20, 50]"
              :total="total"
            />
          </div>
        </template>
      </template>
    </el-card>

    <el-dialog v-model="editDialogVisible" title="编辑题目" width="720px">
      <el-form v-if="editingQuestion" label-position="top">
        <el-form-item label="题目类型">
          <el-select v-model="editingQuestion.type" style="width: 100%">
            <el-option label="技术类" value="technical" />
            <el-option label="行为类" value="behavioral" />
            <el-option label="情景类" value="situational" />
            <el-option label="开放类" value="open" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度等级">
          <el-select v-model="editingQuestion.difficulty" style="width: 100%">
            <el-option label="初级" value="junior" />
            <el-option label="中级" value="middle" />
            <el-option label="高级" value="senior" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input v-model="editingQuestion.question" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="参考答案">
          <el-input v-model="editingQuestion.reference_answer" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="评分要点（每行一个）">
          <el-input v-model="scoringPointsText" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveQuestion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getPositionListApi } from '@/api/position'
import { getResumeListApi } from '@/api/resume'
import {
  deleteQuestionApi,
  generateQuestionsApi,
  getQuestionListApi,
  saveQuestionsToBankApi,
  updateQuestionApi,
} from '@/api/question'

const router = useRouter()
const generating = ref(false)
const saving = ref(false)
const editDialogVisible = ref(false)
const activeTab = ref('technical')
const positionOptions = ref<any[]>([])
const resumeOptions = ref<any[]>([])
const questions = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const editingQuestion = ref<any>(null)
const scoringPointsText = ref('')

const form = reactive({
  mode: 'hybrid',
  positionId: undefined as number | undefined,
  resumeId: undefined as number | undefined,
  questionTypes: ['technical', 'behavioral'],
  difficulty: 'middle',
  count: 5,
  withAnswer: true,
})

const showPositionSelect = computed(() => form.mode === 'position' || form.mode === 'hybrid')
const showResumeSelect = computed(() => form.mode === 'resume' || form.mode === 'hybrid')

const typeLabelMap: Record<string, string> = {
  technical: '技术类',
  behavioral: '行为类',
  situational: '情景类',
  open: '开放类',
}

const difficultyLabelMap: Record<string, string> = {
  junior: '初级',
  middle: '中级',
  senior: '高级',
}

const normalizeQuestionType = (type?: string) => {
  if (type === '技术类') return 'technical'
  if (type === '行为类') return 'behavioral'
  if (type === '情景类') return 'situational'
  if (type === '开放类') return 'open'
  return type || 'technical'
}

const normalizeDifficulty = (difficulty?: string) => {
  if (difficulty === '初级') return 'junior'
  if (difficulty === '中级') return 'middle'
  if (difficulty === '高级') return 'senior'
  return difficulty || 'middle'
}

const groupedQuestions = computed(() => {
  const groups: Record<string, any[]> = {
    technical: [],
    behavioral: [],
    situational: [],
    open: [],
  }

  questions.value.forEach((item) => {
    const normalizedType = normalizeQuestionType(item.type || item.question_type)
    if (!groups[normalizedType]) groups[normalizedType] = []
    groups[normalizedType].push(item)
  })

  return Object.keys(groups)
    .filter((key) => groups[key].length > 0)
    .map((key) => ({
      key,
      label: typeLabelMap[key] || key,
      items: groups[key],
    }))
})

const normalizeQuestionResponse = (responseData: any) => {
  const payload =
    responseData?.data?.data ??
    responseData?.data ??
    responseData ??
    {}

  const rawQuestions =
    payload.questions ??
    payload.data?.questions ??
    []

  const normalizedQuestions = Array.isArray(rawQuestions)
    ? rawQuestions.map((item) => ({
        id: item.id ?? null,
        type: normalizeQuestionType(item.type || item.question_type),
        difficulty: normalizeDifficulty(item.difficulty),
        question: item.question || item.question_content || '',
        reference_answer: item.reference_answer || '',
        scoring_points: Array.isArray(item.scoring_points) ? item.scoring_points : [],
        source: item.source || '',
      }))
    : []

  return {
    questions: normalizedQuestions,
    count: Number(payload.count ?? normalizedQuestions.length) || normalizedQuestions.length,
  }
}

const loadQuestions = async () => {
  try {
    const res = await getQuestionListApi({ page: currentPage.value, page_size: pageSize.value })
    const payload =
      res.data?.data?.data ??
      res.data?.data ??
      res.data ??
      {}
    const rawItems =
      payload.items ??
      payload.data?.items ??
      []
    console.log('题目列表响应：', res.data)
    console.log('题目列表原始 items：', rawItems)
    total.value = Number(payload.total ?? 0)
    questions.value = rawItems.map((item: any) => ({
      id: item.id ?? null,
      type: normalizeQuestionType(item.type || item.question_type),
      question_type: normalizeQuestionType(item.type || item.question_type),
      difficulty: normalizeDifficulty(item.difficulty),
      question: item.question || item.question_content || '',
      question_content: item.question || item.question_content || '',
      reference_answer: item.reference_answer || '',
      scoring_points: Array.isArray(item.scoring_points) ? item.scoring_points : [],
      source: item.source || '',
      is_saved: item.is_saved ?? 0,
    }))
    console.log('题目列表解析后数量：', questions.value.length)
    if (groupedQuestions.value.length) {
      activeTab.value = groupedQuestions.value[0].key
    }
  } catch (error: any) {
    console.error('获取题目列表失败原始错误：', error)
    console.error('获取题目列表失败响应数据：', error?.response?.data)
    questions.value = []
    ElMessage.error(error?.response?.data?.message || error?.response?.data?.detail || '获取题目列表失败')
  }
}

const loadPositions = async () => {
  const res = await getPositionListApi({ page: 1, page_size: 100 })
  positionOptions.value = res.data?.items || []
}

const loadResumes = async () => {
  const res = await getResumeListApi({ page: 1, page_size: 100 })
  const payload = res.data?.data || {}
  resumeOptions.value = payload.data || []
}

const handleGenerate = async () => {
  if (showPositionSelect.value && !form.positionId) {
    ElMessage.warning('请选择岗位')
    return
  }
  if (showResumeSelect.value && !form.resumeId) {
    ElMessage.warning('请选择候选人')
    return
  }
  if (!form.questionTypes.length) {
    ElMessage.warning('请至少选择一种题目类型')
    return
  }

  generating.value = true
  try {
    const res = await generateQuestionsApi({
      mode: form.mode,
      positionId: form.positionId,
      resumeId: form.resumeId,
      questionTypes: form.questionTypes,
      difficulty: form.difficulty,
      count: form.count,
      withAnswer: form.withAnswer,
    })

    const normalized = normalizeQuestionResponse(res.data)
    console.log('面试题生成响应：', res.data)
    console.log('面试题生成解析数量：', normalized.count)
    currentPage.value = 1
    await loadQuestions()
    ElMessage.success('面试题生成成功')
  } catch (error: any) {
    console.error('生成面试题失败原始错误：', error)
    console.error('生成面试题失败响应数据：', error?.response?.data)

    ElMessage.error(
      error?.code === 'ECONNABORTED'
        ? '生成耗时较长，请稍后重试'
        : error?.response?.data?.message ||
          error?.response?.data?.detail ||
          '生成失败，请稍后重试'
    )
  } finally {
    generating.value = false
  }
}

const handleDelete = async (id: number) => {
  await deleteQuestionApi(id)
  ElMessage.success('删除成功')
  await loadQuestions()
}

const openEditDialog = (item: any) => {
  editingQuestion.value = {
    id: item.id,
    type: normalizeQuestionType(item.type || item.question_type),
    difficulty: normalizeDifficulty(item.difficulty),
    question: item.question || item.question_content,
    reference_answer: item.reference_answer || '',
  }
  scoringPointsText.value = (item.scoring_points || []).join('\n')
  editDialogVisible.value = true
}

const handleSaveQuestion = async () => {
  if (!editingQuestion.value) return

  saving.value = true
  try {
    await updateQuestionApi(editingQuestion.value.id, {
      type: editingQuestion.value.type,
      difficulty: editingQuestion.value.difficulty,
      question: editingQuestion.value.question,
      referenceAnswer: editingQuestion.value.reference_answer,
      scoringPoints: scoringPointsText.value
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean),
    })
    ElMessage.success('保存成功')
    const target = questions.value.find((item) => item.id === editingQuestion.value.id)
    if (target) {
      target.type = editingQuestion.value.type
      target.difficulty = editingQuestion.value.difficulty
      target.question = editingQuestion.value.question
      target.reference_answer = editingQuestion.value.reference_answer
      target.scoring_points = scoringPointsText.value
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean)
    }
    editDialogVisible.value = false
    await loadQuestions()
  } finally {
    saving.value = false
  }
}

const handleSaveSingleToBank = async (id: number) => {
  await saveQuestionsToBankApi([id])
  ElMessage.success('保存到题库成功')
  await loadQuestions()
}

const copyQuestion = async (item: any) => {
  const text = item.question || item.question_content || ''
  await navigator.clipboard.writeText(text)
  ElMessage.success('题目已复制')
}

const formatDifficulty = (difficulty: string) => difficultyLabelMap[normalizeDifficulty(difficulty)] || difficulty
const getDifficultyTagType = (difficulty: string) => {
  const normalizedDifficulty = normalizeDifficulty(difficulty)
  if (normalizedDifficulty === 'junior') return 'success'
  if (normalizedDifficulty === 'middle') return 'warning'
  if (normalizedDifficulty === 'senior') return 'danger'
  return 'info'
}

onMounted(async () => {
  await loadPositions()
  await loadResumes()
  await loadQuestions()
})

watch([currentPage, pageSize], () => {
  loadQuestions()
})
</script>

<style scoped>
.question-page {
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

.config-card,
.result-card {
  border: none;
  border-radius: 12px;
}

.card-title {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-card {
  border: none;
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

.question-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.question-order {
  color: #606266;
  font-size: 13px;
  font-weight: 600;
}

.question-content {
  margin-bottom: 16px;
  color: #303133;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.8;
  white-space: pre-wrap;
}

.collapse-content {
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
}

.scoring-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
