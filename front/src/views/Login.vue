<template>
  <div class="login-page">
    <section class="brand-panel">
      <div class="brand-overlay">
        <div class="brand-content">
          <div class="brand-badge">Recruiting AI Demo</div>
          <el-icon class="brand-icon"><OfficeBuilding /></el-icon>
          <h1>AI 招聘提效助手</h1>
          <p>
            面向企业微信、招聘群和腾讯在线文档的自动化采集 Demo，
            用 AI 把零散招聘消息转成可同步、可追踪、可分析的数据。
          </p>
          <ul class="brand-points">
            <li>群聊消息自动结构化抽取</li>
            <li>腾讯文档镜像表实时同步</li>
            <li>招聘进度看板自动更新</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="form-panel">
      <div class="login-card">
        <div class="login-header">
          <div class="logo-wrap">
            <el-icon class="logo-icon"><OfficeBuilding /></el-icon>
          </div>
          <div>
            <h2>AI 招聘提效助手</h2>
            <p>招聘数据自动采集与同步 Demo</p>
          </div>
        </div>

        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              clearable
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          </div>

          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
          <el-button
            size="large"
            class="demo-button"
            @click="handleDemoLogin"
          >
            演示模式登录
          </el-button>
          <p class="demo-tip">用于面试 Demo，本地写入登录态，不依赖后端账号。</p>
        </el-form>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Lock, OfficeBuilding, User } from '@element-plus/icons-vue'
import { loginApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

const rules: FormRules<typeof loginForm> = {
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur',
    },
    {
      min: 6,
      message: '密码长度不能少于6位',
      trigger: 'blur',
    },
  ],
}

const handleLogin = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true

  try {
    const { data } = await loginApi({
      hr_name: loginForm.username,
      password: loginForm.password,
    })

    userStore.setUser({
      username: loginForm.username,
      remember: loginForm.remember,
    })

    ElMessage.success(data?.message || '登录成功')
    router.push('/dashboard')
  } catch (error: any) {
    const message = error?.response?.data?.detail || '登录失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleDemoLogin = () => {
  userStore.setUser({
    username: 'Demo HR',
    remember: true,
    demo: true,
  })
  ElMessage.success('已进入演示模式')
  router.push('/intake')
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.brand-panel {
  position: relative;
  flex: 0 0 60%;
  overflow: hidden;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.brand-panel::before,
.brand-panel::after {
  position: absolute;
  border-radius: 50%;
  content: '';
  background: rgba(255, 255, 255, 0.12);
}

.brand-panel::before {
  top: -12%;
  left: -8%;
  width: 320px;
  height: 320px;
}

.brand-panel::after {
  right: 8%;
  bottom: 10%;
  width: 240px;
  height: 240px;
}

.brand-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 48px;
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 520px;
  color: #fff;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 13px;
  letter-spacing: 1px;
}

.brand-icon {
  margin-bottom: 24px;
  font-size: 56px;
}

.brand-content h1 {
  margin: 0 0 16px;
  font-size: 42px;
  font-weight: 700;
  line-height: 1.2;
}

.brand-content p {
  margin: 0 0 24px;
  font-size: 18px;
  line-height: 1.8;
  opacity: 0.95;
}

.brand-points {
  padding-left: 18px;
  margin: 0;
  display: grid;
  gap: 10px;
  font-size: 15px;
  line-height: 1.7;
}

.form-panel {
  display: flex;
  flex: 0 0 40%;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: #fff;
}

.login-card {
  width: min(100%, 420px);
  padding: 40px 36px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.logo-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(64, 158, 255, 0.12);
}

.logo-icon {
  font-size: 30px;
  color: #409eff;
}

.login-header h2 {
  margin: 0 0 6px;
  color: #303133;
  font-size: 24px;
  font-weight: 700;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-form :deep(.el-input__wrapper) {
  min-height: 44px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  min-height: 44px;
  font-weight: 600;
}

.demo-button {
  width: 100%;
  min-height: 44px;
  margin: 12px 0 0;
  font-weight: 600;
}

.demo-tip {
  margin: 10px 0 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.6;
  text-align: center;
}

@media (max-width: 768px) {
  .login-page {
    justify-content: center;
    padding: 24px;
  }

  .brand-panel {
    display: none;
  }

  .form-panel {
    flex: 1;
    padding: 0;
    background: transparent;
  }

  .login-card {
    padding: 32px 24px;
  }
}
</style>
