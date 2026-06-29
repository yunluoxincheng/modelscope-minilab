// utils/config.js
// 开发环境：使用本地后端。请在正式部署时改为 HTTPS 域名。
const API_BASE = 'http://127.0.0.1:8000/api';

module.exports = {
  API_BASE,
  MAX_UPLOAD_MB: 5,
  SUPPORTED_TYPES: ['jpg', 'jpeg', 'png', 'webp'],
};
