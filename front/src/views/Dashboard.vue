<template>
  <div class="dashboard-page" v-loading="loading">
    <el-row :gutter="16" class="stats-row">
      <el-col
        v-for="item in stats"
        :key="item.title"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card shadow="hover" class="stats-card clickable-card" @click="handleStatsClick(item.route)">
          <div class="stats-card__content">
            <div class="stats-icon" :style="{ backgroundColor: item.bgColor, color: item.color }">
              <el-icon :size="24">
                <component :is="item.icon" />
              </el-icon>
            </div>

            <div class="stats-info">
              <div class="stats-title">{{ item.title }}</div>
              <div class="stats-value">{{ item.value }}</div>
              <div class="stats-trend">
                <span>实时统计</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="middle-row">
      <el-col :xs="24" :lg="12">
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
            </div>
          </template>

          <div class="todo-list" v-if="todoList.length">
            <button
              v-for="(item, index) in todoList"
              :key="`${item.type}-${index}`"
              type="button"
              class="todo-item"
              @click="handleTodoClick(item.type)"
            >
              <span class="todo-title">{{ item.title }}</span>
              <span class="todo-meta">{{ item.type }}</span>
            </button>
          </div>
          <el-empty v-else description="暂无待办事项" />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <span>最近面试安排</span>
            </div>
          </template>

          <el-timeline v-if="interviewSchedule.length">
            <el-timeline-item
              v-for="item in interviewSchedule"
              :key="item.recording_id"
              :timestamp="item.interview_date || '-'"
              :type="getInterviewTimelineType(item.transcript_status_name)"
            >
              <button type="button" class="timeline-entry" @click="handleInterviewClick(item)">
                <div class="timeline-name">{{ item.candidate_name }}</div>
                <div class="timeline-role">{{ item.position_name || '岗位待定' }}</div>
              </button>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无最近面试安排" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>最近动态</span>
        </div>
      </template>

      <div class="activity-list" v-if="activities.length">
        <div v-for="(item, index) in activities" :key="`${item.time}-${index}`" class="activity-item">
          <div class="activity-main">
            <button type="button" class="activity-link" @click="handleActivityClick(item)">
              <div class="activity-title">{{ item.title }}</div>
            </button>
          </div>
          <div class="activity-time">{{ item.time }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无最近动态" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Microphone,
  OfficeBuilding,
  Search,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getDashboardOverviewApi } from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const overview = ref<any>(null)

const stats = computed(() => {
  const source = overview.value?.stats || {}
  return [
    {
      title: '开放岗位数',
      value: source.open_positions || 0,
      icon: OfficeBuilding,
      color: '#409EFF',
      bgColor: 'rgba(64, 158, 255, 0.12)',
      route: '/position',
    },
    {
      title: '简历总数',
      value: source.resume_total || 0,
      icon: Document,
      color: '#67C23A',
      bgColor: 'rgba(103, 194, 58, 0.12)',
      route: '/resume',
    },
    {
      title: '待筛选简历',
      value: source.pending_resumes || 0,
      icon: Search,
      color: '#E6A23C',
      bgColor: 'rgba(230, 162, 60, 0.14)',
      route: '/resume',
    },
    {
      title: '面试中候选人',
      value: source.interviewing_count || 0,
      icon: Microphone,
      color: '#8E44AD',
      bgColor: 'rgba(142, 68, 173, 0.12)',
      route: '/recording',
    },
    {
      title: '今日自动采集',
      value: source.intake_today || 0,
      icon: Document,
      color: '#13A8A8',
      bgColor: 'rgba(19, 168, 168, 0.12)',
      route: '/intake',
    },
    {
      title: '文档同步总数',
      value: source.doc_synced_total || 0,
      icon: OfficeBuilding,
      color: '#2F54EB',
      bgColor: 'rgba(47, 84, 235, 0.12)',
      route: '/intake',
    },
    {
      title: '需人工确认',
      value: source.needs_review_total || 0,
      icon: Search,
      color: '#F56C6C',
      bgColor: 'rgba(245, 108, 108, 0.12)',
      route: '/intake',
    },
    {
      title: '待面试候选人',
      value: source.pending_interviews || 0,
      icon: Microphone,
      color: '#E6A23C',
      bgColor: 'rgba(230, 162, 60, 0.14)',
      route: '/intake',
    },
  ]
})

const todoList = computed(() => overview.value?.todos || [])
const interviewSchedule = computed(() => overview.value?.recent_interviews || [])
const activities = computed(() => overview.value?.recent_activities || [])

const getInterviewTimelineType = (statusName?: string) => {
  if (statusName === '已完成') return 'success'
  if (statusName === '转写中') return 'warning'
  if (statusName === '失败') return 'danger'
  return 'primary'
}

const handleStatsClick = (route?: string) => {
  if (!route) return
  router.push(route)
}

const handleTodoClick = (type: string) => {
  const routeMap: Record<string, string> = {
    resume_pending: '/resume',
    recording_pending: '/recording',
    summary_pending: '/recording',
    evaluation_pending: '/evaluation',
    intake_review: '/intake',
  }
  router.push(routeMap[type] || '/dashboard')
}

const handleInterviewClick = () => {
  router.push('/recording')
}

const handleActivityClick = (item: any) => {
  const title = item?.title || ''
  if (title.includes('摘要')) {
    router.push('/recording')
    return
  }
  if (title.includes('评价')) {
    router.push('/evaluation')
    return
  }
  if (title.includes('录音')) {
    router.push('/recording')
    return
  }
  if (title.includes('简历')) {
    router.push('/resume')
    return
  }
  ElMessage.info('当前动态未配置精确跳转，已保留模块入口')
}

const loadOverview = async () => {
  loading.value = true
  try {
    const res = await getDashboardOverviewApi()
    overview.value = res.data?.data || null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOverview()
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row,
.middle-row {
  margin-bottom: 0;
}

.stats-card {
  border: none;
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-card {
  cursor: pointer;
}

.stats-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.stats-card__content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  flex-shrink: 0;
}

.stats-info {
  min-width: 0;
}

.stats-title {
  margin-bottom: 8px;
  color: #909399;
  font-size: 14px;
}

.stats-value {
  margin-bottom: 8px;
  color: #303133;
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.stats-trend {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
}

.panel-card {
  border: none;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.todo-item:hover {
  border-color: #409eff;
  transform: translateX(2px);
  box-shadow: 0 8px 18px rgba(64, 158, 255, 0.08);
}

.todo-title {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.todo-meta {
  color: #909399;
  font-size: 13px;
}

.timeline-name {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.timeline-role {
  margin-top: 4px;
  color: #909399;
  font-size: 13px;
}

.timeline-entry {
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.activity-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.activity-title {
  margin-bottom: 6px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.activity-link {
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.activity-time {
  color: #909399;
  font-size: 13px;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .stats-card__content,
  .activity-item,
  .todo-item {
    align-items: flex-start;
    flex-direction: column;
  }

  .activity-time,
  .todo-meta {
    white-space: normal;
  }
}
</style>
