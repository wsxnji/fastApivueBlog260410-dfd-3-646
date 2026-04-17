import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/create',
    name: 'CreatePost',
    component: () => import('../views/CreatePost.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/edit/:id',
    name: 'EditPost',
    component: () => import('../views/EditPost.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/admin')
  } else {
    next()
  }
})

export default router
