<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <div class="brand">
          <div class="brand-logo">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <span class="brand-name">AI 招聘提效助手</span>
        </div>

        <el-button v-if="showBackButton" class="back-btn" text @click="handleBack">
          <el-icon size="18"><ArrowLeft /></el-icon>
          <span>返回</span>
        </el-button>

        <el-button class="collapse-btn" text @click="toggleCollapse">
          <el-icon size="20">
            <component :is="isCollapse ? Expand : Fold" />
          </el-icon>
        </el-button>
      </div>

      <div class="header-right">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-entry">
            <el-avatar :size="36" class="user-avatar">HR</el-avatar>
            <span class="user-name">{{ userStore.displayName }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="layout-body">
      <el-aside :width="asideWidth" class="layout-aside">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
          class="side-menu"
        >
          <el-menu-item
            v-for="item in menuItems"
            :key="item.path"
            :index="item.path"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="layout-main" :style="{ marginLeft: asideWidth }">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  ArrowDown,
  Document,
  Expand,
  Fold,
  House,
  Microphone,
  OfficeBuilding,
  QuestionFilled,
  ScaleToOriginal,
  Search,
  Star,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const menuItems = [
  { title: '工作台', path: '/dashboard', icon: House },
  { title: '数据采集', path: '/intake', icon: Document },
  { title: '岗位管理', path: '/position', icon: OfficeBuilding },
  { title: '简历管理', path: '/resume', icon: Document },
  { title: '智能筛选', path: '/screening', icon: Search },
  { title: '面试题生成', path: '/question', icon: QuestionFilled },
  { title: '录音管理', path: '/recording', icon: Microphone },
  { title: '面试评价', path: '/evaluation', icon: Star },
  { title: '候选人对比', path: '/comparison', icon: ScaleToOriginal },
]

const asideWidth = computed(() => (isCollapse.value ? '64px' : '200px'))
const activeMenu = computed(() => route.path)
const rootRoutes = ['/dashboard', '/intake', '/position', '/resume', '/screening', '/question', '/recording', '/evaluation', '/comparison']
const showBackButton = computed(() => !rootRoutes.includes(route.path))

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const getFallbackRoute = () => {
  if (route.path.startsWith('/position/')) return '/position'
  if (route.path.startsWith('/resume/')) return '/resume'
  if (route.path.startsWith('/summary/')) return '/recording'
  if (route.path.startsWith('/evaluation/')) return '/evaluation'
  return '/dashboard'
}

const handleBack = () => {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push(getFallbackRoute())
}

const handleCommand = (command: string) => {
  if (command === 'profile') {
    ElMessage.info('演示版本暂不包含个人信息配置')
    return
  }

  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.layout-header {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: #fff;
  font-size: 20px;
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.2);
}

.brand-name {
  color: #303133;
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
}

.collapse-btn {
  color: #409eff;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
  cursor: pointer;
  outline: none;
}

.user-avatar {
  background: #409eff;
  color: #fff;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.layout-body {
  padding-top: 60px;
}

.layout-aside {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  z-index: 999;
  overflow: hidden;
  background: #fff;
  border-right: 1px solid #ebeef5;
  transition: width 0.2s ease;
}

.side-menu {
  height: 100%;
  border-right: none;
}

.side-menu:not(.el-menu--collapse) {
  width: 200px;
}

.layout-main {
  min-height: calc(100vh - 60px);
  padding: 16px;
  background: #f5f7fa;
  transition: margin-left 0.2s ease;
}

@media (max-width: 768px) {
  .layout-header {
    padding: 0 16px;
  }

  .brand-name,
  .user-name {
    display: none;
  }

  .layout-aside {
    width: 64px !important;
  }

  .layout-main {
    margin-left: 64px !important;
    padding: 12px;
  }
}
</style>
