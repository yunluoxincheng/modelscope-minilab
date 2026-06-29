// pages/login/login.js
const api = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    redirect: '',
    loading: false,
    error: '',
  },

  onLoad(options) {
    this.setData({ redirect: options.redirect || '/pages/index/index' });
  },

  onLogin() {
    if (this.data.loading) return;
    this.setData({ loading: true, error: '' });
    wx.login({
      success: (res) => {
        if (!res.code) {
          this.setData({ loading: false, error: '获取微信登录凭证失败' });
          return;
        }
        api
          .wechatLogin(res.code)
          .then((resp) => {
            auth.setToken(resp.token);
            auth.setUserInfo(resp.user);
            this.setData({ loading: false });
            wx.showToast({ title: '登录成功', icon: 'success' });
            setTimeout(() => {
              const redirect = this.data.redirect;
              if (redirect && redirect.indexOf('tabBar') > -1) {
                wx.switchTab({ url: redirect });
              } else if (redirect === '/pages/index/index' || redirect === '/pages/history/history' || redirect === '/pages/about/about') {
                wx.switchTab({ url: redirect });
              } else {
                wx.redirectTo({
                  url: redirect,
                  fail: () => wx.switchTab({ url: '/pages/index/index' }),
                });
              }
            }, 500);
          })
          .catch((err) => {
            this.setData({ loading: false, error: (err && err.message) || '登录失败' });
          });
      },
      fail: () => {
        this.setData({ loading: false, error: '微信登录取消' });
      },
    });
  },
});
