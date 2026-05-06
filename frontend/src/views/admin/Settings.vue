<template>
  <div class="settings-container">
    <el-card>
      <h2>系统设置 (公式参数与建议配置)</h2>
      <el-form :model="form" label-width="150px" style="max-width: 800px; margin-top: 20px;" v-loading="loading">
        <h3>计算公式系数</h3>
        <el-form-item label="基础常量 (Base)">
          <el-input-number v-model="form.base" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="术中体位">
          <el-input-number v-model="form.position" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="手术等级">
          <el-input-number v-model="form.surgery_level" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="手术方式">
          <el-input-number v-model="form.surgery_method" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="BMI 系数">
          <el-input-number v-model="form.bmi" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="诱导低体温">
          <el-input-number v-model="form.hypothermia" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="白蛋白异常">
          <el-input-number v-model="form.albumin_abnormal" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="葡萄糖异常">
          <el-input-number v-model="form.glucose_abnormal" :precision="4" :step="0.1" />
        </el-form-item>
        <el-form-item label="预计手术时间">
          <el-input-number v-model="form.surgery_time" :precision="4" :step="0.001" />
        </el-form-item>

        <el-divider />
        <h3>风险建议文本</h3>
        <el-form-item label="低风险建议 (<30%)">
          <el-input type="textarea" :rows="4" v-model="form.suggestion_low" />
        </el-form-item>
        <el-form-item label="中风险建议 (30%-48%)">
          <el-input type="textarea" :rows="4" v-model="form.suggestion_medium" />
        </el-form-item>
        <el-form-item label="高风险建议 (>48%)">
          <el-input type="textarea" :rows="4" v-model="form.suggestion_high" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../utils/api'

const loading = ref(false)
const form = ref({})

onMounted(async () => {
  fetchConfigs()
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const data = await api.get('/admin/configs')
    form.value = data
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  loading.value = true
  try {
    await api.post('/admin/configs', form.value)
    ElMessage.success('配置保存成功')
  } finally {
    loading.value = false
  }
}
</script>