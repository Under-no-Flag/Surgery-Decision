<template>
  <div class="records-container">
    <el-card>
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between;">
        <h2>录入数据管理</h2>
        <el-button type="primary" @click="exportExcel">导出 Excel</el-button>
      </div>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="hospital_no" label="住院号" width="180" />
        <el-table-column prop="user" label="录入人(微信昵称)" width="150" />
        <el-table-column prop="risk_level" label="评估风险等级" width="120">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)">{{ row.risk_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="录入时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
// 生产环境可使用 xlsx 库在前端导出或者请求后端的导出接口
import * as XLSX from 'xlsx'

const tableData = ref([])
const loading = ref(false)

onMounted(async () => {
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = await api.get('/admin/records')
  } finally {
    loading.value = false
  }
}

const getRiskType = (level) => {
  if (level === '低风险') return 'success'
  if (level === '中风险') return 'warning'
  if (level === '高风险') return 'danger'
  return 'info'
}

const exportExcel = () => {
  const ws = XLSX.utils.json_to_sheet(tableData.value.map(r => ({
    '记录ID': r.id,
    '住院号': r.hospital_no,
    '微信昵称': r.user,
    '风险等级': r.risk_level,
    '录入时间': r.created_at
  })))
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "评估记录")
  XLSX.writeFile(wb, "术中压力性损伤评估记录.xlsx")
}
</script>