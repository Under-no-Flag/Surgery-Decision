<template>
  <div class="result-container">
    <van-nav-bar title="风险评估结果" left-arrow @click-left="goBack" />
    
    <div class="result-box" :class="riskClass">
      <h2>{{ riskLevel }}</h2>
      <p class="suggestion-title">护理建议：</p>
      <div class="suggestion-content">
        {{ suggestion }}
      </div>
    </div>
    
    <div style="margin: 30px 16px;">
      <van-button round block type="primary" @click="goBack">返回继续录入</van-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const riskLevel = route.query.risk_level || '未知'
const suggestion = route.query.suggestion || '暂无建议'

const riskClass = computed(() => {
  if (riskLevel === '低风险') return 'low'
  if (riskLevel === '中风险') return 'medium'
  if (riskLevel === '高风险') return 'high'
  return ''
})

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.result-box {
  margin: 20px;
  padding: 20px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.result-box h2 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 20px;
}
.low h2 { color: #07c160; }
.medium h2 { color: #ff976a; }
.high h2 { color: #ee0a24; }
.suggestion-title {
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 16px;
}
.suggestion-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}
</style>