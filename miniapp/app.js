const auth = require('./utils/auth');
const config = require('./utils/config');

App({
  globalData: {
    userInfo: null,
    token: null,
    apiBase: config.API_BASE,
  },

  onLaunch() {
    this.globalData.token = auth.getToken();
    this.globalData.userInfo = auth.getUserInfo();
  },
});
