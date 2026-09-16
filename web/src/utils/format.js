// 展示层格式化工具
export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined) return '--';
  return (value * 100).toFixed(digits) + '%';
}

export function formatTime(isoString) {
  if (!isoString) return '--';
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) return isoString;
  const pad = (n) => String(n).padStart(2, '0');
  return (
    d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
    ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
  );
}

export function formatBytes(bytes) {
  if (bytes === null || bytes === undefined) return '--';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1024 / 1024).toFixed(2) + ' MB';
}

// 通用错误文案（业务错误码映射在 api 层已做，这里兜底网络错误）
export function errMessage(err, fallback) {
  return (err && err.message) || fallback || '操作失败，请稍后重试';
}
