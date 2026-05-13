import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // --- H5 User Pages ---
  {
    path: '/',
    redirect: '/h5/login'
  },
  {
    path: '/h5/login',
    name: 'H5Login',
    component: () => import('../views/h5/Login.vue')
  },
  {
    path: '/h5/form',
    name: 'H5Form',
    meta: { requiresAuth: true },
    component: () => import('../views/h5/Form.vue')
  },
  {
    path: '/h5/result',
    name: 'H5Result',
    meta: { requiresAuth: true },
    component: () => import('../views/h5/Result.vue')
  },
  {
    path: '/h5/my',
    name: 'H5My',
    meta: { requiresAuth: true },
    component: () => import('../views/h5/My.vue')
  },
  
  // --- Admin Pages ---
  {
    path: '/admin',
    redirect: '/admin/login'
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/Login.vue')
  },
  {
    path: '/admin/layout',
    name: 'AdminLayout',
    meta: { requiresAdmin: true },
    component: () => import('../views/admin/Layout.vue'),
    redirect: '/admin/records',
    children: [
      {
        path: '/admin/records',
        name: 'AdminRecords',
        component: () => import('../views/admin/Records.vue')
      },
      {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('../views/admin/Users.vue')
      },
      {
        path: '/admin/settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/Settings.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const adminToken = localStorage.getItem('adminToken')
  
  if (to.meta.requiresAuth && !token) {
    next('/h5/login')
  } else if (to.meta.requiresAdmin && !adminToken) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router
