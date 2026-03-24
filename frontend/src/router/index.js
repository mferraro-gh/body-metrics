import { createRouter, createWebHistory } from 'vue-router'
import HomeView      from '../views/HomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import UploadView    from '../views/UploadView.vue'
import CompareView   from '../views/CompareView.vue'
import SettingsView  from '../views/SettingsView.vue'

const routes = [
  { path: '/',          component: HomeView },
  { path: '/dashboard', component: DashboardView },
  { path: '/upload',    component: UploadView },
  { path: '/compare',   component: CompareView },
  { path: '/settings',  component: SettingsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
