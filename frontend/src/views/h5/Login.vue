<template>
  <div class="login-page">
    <div class="brand">
      <div class="title">压力性损伤风险评估系统</div>
      <div class="subtitle">账号登录后可录入评估并查看历史记录</div>
    </div>

    <div class="auth-card">
      <div class="mode-switch">
        <button :class="{ active: mode === 'login' }" type="button" @click="switchMode('login')">登录</button>
        <button :class="{ active: mode === 'register' }" type="button" @click="switchMode('register')">注册</button>
      </div>

      <van-form @submit="handleSubmit">
        <van-cell-group inset>
          <van-field
            v-model.trim="form.username"
            name="username"
            label="账号"
            placeholder="请输入账号"
            autocomplete="username"
            :rules="[{ required: true, message: '请输入账号' }]"
          />
          <van-field
            v-if="mode === 'register'"
            v-model.trim="form.nickname"
            name="nickname"
            label="姓名"
            placeholder="请输入姓名或昵称"
          />
          <van-field
            v-model="form.password"
            name="password"
            label="密码"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            :rules="[{ required: true, message: '请输入密码' }]"
          />
          <van-field
            v-if="mode === 'register'"
            v-model="form.confirmPassword"
            name="confirmPassword"
            label="确认密码"
            type="password"
            placeholder="请再次输入密码"
            autocomplete="new-password"
            :rules="[{ required: true, message: '请确认密码' }]"
          />
        </van-cell-group>

        <div class="submit-area">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            {{ mode === 'login' ? '登录' : '注册并登录' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import api from '../../utils/api'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const switchMode = (nextMode) => {
  mode.value = nextMode
  form.password = ''
  form.confirmPassword = ''
}

const saveSession = (res) => {
  localStorage.setItem('token', res.token)
  localStorage.setItem('user', JSON.stringify(res.user))
  router.replace('/h5/form')
}

const handleSubmit = async () => {
  if (mode.value === 'register' && form.password !== form.confirmPassword) {
    showToast('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    const url = mode.value === 'login' ? '/auth/login' : '/auth/register'
    const payload = {
      username: form.username,
      password: form.password
    }
    if (mode.value === 'register') {
      payload.nickname = form.nickname
    }
    const res = await api.post(url, payload)
    saveSession(res)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 72px 18px 32px;
  background: linear-gradient(180deg, #edf6ff 0%, #f7f8fa 45%, #f7f8fa 100%);
}

.brand {
  margin-bottom: 28px;
  text-align: center;
}

.title {
  color: #17233d;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.35;
}

.subtitle {
  margin-top: 10px;
  color: #6b7280;
  font-size: 14px;
}

.auth-card {
  overflow: hidden;
  padding: 18px 0 20px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(31, 45, 61, 0.08);
}

.mode-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 0 16px 16px;
  padding: 4px;
  border-radius: 8px;
  background: #eef2f7;
}

.mode-switch button {
  height: 38px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #5f6b7a;
  font-size: 15px;
}

.mode-switch button.active {
  background: #fff;
  color: #1989fa;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(31, 45, 61, 0.08);
}

.submit-area {
  margin: 20px 16px 0;
}
</style>
