import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/Layout.vue'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import Intake from '@/views/Intake.vue'
import Position from '@/views/Position.vue'
import PositionForm from '@/views/PositionForm.vue'
import PositionDetail from '@/views/PositionDetail.vue'
import Resume from '@/views/Resume.vue'
import ResumeDetail from '@/views/ResumeDetail.vue'
import ResumeUpload from '@/views/ResumeUpload.vue'
import Screening from '@/views/Screening.vue'
import Question from '@/views/Question.vue'
import Recording from '@/views/Recording.vue'
import Summary from '@/views/Summary.vue'
import EvaluationEntry from '@/views/EvaluationEntry.vue'
import Evaluation from '@/views/Evaluation.vue'
import Comparison from '@/views/Comparison.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'intake', name: 'Intake', component: Intake },
      { path: 'position', name: 'Position', component: Position },
      { path: 'position/create', name: 'PositionCreate', component: PositionForm },
      { path: 'position/:id', name: 'PositionDetail', component: PositionDetail },
      { path: 'position/:id/edit', name: 'PositionEdit', component: PositionForm },
      { path: 'resume', name: 'Resume', component: Resume },
      { path: 'resume/upload', name: 'ResumeUpload', component: ResumeUpload },
      { path: 'resume/:id', name: 'ResumeDetail', component: ResumeDetail },
      { path: 'screening', name: 'Screening', component: Screening },
      { path: 'question', name: 'Question', component: Question },
      { path: 'recording', name: 'Recording', component: Recording },
      { path: 'summary/:recordingId', name: 'Summary', component: Summary },
      { path: 'evaluation', name: 'EvaluationEntry', component: EvaluationEntry },
      { path: 'evaluation/:resumeId', name: 'Evaluation', component: Evaluation },
      { path: 'comparison', name: 'Comparison', component: Comparison },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const raw = localStorage.getItem('hr-assistant-user')
  const isLoggedIn = !!raw

  if (to.meta.public) {
    if (to.path === '/login' && isLoggedIn) {
      return '/dashboard'
    }
    return true
  }

  if (!isLoggedIn) {
    return '/login'
  }

  return true
})

export default router
