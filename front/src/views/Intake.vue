<template>
  <div class="intake-page">
    <div class="page-heading">
      <div>
        <h2 class="page-title">数据采集与同步</h2>
        <p class="page-subtitle">企业微信群消息自动解析，实时同步到腾讯在线文档镜像表</p>
      </div>
      <el-button :icon="Refresh" @click="loadPageData">刷新</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="8">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="card-title">企业微信群消息</div>
          </template>

          <div class="sample-list">
            <button
              v-for="item in sampleMessages"
              :key="item.title"
              type="button"
              class="sample-item"
              @click="applySample(item.message)"
            >
              <span>{{ item.title }}</span>
              <small>{{ item.message }}</small>
            </button>
          </div>

          <el-form label-position="top" class="message-form">
            <el-form-item label="来源群">
              <el-input v-model="form.sourceChannel" />
            </el-form-item>
            <el-form-item label="发送人">
              <el-input v-model="form.sender" />
            </el-form-item>
            <el-form-item label="群聊原文">
              <el-input
                v-model="form.rawMessage"
                type="textarea"
                :rows="7"
                placeholder="粘贴企业微信群里的候选人状态、面试安排或招聘跟进消息"
              />
            </el-form-item>
          </el-form>

          <el-button
            type="primary"
            size="large"
            class="parse-btn"
            :loading="parsing"
            @click="handleParse"
          >
            AI 解析并同步
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="panel-card result-panel" shadow="never">
          <template #header>
            <div class="card-title">AI 抽取结果</div>
          </template>

          <el-empty v-if="!lastResult" description="提交群消息后展示结构化结果" />

          <div v-else class="result-content">
            <div class="candidate-line">
              <span class="candidate-name">{{ lastResult.candidate_name }}</span>
              <el-tag :type="lastResult.needs_review ? 'warning' : 'success'">
                {{ lastResult.needs_review ? '需人工确认' : '自动确认' }}
              </el-tag>
            </div>

            <div class="field-grid">
              <div class="field-item">
                <span>岗位</span>
                <strong>{{ lastResult.position_name || '待确认' }}</strong>
              </div>
              <div class="field-item">
                <span>阶段</span>
                <strong>{{ lastResult.stage || '待确认' }}</strong>
              </div>
              <div class="field-item">
                <span>学历</span>
                <strong>{{ lastResult.education || '待确认' }}</strong>
              </div>
              <div class="field-item">
                <span>年限</span>
                <strong>{{ formatYears(lastResult.work_years) }}</strong>
              </div>
              <div class="field-item">
                <span>面试时间</span>
                <strong>{{ lastResult.interview_time || '待确认' }}</strong>
              </div>
              <div class="field-item">
                <span>负责人</span>
                <strong>{{ lastResult.owner || '-' }}</strong>
              </div>
            </div>

            <div class="confidence-block">
              <span>置信度</span>
              <el-progress
                :percentage="Math.round((lastResult.confidence || 0) * 100)"
                :status="lastResult.needs_review ? 'warning' : 'success'"
              />
            </div>

            <el-alert
              v-if="lastResult.needs_review"
              type="warning"
              show-icon
              :closable="false"
              title="模型或规则抽取置信度较低，建议 HR 在文档镜像表中确认后再流转。"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="panel-card events-panel" shadow="never">
          <template #header>
            <div class="card-title">最近同步动态</div>
          </template>

          <el-timeline v-if="events.length">
            <el-timeline-item
              v-for="item in events"
              :key="item.id"
              :timestamp="formatDateTime(item.created_at)"
              :type="getEventType(item.event_type)"
            >
              <div class="event-title">{{ item.title }}</div>
              <div v-if="item.detail" class="event-detail">{{ item.detail }}</div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无同步动态" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card docs-card" shadow="never">
      <template #header>
        <div class="table-header">
          <span class="card-title">腾讯在线文档镜像表</span>
          <el-tag type="success">自动同步</el-tag>
        </div>
      </template>

      <el-table v-loading="loadingDocs" :data="docRows" stripe border>
        <el-table-column prop="candidate_name" label="候选人" min-width="110" />
        <el-table-column prop="position_name" label="岗位" min-width="130">
          <template #default="{ row }">{{ row.position_name || '待确认' }}</template>
        </el-table-column>
        <el-table-column prop="stage" label="当前阶段" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.stage || '待确认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="interview_time" label="面试时间" min-width="130">
          <template #default="{ row }">{{ row.interview_time || '-' }}</template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="110">
          <template #default="{ row }">{{ row.owner || '-' }}</template>
        </el-table-column>
        <el-table-column prop="source_channel" label="来源" min-width="150" />
        <el-table-column label="同步状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.needs_review ? 'warning' : 'success'">
              {{ row.needs_review ? '待确认' : row.sync_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="160">
          <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getIntakeEventsApi, getTencentDocsApi, parseIntakeMessageApi } from '@/api/intake'

const sampleMessages = [
  {
    title: '新增初面安排',
    message: '@HR 张三 Java后端 3年经验 本科，简历已收，约周三14:00初面，面试官王经理',
  },
  {
    title: '一面通过待复试',
    message: '李四 产品经理 5年经验 硕士，今天一面通过，待安排复试，负责人刘敏',
  },
  {
    title: '候选人淘汰记录',
    message: '王五 前端开发 2年经验 本科，初面沟通后不匹配，已淘汰，面试官陈主管',
  },
]

const form = reactive({
  rawMessage: sampleMessages[0].message,
  sourceChannel: '企业微信-招聘群',
  sender: '招聘助理',
})

const parsing = ref(false)
const loadingDocs = ref(false)
const lastResult = ref<any>(null)
const docRows = ref<any[]>([])
const events = ref<any[]>([])

const applySample = (message: string) => {
  form.rawMessage = message
}

const handleParse = async () => {
  if (!form.rawMessage.trim()) {
    ElMessage.warning('请先输入企业微信群消息')
    return
  }

  parsing.value = true
  try {
    const res = await parseIntakeMessageApi({
      raw_message: form.rawMessage,
      source_channel: form.sourceChannel,
      sender: form.sender,
    })
    lastResult.value = res.data?.data || null
    ElMessage.success('解析并同步成功')
    await loadPageData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || error?.response?.data?.detail || '解析同步失败')
  } finally {
    parsing.value = false
  }
}

const loadDocs = async () => {
  loadingDocs.value = true
  try {
    const res = await getTencentDocsApi({ limit: 100 })
    docRows.value = res.data?.data || []
  } finally {
    loadingDocs.value = false
  }
}

const loadEvents = async () => {
  const res = await getIntakeEventsApi({ limit: 10 })
  events.value = res.data?.data || []
}

const loadPageData = async () => {
  await Promise.all([loadDocs(), loadEvents()])
}

const formatYears = (value?: number) => {
  if (!value && value !== 0) return '待确认'
  return `${value}年`
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

const getEventType = (type?: string) => {
  if (type === 'needs_review') return 'warning'
  if (type === 'doc_synced') return 'success'
  return 'primary'
}

onMounted(() => {
  loadPageData()
})
</script>

<style scoped>
.intake-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-title {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 700;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #606266;
  font-size: 14px;
}

.panel-card {
  border: none;
  border-radius: 8px;
}

.card-title {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
}

.sample-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.sample-item {
  display: grid;
  gap: 6px;
  width: 100%;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  color: #303133;
  text-align: left;
  cursor: pointer;
}

.sample-item:hover {
  border-color: #409eff;
  background: #f5f9ff;
}

.sample-item span {
  font-size: 14px;
  font-weight: 700;
}

.sample-item small {
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.message-form {
  margin-top: 8px;
}

.parse-btn {
  width: 100%;
}

.result-panel,
.events-panel {
  min-height: 100%;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.candidate-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.candidate-name {
  color: #303133;
  font-size: 22px;
  font-weight: 700;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.field-item {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 8px;
  background: #f5f7fa;
}

.field-item span,
.confidence-block span {
  color: #909399;
  font-size: 12px;
}

.field-item strong {
  color: #303133;
  font-size: 14px;
}

.confidence-block {
  display: grid;
  gap: 8px;
}

.event-title {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.event-detail {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.docs-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-heading,
  .candidate-line {
    align-items: stretch;
    flex-direction: column;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
