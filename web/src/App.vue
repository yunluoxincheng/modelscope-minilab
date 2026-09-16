<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { UserFilled, SwitchButton, Coin } from '@element-plus/icons-vue';
import { authStore, clearAuth, displayName } from './stores/auth';

const route = useRoute();
const router = useRouter();

const navs = [
  { path: '/', label: '模型广场' },
  { path: '/history', label: '识别记录', auth: true },
  { path: '/about', label: '关于' },
];

const logged = computed(() => !!authStore.token);
const name = computed(() => displayName());
const avatarChar = computed(() => (name.value || '客').slice(0, 1).toUpperCase());

function isActive(nav) {
  if (nav.path === '/') return route.path === '/';
  return route.path.startsWith(nav.path);
}

function handleCommand(cmd) {
  if (cmd === 'logout') {
    clearAuth();
    ElMessage.success('已退出登录');
    router.push('/');
  } else if (cmd === 'history') {
    router.push('/history');
  }
}
</script>

<template>
  <header class="site-header">
    <div class="lab-container header-inner">
      <router-link to="/" class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="26" height="26">
            <rect width="32" height="32" rx="7" fill="var(--lab-accent)" />
            <circle cx="11.5" cy="12" r="3.2" fill="#101218" />
            <circle cx="20.5" cy="12" r="3.2" fill="#101218" />
            <path
              d="M16 17c3.6 0 6.5 2.6 6.5 5.4 0 1.6-1.3 2.6-2.9 2.6-1.4 0-2.4-.8-3.6-.8s-2.2.8-3.6.8c-1.6 0-2.9-1-2.9-2.6C9.5 19.6 12.4 17 16 17z"
              fill="#101218"
            />
          </svg>
        </span>
        <span class="brand-text">
          <span class="brand-cn">智模工坊</span>
          <span class="brand-en mono">MINILAB</span>
        </span>
      </router-link>

      <nav class="site-nav">
        <router-link
          v-for="nav in navs"
          :key="nav.path"
          :to="nav.path"
          class="nav-link"
          :class="{ active: isActive(nav) }"
        >
          {{ nav.label }}
          <span v-if="nav.auth && !logged" class="nav-lock mono">*</span>
        </router-link>
      </nav>

      <div class="header-user">
        <template v-if="logged">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-chip">
              <span class="user-avatar mono">{{ avatarChar }}</span>
              <span class="user-name">{{ name }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="history" :icon="Coin">识别记录</el-dropdown-item>
                <el-dropdown-item command="logout" :icon="SwitchButton" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login">
            <el-button type="primary" round size="default" :icon="UserFilled">登录 / 注册</el-button>
          </router-link>
        </template>
      </div>
    </div>
  </header>

  <main class="site-main">
    <router-view v-slot="{ Component }">
      <transition name="fade-slide" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>
  </main>

  <footer class="site-footer">
    <div class="lab-container footer-inner mono">
      <span>MODELSCOPE MINILAB © 2026</span>
      <span class="footer-dot">·</span>
      <span>FASTAPI + PYTORCH + VUE3</span>
      <span class="footer-dot">·</span>
      <span>DEPLOYED ON DOCKER</span>
    </div>
  </footer>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  background: rgba(15, 18, 22, 0.82);
  border-bottom: 1px solid var(--lab-line);
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 64px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--lab-ink);
}

.brand-mark {
  display: grid;
  place-items: center;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand-cn {
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-en {
  font-size: 10px;
  letter-spacing: 0.3em;
  color: var(--lab-accent);
}

.site-nav {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-link {
  position: relative;
  padding: 6px 14px;
  border-radius: 8px;
  color: var(--lab-ink-dim);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.18s ease, background 0.18s ease;
}

.nav-link:hover {
  color: var(--lab-ink);
  background: rgba(255, 255, 255, 0.05);
}

.nav-link.active {
  color: var(--lab-accent);
  background: var(--lab-accent-soft);
}

.nav-lock {
  color: var(--lab-ink-faint);
  font-size: 11px;
}

.header-user {
  display: flex;
  align-items: center;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 999px;
  border: 1px solid var(--lab-line);
  background: var(--lab-panel);
  outline: none;
}

.user-chip:hover {
  border-color: var(--lab-accent-line);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--lab-accent);
  color: #101218;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
}

.user-name {
  font-size: 13px;
  color: var(--lab-ink);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.site-main {
  flex: 1;
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.site-footer {
  border-top: 1px solid var(--lab-line);
  padding: 20px 0 26px;
  background: rgba(15, 18, 22, 0.6);
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 11px;
  letter-spacing: 0.12em;
  color: var(--lab-ink-faint);
}

.footer-dot {
  color: var(--lab-accent);
}

@media (max-width: 720px) {
  .header-inner {
    gap: 12px;
  }
  .brand-en {
    display: none;
  }
  .site-nav {
    gap: 0;
  }
  .nav-link {
    padding: 6px 8px;
    font-size: 13px;
  }
  .user-name {
    display: none;
  }
}
</style>
