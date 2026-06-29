// pages/history/history.js
const api = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    loading: true,
    items: [],
    page: 1,
    pageSize: 20,
    total: 0,
    error: '',
    loggedIn: false,
  },

  onShow() {
    const loggedIn = auth.isLoggedIn();
    this.setData({ loggedIn });
    if (loggedIn) {
      this.loadHistory(true);
    } else {
      this.setData({ loading: false, items: [], total: 0 });
    }
  },

  onPullDownRefresh() {
    this.loadHistory(true).finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    if (this.data.items.length >= this.data.total) return;
    this.loadHistory(false);
  },

  loadHistory(reset) {
    const page = reset ? 1 : this.data.page + 1;
    this.setData({ loading: true, error: '' });
    return api
      .getHistory(page, this.data.pageSize)
      .then((resp) => {
        const items = reset ? resp.items : this.data.items.concat(resp.items);
        this.setData({
          items,
          page,
          total: resp.total,
          loading: false,
        });
      })
      .catch(() => {
        this.setData({ loading: false, error: '加载失败，下拉刷新' });
      });
  },

  goLogin() {
    wx.navigateTo({ url: '/pages/login/login?redirect=/pages/history/history' });
  },
});
