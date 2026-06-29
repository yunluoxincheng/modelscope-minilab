// utils/auth.js
const TOKEN_KEY = 'minilab_token';
const USER_KEY = 'minilab_user';

module.exports = {
  getToken() {
    try {
      return wx.getStorageSync(TOKEN_KEY) || '';
    } catch (e) {
      return '';
    }
  },

  setToken(token) {
    try {
      wx.setStorageSync(TOKEN_KEY, token);
    } catch (e) {}
  },

  clearToken() {
    try {
      wx.removeStorageSync(TOKEN_KEY);
      wx.removeStorageSync(USER_KEY);
    } catch (e) {}
  },

  getUserInfo() {
    try {
      return wx.getStorageSync(USER_KEY) || null;
    } catch (e) {
      return null;
    }
  },

  setUserInfo(user) {
    try {
      wx.setStorageSync(USER_KEY, user);
    } catch (e) {}
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  ensureLogin(redirect) {
    if (this.isLoggedIn()) {
      return true;
    }
    wx.navigateTo({
      url: '/pages/login/login' + (redirect ? '?redirect=' + encodeURIComponent(redirect) : ''),
    });
    return false;
  },
};
