// utils/api.js
const { request, uploadFile } = require('./request');

module.exports = {
  getModels: () => request({ url: '/models' }),
  getModelDetail: (modelId) => request({ url: '/models/' + modelId }),
  getHistory: (page = 1, pageSize = 20) =>
    request({ url: '/predictions/history', data: { page, page_size: pageSize } }),
  wechatLogin: (code, profile) =>
    request({ url: '/auth/wechat-login', method: 'POST', data: { code, ...(profile || {}) } }),
  predict: (modelId, filePath) =>
    uploadFile({ url: '/models/' + modelId + '/predict', filePath }),
};
