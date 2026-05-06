<template>
  <el-container class="admin-layout">
    <el-aside width="200px" style="background-color: #304156;">
      <div class="logo">压力性损伤辅助系统后台</div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/admin/records">
          <el-icon><Document /></el-icon>
          <span>记录管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置 (公式配置)</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; justify-content: flex-end; align-items: center; border-bottom: 1px solid #dcdfe6; background: #fff;">
        <span style="margin-right: 15px;">管理员</span>
        <el-button type="danger" size="small" @click="logout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

const logout = () => {
  localStorage.removeItem('adminToken')
  router.replace('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-weight: bold;
  font-size: 16px;
  background-color: #2b3643;
}
.el-menu-vertical {
  border-right: none;
}
</style>