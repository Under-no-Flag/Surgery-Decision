<template>
  <div class="login-wrapper">
    <div class="title">压力性损伤风险评估系统</div>
    <van-button type="primary" block @click="doWechatLogin" v-if="!isWechatCallback">
      微信授权登录
    </van-button>
    <div class="loading" v-else>
      登录中...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../utils/api'

const router = useRouter()
const route = useRoute()
const isWechatCallback = ref(false)

const appId = 'wx447816e4e2d99865'

onMounted(() => {
  const code = route.query.code
  if (code) {
    isWechatCallback.ref = true
    handleCallback(code)
  }
})

const doWechatLogin = () => {
  const redirectUri = encodeURIComponent(window.location.origin + '/h5/login')
  const url = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect`
  window.location.href = url
}

const handleCallback = async (code) => {
  try {
    const res = await api.post('/wechat/login', { code })
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
    router.replace('/h5/form')
  } catch (error) {
    // 错误在拦截器已提示
  }
}
</script>

<style scoped>
.login-wrapper {
  padding: 50px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100vh;
  box-sizing: border-box;
}
.title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 50px;
}
.loading {
  text-align: center;
  color: #999;
}
</style>