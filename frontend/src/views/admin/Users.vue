<template>
  <div class="users-container">
    <el-card>
      <div class="page-header">
        <h2>用户账号管理</h2>
        <el-button type="primary" @click="openCreate">新增用户</el-button>
      </div>

      <el-table :data="users" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="账号" min-width="160">
          <template #default="{ row }">
            {{ row.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="姓名/昵称" min-width="160">
          <template #default="{ row }">
            {{ row.nickname || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="record_count" label="评估记录数" width="120" />
        <el-table-column prop="is_admin" label="权限" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'success' : 'info'">
              {{ row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="openReset(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editor.visible" :title="editor.form.id ? '编辑用户' : '新增用户'" width="520px">
      <el-form :model="editor.form" label-width="90px">
        <el-form-item label="账号">
          <el-input v-model.trim="editor.form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="姓名/昵称">
          <el-input v-model.trim="editor.form.nickname" placeholder="请输入姓名或昵称" />
        </el-form-item>
        <el-form-item v-if="!editor.form.id" label="密码">
          <el-input v-model="editor.form.password" type="password" show-password placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="权限">
          <el-switch v-model="editor.form.is_admin" active-text="管理员" inactive-text="普通用户" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editor.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetter.visible" title="重置密码" width="420px">
      <el-form label-width="90px">
        <el-form-item label="账号">
          <el-input :model-value="resetter.user?.username || '-'" disabled />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="resetter.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="resetter.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetter.visible = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="resetPassword">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../utils/api'

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)

const editor = reactive({
  visible: false,
  form: {
    id: null,
    username: '',
    nickname: '',
    password: '',
    is_admin: false
  }
})

const resetter = reactive({
  visible: false,
  user: null,
  password: '',
  confirmPassword: ''
})

onMounted(() => {
  fetchUsers()
})

const fetchUsers = async () => {
  loading.value = true
  try {
    users.value = await api.get('/admin/users')
  } finally {
    loading.value = false
  }
}

const resetEditor = () => {
  Object.assign(editor.form, {
    id: null,
    username: '',
    nickname: '',
    password: '',
    is_admin: false
  })
}

const openCreate = () => {
  resetEditor()
  editor.visible = true
}

const openEdit = (row) => {
  Object.assign(editor.form, {
    id: row.id,
    username: row.username || '',
    nickname: row.nickname || '',
    password: '',
    is_admin: Boolean(row.is_admin)
  })
  editor.visible = true
}

const validateEditor = () => {
  if (!editor.form.username) {
    ElMessage.warning('请输入账号')
    return false
  }
  if (!editor.form.id && !editor.form.password) {
    ElMessage.warning('请输入初始密码')
    return false
  }
  return true
}

const saveUser = async () => {
  if (!validateEditor()) return

  saving.value = true
  try {
    const payload = {
      username: editor.form.username,
      nickname: editor.form.nickname,
      is_admin: editor.form.is_admin
    }
    if (editor.form.id) {
      await api.put(`/admin/users/${editor.form.id}`, payload)
      ElMessage.success('用户已更新')
    } else {
      await api.post('/admin/users', {
        ...payload,
        password: editor.form.password
      })
      ElMessage.success('用户已创建')
    }
    editor.visible = false
    fetchUsers()
  } finally {
    saving.value = false
  }
}

const openReset = (row) => {
  resetter.user = row
  resetter.password = ''
  resetter.confirmPassword = ''
  resetter.visible = true
}

const resetPassword = async () => {
  if (!resetter.password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (resetter.password !== resetter.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  resetting.value = true
  try {
    await api.patch(`/admin/users/${resetter.user.id}/password`, {
      password: resetter.password
    })
    ElMessage.success('密码已重置')
    resetter.visible = false
  } finally {
    resetting.value = false
  }
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户「${row.username || row.nickname || row.id}」吗？该用户的评估记录也会被删除。`, '删除用户', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await api.delete(`/admin/users/${row.id}`)
    ElMessage.success('用户已删除')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}
</style>
