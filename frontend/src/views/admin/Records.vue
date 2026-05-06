<template>
  <div class="records-container">
    <el-card>
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between;">
        <h2>录入数据管理</h2>
        <el-button type="primary" @click="exportExcel">导出 Excel</el-button>
      </div>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <el-descriptions>
              <el-descriptions-item label="术后皮肤情况">{{ formatSkin(row.postop_skin) }}</el-descriptions-item>
              <el-descriptions-item label="术中体位">{{ formatPosition(row.position) }}</el-descriptions-item>
              <el-descriptions-item label="手术等级">{{ formatLevel(row.surgery_level) }}</el-descriptions-item>
              <el-descriptions-item label="手术方式">{{ formatMethod(row.surgery_method) }}</el-descriptions-item>
              <el-descriptions-item label="身高(m)">{{ row.height }}</el-descriptions-item>
              <el-descriptions-item label="体重(kg)">{{ row.weight }}</el-descriptions-item>
              <el-descriptions-item label="BMI">{{ row.bmi }}</el-descriptions-item>
              <el-descriptions-item label="诱导期低体温">{{ row.hypothermia ? '<36°C' : '≥36°C' }}</el-descriptions-item>
              <el-descriptions-item label="葡萄糖异常">{{ row.glucose_abnormal ? '异常' : '正常' }}</el-descriptions-item>
              <el-descriptions-item label="白蛋白异常">{{ row.albumin_abnormal ? '异常' : '正常' }}</el-descriptions-item>
              <el-descriptions-item label="手术时间(分)">{{ row.surgery_time }}</el-descriptions-item>
              <el-descriptions-item label="计算风险值(P)">{{ row.p_value != null ? (row.p_value * 100).toFixed(2) + '%' : '-' }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="hospital_no" label="住院号" width="180" />
        <el-table-column prop="user" label="录入人" width="150" />
        <el-table-column prop="risk_level" label="评估风险等级" width="120">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)">{{ row.risk_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="录入时间" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-popconfirm title="确定要删除这条记录吗？" @confirm="deleteRecord(row.id)">
              <template #reference>
                <el-button type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../utils/api'
// 生产环境可使用 xlsx 库在前端导出或者请求后端的导出接口
import * as XLSX from 'xlsx'

const tableData = ref([])
const loading = ref(false)

const formatSkin = (v) => ({1: '压红', 2: '一期', 3: '二期', 4: '其他'})[v] || '未知';
const formatPosition = (v) => ({1: '中转体位', 2: '侧卧位', 3: '俯卧位', 4: '仰卧位', 5: '截石位'})[v] || '未知';
const formatLevel = (v) => ({1: '四级', 2: '三级', 3: '一级或二级'})[v] || '未知';
const formatMethod = (v) => ({1: '中转开腹', 2: '开腹', 3: '浅表或深部组织', 4: '微创(腔镜)'})[v] || '未知';

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

const deleteRecord = async (id) => {
  try {
    await api.delete(`/admin/records/${id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const exportExcel = () => {
  const ws = XLSX.utils.json_to_sheet(tableData.value.map(r => ({
    '记录ID': r.id,
    '住院号': r.hospital_no,
    '微信昵称': r.user,
    '风险等级': r.risk_level,
    '计算风险概率': r.p_value != null ? (r.p_value * 100).toFixed(2) + '%' : '',
    '术后皮肤情况': formatSkin(r.postop_skin),
    '术中体位': formatPosition(r.position),
    '手术等级': formatLevel(r.surgery_level),
    '手术方式': formatMethod(r.surgery_method),
    '身高(m)': r.height,
    '体重(kg)': r.weight,
    'BMI': r.bmi,
    '诱导期低体温': r.hypothermia ? '<36°C' : '≥36°C',
    '葡萄糖异常': r.glucose_abnormal ? '异常' : '正常',
    '白蛋白异常': r.albumin_abnormal ? '异常' : '正常',
    '手术时间(分)': r.surgery_time,
    '录入时间': r.created_at
  })))
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "评估记录")
  XLSX.writeFile(wb, "术中压力性损伤评估记录.xlsx")
}
</script>