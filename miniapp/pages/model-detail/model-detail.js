// pages/model-detail/model-detail.js
const api = require('../../utils/api');
const auth = require('../../utils/auth');
const config = require('../../utils/config');

Page({
  data: {
    modelId: '',
    model: null,
    loading: true,
    predicting: false,
    imageSrc: '',
    result: null,
    error: '',
    maxUploadMb: config.MAX_UPLOAD_MB,
  },

  onLoad(options) {
    this.setData({ modelId: options.id });
    api
      .getModelDetail(options.id)
      .then((model) => {
        this.setData({ model, loading: false });
      })
      .catch(() => {
        this.setData({ loading: false, error: '加载模型信息失败' });
      });
  },

  onChooseImage() {
    if (!auth.isLoggedIn()) {
      auth.ensureLogin('/pages/model-detail/model-detail?id=' + this.data.modelId);
      return;
    }
    if (this.data.predicting) return;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed', 'original'],
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0];
        if (!file) return;
        this.validateAndUpload(file.tempFilePath, file.size);
      },
      fail: () => {},
    });
  },

  validateAndUpload(filePath, size) {
    const lower = (filePath || '').toLowerCase();
    const ok = config.SUPPORTED_TYPES.some((ext) => lower.endsWith('.' + ext));
    if (!ok) {
      wx.showToast({ title: '仅支持 JPG、PNG、WEBP 图片', icon: 'none' });
      return;
    }
    if (size && size > this.data.maxUploadMb * 1024 * 1024) {
      wx.showToast({ title: '图片不能超过 5MB', icon: 'none' });
      return;
    }
    this.setData({ imageSrc: filePath, result: null, error: '', predicting: true });
    api
      .predict(this.data.modelId, filePath)
      .then((data) => {
        this.setData({ result: data, predicting: false });
      })
      .catch((err) => {
        this.setData({ predicting: false, error: (err && err.message) || '识别失败' });
      });
  },

  goHistory() {
    wx.switchTab({ url: '/pages/history/history' });
  },
});
