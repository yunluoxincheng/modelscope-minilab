// pages/index/index.js
const api = require('../../utils/api');

Page({
  data: {
    loading: true,
    models: [],
    error: '',
  },

  onShow() {
    this.loadModels();
  },

  onPullDownRefresh() {
    this.loadModels().finally(() => wx.stopPullDownRefresh());
  },

  loadModels() {
    this.setData({ loading: true, error: '' });
    return api
      .getModels()
      .then((resp) => {
        const items = (resp && resp.items) || [];
        this.setData({ models: items, loading: false });
      })
      .catch(() => {
        this.setData({ models: [], loading: false, error: '加载失败，请下拉刷新' });
      });
  },

  onTapModel(e) {
    const modelId = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/model-detail/model-detail?id=' + modelId });
  },
});
