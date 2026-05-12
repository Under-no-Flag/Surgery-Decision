<template>
  <div class="admin-login-wrapper">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>管理系统登录</span>
        </div>
      </template>
      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" class="w-full" @click="handleLogin" :loading="loading">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await api.post('/admin/login', form)
    localStorage.setItem('adminToken', res.token)
    router.replace('/admin/layout')
  } catch (error) {
    // API intercepts errors
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
.card-header {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
}
.w-full {
  width: 100%;
}
</style>