import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn } from '../stores/auth';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/models/:id',
    name: 'model-detail',
    component: () => import('../views/ModelDetailView.vue'),
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../views/HistoryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }
  if (to.name === 'login' && isLoggedIn()) {
    return { path: '/' };
  }
  return true;
});

export default router;
