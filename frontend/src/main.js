import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// Vant
import 'vant/lib/index.css';
import { Button, Field, CellGroup, Form, Picker, Popup, NavBar, Tabbar, TabbarItem, RadioGroup, Radio } from 'vant';

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(router)
app.use(createPinia())

// Use Vant components
app.use(Button)
app.use(Field)
app.use(CellGroup)
app.use(Form)
app.use(Picker)
app.use(Popup)
app.use(NavBar)
app.use(Tabbar)
app.use(TabbarItem)
app.use(RadioGroup)
app.use(Radio)

app.use(ElementPlus)

app.mount('#app')
