import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/guest',
      component: () => import('@/views/guest/GuestLayout.vue'),
      meta: { role: 'guest' },
      children: [
        {
          path: '',
          redirect: '/guest/preference',
        },
        {
          path: 'preference',
          name: 'guest-preference',
          component: () => import('@/views/guest/GuestProfileView.vue'),
        },
        {
          path: 'profile',
          redirect: '/guest/preference',
        },
        {
          path: 'rooms',
          name: 'guest-rooms',
          component: () => import('@/views/guest/GuestRoomsView.vue'),
        },
        {
          path: 'services',
          name: 'guest-services',
          component: () => import('@/views/guest/GuestServicesView.vue'),
        },
      ],
    },
    {
      path: '/manager',
      component: () => import('@/views/manager/ManagerLayout.vue'),
      meta: { role: 'manager' },
      children: [
        {
          path: '',
          redirect: '/manager/twin',
        },
        {
          path: 'twin',
          name: 'manager-twin',
          component: () => import('@/views/manager/ManagerTwinView.vue'),
        },
        {
          path: 'monitor',
          name: 'manager-monitor',
          component: () => import('@/views/manager/ManagerMonitorView.vue'),
        },
        {
          path: 'rooms',
          name: 'manager-rooms',
          component: () => import('@/views/manager/ManagerRoomsView.vue'),
        },
        {
          path: 'requests',
          name: 'manager-requests',
          component: () => import('@/views/manager/ManagerRequestsView.vue'),
        },
        {
          path: 'staff',
          name: 'manager-staff',
          component: () => import('@/views/manager/ManagerStaffView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isLoggedIn) {
      return auth.role === 'manager' ? '/manager/twin' : '/guest/preference'
    }
    return true
  }
  if (!auth.isLoggedIn) return '/login'
  if (to.meta.role && auth.role !== to.meta.role) {
    return auth.role === 'manager' ? '/manager/twin' : '/guest/preference'
  }
  return true
})

export default router
