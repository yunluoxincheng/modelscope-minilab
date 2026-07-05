// utils/config.js
// 开发环境：使用本地后端。请在正式部署时改为 HTTPS 域名。
const API_BASE = 'https://modelscope.yunluostar.com/api';

module.exports = {
  API_BASE,
  MAX_UPLOAD_MB: 5,
  SUPPORTED_TYPES: ['jpg', 'jpeg', 'png', 'webp'],
};
