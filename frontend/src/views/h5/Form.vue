<template>
  <div class="form-container">
    <van-nav-bar title="术中压力性损伤风险评估" />
    <van-form @submit="onSubmit">
      <van-cell-group inset title="基本信息">
        <van-field
          v-model="formData.hospital_no"
          name="hospital_no"
          label="住院号"
          placeholder="请输入住院号"
          :rules="[{ required: true, message: '请填写住院号' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="评估指标">
        <van-field
          readonly
          clickable
          name="position"
          :model-value="columns.position.find(item => item.value === formData.position)?.text"
          label="术中体位"
          placeholder="点击选择"
          @click="showPicker.position = true"
          :rules="[{ required: true, message: '请选择术中体位' }]"
        />
        <van-popup v-model:show="showPicker.position" position="bottom">
          <van-picker
            :columns="columns.position"
            @confirm="onConfirm('position', $event)"
            @cancel="showPicker.position = false"
          />
        </van-popup>

        <van-field
          readonly
          clickable
          name="surgery_level"
          :model-value="columns.surgery_level.find(item => item.value === formData.surgery_level)?.text"
          label="手术等级"
          placeholder="点击选择"
          @click="showPicker.surgery_level = true"
          :rules="[{ required: true, message: '请选择手术等级' }]"
        />
        <van-popup v-model:show="showPicker.surgery_level" position="bottom">
          <van-picker
            :columns="columns.surgery_level"
            @confirm="onConfirm('surgery_level', $event)"
            @cancel="showPicker.surgery_level = false"
          />
        </van-popup>

        <van-field
          readonly
          clickable
          name="surgery_method"
          :model-value="columns.surgery_method.find(item => item.value === formData.surgery_method)?.text"
          label="手术方式"
          placeholder="点击选择"
          @click="showPicker.surgery_method = true"
          :rules="[{ required: true, message: '请选择手术方式' }]"
        />
        <van-popup v-model:show="showPicker.surgery_method" position="bottom">
          <van-picker
            :columns="columns.surgery_method"
            @confirm="onConfirm('surgery_method', $event)"
            @cancel="showPicker.surgery_method = false"
          />
        </van-popup>

        <van-field
          v-model="formData.height"
          type="digit"
          name="height"
          placeholder="例如 175"
          :rules="[{ required: true, message: '请填写身高' }]"
        >
          <template #label>身高 <span style="color: red;">(厘米)</span></template>
        </van-field>
        <van-field
          v-model="formData.weight"
          type="number"
          name="weight"
          placeholder="例如 65"
          :rules="[{ required: true, message: '请填写体重' }]"
        >
          <template #label>体重 <span style="color: red;">(KG)</span></template>
        </van-field>

        <van-field
          v-model="formData.temperature"
          type="number"
          name="temperature"
          label="诱导期低体温(℃)"
          placeholder="请填写体温"
          :rules="[{ required: true, message: '请填写体温' }]"
        />

        <van-field
          v-model="formData.glucose"
          type="number"
          name="glucose"
          label="葡萄糖(mmol/L)"
          placeholder="请填写葡萄糖"
          :rules="[{ required: true, message: '请填写葡萄糖' }]"
        />

        <van-field
          v-model="formData.albumin"
          type="number"
          name="albumin"
          label="白蛋白(g/L)"
          placeholder="请填写白蛋白"
          :rules="[{ required: true, message: '请填写白蛋白' }]"
        />

        <van-field
          v-model="formData.surgery_time"
          type="digit"
          name="surgery_time"
          placeholder="请输入预计手术时间"
          :rules="[{ required: true, message: '请填写手术时间' }]"
        >
          <template #label>预计手术时间<span style="color: red;">(分)</span></template>
        </van-field>

      </van-cell-group>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          计算风险
        </van-button>
      </div>
    </van-form>

    <van-tabbar route>
      <van-tabbar-item replace to="/h5/form" icon="home-o">决策辅助</van-tabbar-item>
      <van-tabbar-item replace to="/h5/my" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'

const router = useRouter()
const submitting = ref(false)

const getInitialData = () => ({
  hospital_no: '',
  position: '',
  surgery_level: '',
  surgery_method: '',
  height: '',
  weight: '',
  temperature: '',
  glucose: '',
  albumin: '',
  surgery_time: ''
})

const formData = reactive(getInitialData())

const showPicker = reactive({
  position: false,
  surgery_level: false,
  surgery_method: false
})

const columns = {
  position: [
    { text: '中转体位', value: 1 },
    { text: '侧卧位', value: 2 },
    { text: '俯卧位', value: 3 },
    { text: '仰卧位', value: 4 },
    { text: '截石位', value: 5 }
  ],
  surgery_level: [
    { text: '四级', value: 1 },
    { text: '三级', value: 2 },
    { text: '一级或二级', value: 3 }
  ],
  surgery_method: [
    { text: '中转开腹', value: 1 },
    { text: '开腹', value: 2 },
    { text: '浅表或深部组织', value: 3 },
    { text: '微创(腔镜)', value: 4 }
  ]
}

const onConfirm = (field, { selectedOptions }) => {
  formData[field] = selectedOptions[0].value
  showPicker[field] = false
}

const onSubmit = async () => {
  submitting.value = true
  try {
    const res = await api.post('/records', formData)
    Object.assign(formData, getInitialData()) // Clean up for next time
    router.push({ name: 'H5Result', query: { risk_level: res.risk_level, suggestion: res.suggestion } })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-container {
  padding-bottom: 60px;
}
</style>