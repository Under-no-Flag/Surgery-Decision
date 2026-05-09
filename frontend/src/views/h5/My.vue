<template>
  <div class="my-container">
    <van-nav-bar title="我的" />
    
    <div class="user-info">
      <div class="avatar-ph" v-if="!user.avatar">{{ user.nickname?.[0] || 'U' }}</div>
      <img v-else :src="user.avatar" class="avatar" />
      <div class="nickname">{{ user.nickname || '未登录用户' }}</div>
    </div>
    
    <van-cell-group title="我的录入记录" class="record-list">
      <van-collapse v-model="activeNames">
        <van-collapse-item 
          v-for="item in records" 
          :key="item.id" 
          :name="item.id"
          :title="'住院号: ' + item.hospital_no" 
          :label="item.created_at"
          :value="item.risk_level"
        >
          <div class="record-detail">
            <p><strong>术中体位:</strong> {{ formatPosition(item.position) }}</p>
            <p><strong>手术等级:</strong> {{ formatLevel(item.surgery_level) }}</p>
            <p><strong>手术方式:</strong> {{ formatMethod(item.surgery_method) }}</p>
            <p><strong>身高(cm):</strong> {{ item.height }}</p>
            <p><strong>体重(kg):</strong> {{ item.weight }}</p>
            <p><strong>BMI:</strong> {{ typeof item.bmi === 'number' ? item.bmi.toFixed(2) : item.bmi }}</p>
            <p><strong>麻醉诱导时体温(℃):</strong> {{ item.temperature }}</p>
            <p><strong>术前葡萄糖(mmol/L):</strong> {{ item.glucose }}</p>
            <p><strong>术前白蛋白(g/L):</strong> {{ item.albumin }}</p>
            <p><strong>手术时间(小时):</strong> {{ item.surgery_time ? (item.surgery_time / 60).toFixed(1) : '' }}</p>
            <p><strong>计算风险值(P):</strong> {{ (item.p_value * 100).toFixed(2) }}%</p>
            <div style="text-align: right; margin-top: 10px;">
              <van-button size="small" type="danger" @click.stop="deleteRecord(item.id)">删除记录</van-button>
            </div>
          </div>
        </van-collapse-item>
      </van-collapse>
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
import { showConfirmDialog, showToast } from 'vant'
import api from '../../utils/api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const records = ref([])
const activeNames = ref([])


const formatPosition = (v) => ({1: '中转体位', 2: '侧卧位', 3: '俯卧位', 4: '仰卧位', 5: '截石位'})[v] || '未知';
const formatLevel = (v) => ({1: '四级', 2: '三级', 3: '一级或二级'})[v] || '未知';
const formatMethod = (v) => ({1: '中转开腹', 2: '开腹', 3: '浅表或深部组织', 4: '微创(腔镜)'})[v] || '未知';

onMounted(async () => {
  fetchRecords()
})

const fetchRecords = async () => {
  try {
    records.value = await api.get('/records/my')
  } catch (e) {}
}

const deleteRecord = (id) => {
  showConfirmDialog({
    title: '删除记录',
    message: '确定要删除这条评估记录吗？',
  }).then(async () => {
    try {
      await api.delete(`/records/${id}`)
      showToast('删除成功')
      fetchRecords()
    } catch (e) {
      showToast('删除失败')
    }
  }).catch(() => {
    // on cancel
  });
}

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
.record-detail p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}
.record-detail strong {
  color: #333;
}
</style>