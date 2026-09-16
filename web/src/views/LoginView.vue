<script setup>
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock, Stamp } from '@element-plus/icons-vue';
import api from '../api';
import { setAuth } from '../stores/auth';
import { errMessage } from '../utils/format';

const route = useRoute();
const router = useRouter();

const activeTab = ref('login');
const loading = ref(false);

const loginForm = reactive({ username: '', password: '' });
const registerForm = reactive({ username: '', password: '', confirm: '', nickname: '' });

const usernameRule = [
  { required: true, message: '请输入用户名', trigger: 'blur' },
  {
    pattern: /^[A-Za-z0-9_-]{3,32}$/,
    message: '3-32 位字母、数字、下划线或中划线',
    trigger: 'blur',
  },
];
const passwordRule = [
  { required: true, message: '请输入密码', trigger: 'blur' },
  { min: 6, max: 64, message: '密码长度 6-64 位', trigger: 'blur' },
];

const loginRef = ref();
const registerRef = ref();

function goBack() {
  const redirect = route.query.redirect;
  if (redirect && typeof redirect === 'string') {
    router.push(redirect);
  } else {
    router.push('/');
  }
}

async function submitLogin() {
  const valid = await loginRef.value.validate().catch(() => false);
  if (!valid || loading.value) return;
  loading.value = true;
  try {
    const resp = await api.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
    });
    setAuth(resp.token, resp.user);
    ElMessage.success('登录成功，欢迎回到实验台');
    goBack();
  } catch (e) {
    /* 错误提示已由拦截器统一弹出 */
  } finally {
    loading.value = false;
  }
}

async function submitRegister() {
  const valid = await registerRef.value.validate().catch(() => false);
  if (!valid || loading.value) return;
  if (registerForm.password !== registerForm.confirm) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }
  loading.value = true;
  try {
    const resp = await api.register({
      username: registerForm.username.trim(),
      password: registerForm.password,
      nickname: registerForm.nickname.trim() || undefined,
    });
    setAuth(resp.token, resp.user);
    ElMessage.success('注册成功，已自动登录');
    goBack();
  } catch (e) {
    /* 错误提示已由拦截器统一弹出 */
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="lab-panel lab-panel--crossed auth-card">
      <p class="lab-eyebrow card-eyebrow">AUTH // 身份验证终端</p>
      <h1 class="card-title">进入实验台</h1>

      <el-tabs v-model="activeTab" stretch class="auth-tabs">
        <el-tab-pane label="登 录" name="login">
          <el-form
            ref="loginRef"
            :model="loginForm"
            label-position="top"
            size="large"
            @keyup.enter="submitLogin"
          >
            <el-form-item label="用户名" prop="username" :rules="usernameRule">
              <el-input v-model="loginForm.username" :prefix-icon="User" placeholder="用户名" autocomplete="username" />
            </el-form-item>
            <el-form-item label="密码" prop="password" :rules="passwordRule">
              <el-input
                v-model="loginForm.password"
                :prefix-icon="Lock"
                type="password"
                show-password
                placeholder="密码"
                autocomplete="current-password"
              />
            </el-form-item>
            <el-button
              type="primary"
              class="submit-btn"
              size="large"
              round
              :loading="loading"
              @click="submitLogin"
            >
              登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注 册" name="register">
          <el-form
            ref="registerRef"
            :model="registerForm"
            label-position="top"
            size="large"
            @keyup.enter="submitRegister"
          >
            <el-form-item label="用户名" prop="username" :rules="usernameRule">
              <el-input v-model="registerForm.username" :prefix-icon="User" placeholder="3-32 位字母/数字/下划线" autocomplete="username" />
            </el-form-item>
            <el-form-item label="密码" prop="password" :rules="passwordRule">
              <el-input
                v-model="registerForm.password"
                :prefix-icon="Lock"
                type="password"
                show-password
                placeholder="至少 6 位"
                autocomplete="new-password"
              />
            </el-form-item>
            <el-form-item
              label="确认密码"
              prop="confirm"
              :rules="[{ required: true, message: '请再次输入密码', trigger: 'blur' }]"
            >
              <el-input
                v-model="registerForm.confirm"
                :prefix-icon="Lock"
                type="password"
                show-password
                placeholder="再输入一次"
                autocomplete="new-password"
              />
            </el-form-item>
            <el-form-item label="昵称（可选）">
              <el-input v-model="registerForm.nickname" :prefix-icon="Stamp" placeholder="展示在右上角的名字" maxlength="32" />
            </el-form-item>
            <el-button
              type="primary"
              class="submit-btn"
              size="large"
              round
              :loading="loading"
              @click="submitRegister"
            >
              注册并登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <p class="card-foot mono">TOKEN ISSUED BY FASTAPI · VALID 7 DAYS</p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  display: flex;
  justify-content: center;
  padding: 40px 0 20px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 32px 34px 26px;
}

.card-eyebrow {
  margin: 0 0 10px;
}

.card-title {
  margin: 0 0 20px;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.auth-tabs :deep(.el-tabs__item) {
  font-weight: 700;
  letter-spacing: 0.2em;
}

.submit-btn {
  width: 100%;
  margin-top: 6px;
}

.card-foot {
  margin: 18px 0 0;
  text-align: center;
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--lab-ink-faint);
}
</style>
