// 后端 API 封装：统一 baseURL、Bearer 注入、错误码→文案映射（与小程序 request.js 对齐）。
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { authStore, clearAuth } from '../stores/auth';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const ERROR_MESSAGES = {
  MODEL_NOT_FOUND: '模型不存在或暂不可用',
  UNAUTHORIZED: '请先登录',
  INVALID_TOKEN: '登录状态已失效，请重新登录',
  INVALID_CREDENTIALS: '用户名或密码错误',
  USERNAME_TAKEN: '用户名已被注册',
  FILE_REQUIRED: '请上传图片',
  FILE_TOO_LARGE: '图片太大了，请压缩后再试',
  UNSUPPORTED_FILE_TYPE: '仅支持 JPG、PNG、WEBP 图片',
  INVALID_IMAGE: '图片解析失败，请更换图片',
  RATE_LIMITED: '请求过于频繁，请稍后重试',
  INFERENCE_FAILED: '模型识别失败，请稍后重试',
  SERVICE_UNAVAILABLE: '服务暂不可用，请在开放时间内重试',
};

const http = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

http.interceptors.request.use((config) => {
  if (authStore.token) {
    config.headers.Authorization = 'Bearer ' + authStore.token;
  }
  return config;
});

http.interceptors.response.use(
  (resp) => resp.data,
  (error) => {
    const status = error.response ? error.response.status : 0;
    const body = error.response ? error.response.data : null;
    let message = ERROR_MESSAGES[body && body.error && body.error.code] ||
      (body && body.error && body.error.message) || '';
    if (status === 401) {
      clearAuth();
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(
          window.location.pathname + window.location.search
        );
        // 动态引入避免 api → router → 视图 → api 的循环依赖
        import('../router').then(({ default: router }) => {
          router.push('/login?redirect=' + redirect);
        });
      }
      message = message || '请先登录';
    } else if (!message) {
      message = status === 0 ? '网络异常，请检查连接' : '请求失败，请稍后重试';
    }
    ElMessage.error(message);
    const err = new Error(message);
    err.status = status;
    err.body = body;
    return Promise.reject(err);
  }
);

export const api = {
  getModels: () => http.get('/models'),
  getModelDetail: (modelId) => http.get('/models/' + modelId),
  getHistory: (page = 1, pageSize = 20) =>
    http.get('/predictions/history', { params: { page, page_size: pageSize } }),
  register: (payload) => http.post('/auth/register', payload),
  login: (payload) => http.post('/auth/login', payload),
  predict: (modelId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return http.post('/models/' + modelId + '/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
  },
};

export default api;
