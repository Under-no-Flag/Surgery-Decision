<template>
  <div class="my-container">
    <van-nav-bar title="我的" />
    
    <div class="user-info">
      <div class="avatar-ph" v-if="!user.avatar">{{ user.nickname?.[0] || 'U' }}</div>
      <img v-else :src="user.avatar" class="avatar" />
      <div class="nickname">{{ user.nickname || '未登录用户' }}</div>
    </div>
    
    <van-cell-group title="我的录入记录" class="record-list">
      <van-cell 
        v-for="item in records" 
        :key="item.id" 
        :title="'住院号: ' + item.hospital_no" 
        :label="item.created_at"
        :value="item.risk_level"
      />
      <div v-if="records.length === 0" class="empty">暂无记录</div>
    </van-cell-group>

    <div style="margin: 30px 16px;">
      <van-button round block type="default" @click="logout">退出登录</van-button>
    </div>
    
    <van-tabbar route>
      <van-tabbar-item replace to="/h5/form" icon="home-o">决策辅助</van-tabbar-item>
      <van-tabbar-item replace to="/h5/my" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const records = ref([])

onMounted(async () => {
  try {
    records.value = await api.get('/records/my')
  } catch (e) {}
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.replace('/h5/login')
}
</script>

<style scoped>
.my-container {
  padding-bottom: 60px;
}
.user-info {
  background: white;
  padding: 30px 20px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.avatar, .avatar-ph {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-right: 15px;
}
.avatar-ph {
  background: #1989fa;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
}
.nickname {
  font-size: 18px;
  font-weight: bold;
}
.empty {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>