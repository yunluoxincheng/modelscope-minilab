// 认证状态：localStorage 持久化的轻量 reactive 单例（vue 官方推荐的小型状态管理模式）。
import { reactive } from 'vue';

const TOKEN_KEY = 'minilab_web_token';
const USER_KEY = 'minilab_web_user';

function readJSON(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function writeJSON(key, value) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    /* 存储不可用时静默降级为内存态 */
  }
}

export const authStore = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: readJSON(USER_KEY),
});

export function setAuth(token, user) {
  authStore.token = token || '';
  authStore.user = user || null;
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch (e) {}
  writeJSON(USER_KEY, user);
}

export function clearAuth() {
  setAuth('', null);
}

export function isLoggedIn() {
  return !!authStore.token;
}

// 展示名：昵称优先，其次用户名，微信用户兜底「实验员」
export function displayName() {
  const u = authStore.user;
  if (!u) return '';
  return u.nickname || u.username || '实验员';
}
