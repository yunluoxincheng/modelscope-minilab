// utils/request.js
const config = require('./config');
const auth = require('./auth');

function showError(message) {
  wx.showToast({
    title: message || '网络异常，请稍后重试',
    icon: 'none',
    duration: 2500,
  });
}

function mapBackendError(body) {
  if (!body || !body.error) return '';
  const code = body.error.code;
  const map = {
    MODEL_NOT_FOUND: '模型不存在或暂不可用',
    UNAUTHORIZED: '请先登录',
    INVALID_TOKEN: '登录状态已失效，请重新登录',
    FILE_REQUIRED: '请上传图片',
    FILE_TOO_LARGE: '图片不能超过 5MB',
    UNSUPPORTED_FILE_TYPE: '仅支持 JPG、PNG、WEBP 图片',
    INVALID_IMAGE: '图片解析失败，请更换图片',
    RATE_LIMITED: '请求过于频繁，请稍后重试',
    INFERENCE_FAILED: '模型识别失败，请稍后重试',
    SERVICE_UNAVAILABLE: '服务暂不可用，请在开放时间内重试',
  };
  return map[code] || body.error.message || '请求失败';
}

function buildHeaders(extra) {
  const headers = { ...(extra || {}) };
  const token = auth.getToken();
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }
  return headers;
}

function request(options) {
  return new Promise((resolve, reject) => {
    const url = options.url.startsWith('http') ? options.url : config.API_BASE + options.url;
    wx.request({
      url,
      method: options.method || 'GET',
      data: options.data,
      header: buildHeaders(options.header),
      success: (resp) => {
        const status = resp.statusCode;
        const data = resp.data;
        if (status >= 200 && status < 300) {
          resolve(data);
          return;
        }
        const message = mapBackendError(data);
        if (status === 401) {
          auth.clearToken();
        }
        showError(message);
        const err = new Error(message || '请求失败');
        err.status = status;
        err.body = data;
        reject(err);
      },
      fail: (err) => {
        showError('网络异常，请稍后重试');
        reject(err);
      },
    });
  });
}

function uploadFile(options) {
  return new Promise((resolve, reject) => {
    const url = options.url.startsWith('http') ? options.url : config.API_BASE + options.url;
    const token = auth.getToken();
    wx.uploadFile({
      url,
      filePath: options.filePath,
      name: 'file',
      formData: options.formData,
      header: token ? { Authorization: 'Bearer ' + token } : {},
      success: (resp) => {
        let data;
        try {
          data = JSON.parse(resp.data);
        } catch (e) {
          data = null;
        }
        const status = resp.statusCode;
        if (status >= 200 && status < 300) {
          resolve(data);
          return;
        }
        const message = mapBackendError(data);
        if (status === 401) {
          auth.clearToken();
        }
        showError(message);
        const err = new Error(message || '上传失败');
        err.status = status;
        err.body = data;
        reject(err);
      },
      fail: (err) => {
        showError('网络异常，请稍后重试');
        reject(err);
      },
    });
  });
}

module.exports = {
  request,
  uploadFile,
  mapBackendError,
  showError,
};
