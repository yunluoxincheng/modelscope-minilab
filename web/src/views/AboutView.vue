<script setup>
const stack = [
  { name: 'FastAPI', role: '后端 API 框架' },
  { name: 'PyTorch', role: '深度学习推理引擎' },
  { name: 'EfficientNet-B0', role: '猫狗分类骨干网络' },
  { name: 'Vue 3', role: 'Web 前端框架' },
  { name: 'Element Plus', role: '前端组件库' },
  { name: 'MySQL / SQLite', role: '数据持久化' },
  { name: 'Redis', role: '限流与缓存' },
  { name: 'Docker', role: '多架构容器化部署' },
  { name: 'GitHub Actions', role: 'CI/CD 自动构建镜像' },
];

const features = [
  {
    title: '可扩展模型注册表',
    desc: '新增模型只需注册一个 predictor 模块和一条元数据，列表 / 详情 / 推理接口自动生效。',
  },
  {
    title: '加权集成推理',
    desc: '猫狗分类模型由 EfficientNet-B0 三个版本（v2/v3/v4）按 5:1:3 加权集成，取长补短。',
  },
  {
    title: '完整的生产管线',
    desc: 'JWT 鉴权、Redis 限流、上传校验、失败留痕、服务时间窗口，一个都不少。',
  },
];
</script>

<template>
  <div>
    <div class="about-head">
      <p class="lab-eyebrow about-eyebrow">// ABOUT THE LAB</p>
      <h1 class="about-title">关于智模工坊</h1>
      <p class="about-sub">
        智模工坊（ModelScope MiniLab）是一个个人作品集风格的 AI 模型展示平台。
        它把"训练好的模型"变成"可以在线体验的服务"：上传一张猫或狗的照片，几毫秒后拿到推理结果，
        每一次调用都被完整记录、限流与鉴权保护——就像一个真正的线上 AI 产品。
      </p>
    </div>

    <section class="features">
      <div v-for="(f, i) in features" :key="f.title" class="feature lab-panel">
        <span class="feature-index mono">{{ String(i + 1).padStart(2, '0') }}</span>
        <h3 class="feature-title">{{ f.title }}</h3>
        <p class="feature-desc">{{ f.desc }}</p>
      </div>
    </section>

    <section class="stack-section">
      <h2 class="section-title">技术栈</h2>
      <div class="stack-grid">
        <div v-for="s in stack" :key="s.name" class="stack-item">
          <span class="stack-name mono">{{ s.name }}</span>
          <span class="stack-role">{{ s.role }}</span>
        </div>
      </div>
    </section>

    <section class="notice lab-panel">
      <p class="notice-text">
        <span class="mono notice-tag">NOTE</span>
        推理服务默认在 <strong>10:00 – 18:00</strong>（北京时间）开放，其余时间请求会返回
        SERVICE_UNAVAILABLE；服务窗口可在服务端配置中调整。历史记录与账号绑定，换个浏览器登录同一账号也能看到。
      </p>
    </section>
  </div>
</template>

<style scoped>
.about-head {
  max-width: 640px;
  margin-bottom: 36px;
}

.about-eyebrow {
  margin: 0 0 12px;
}

.about-title {
  margin: 0 0 14px;
  font-size: 34px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.about-sub {
  margin: 0;
  color: var(--lab-ink-dim);
  line-height: 1.9;
  font-size: 15px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.feature {
  padding: 22px 24px;
}

.feature-index {
  font-size: 12px;
  color: var(--lab-accent);
  letter-spacing: 0.14em;
}

.feature-title {
  margin: 10px 0 8px;
  font-size: 17px;
  font-weight: 800;
}

.feature-desc {
  margin: 0;
  font-size: 13.5px;
  color: var(--lab-ink-dim);
  line-height: 1.8;
}

.section-title {
  margin: 0 0 18px;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 40px;
}

.stack-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 14px 18px;
  border: 1px solid var(--lab-line);
  border-radius: 10px;
  background: rgba(23, 28, 36, 0.5);
  transition: border-color 0.2s ease;
}

.stack-item:hover {
  border-color: var(--lab-accent-line);
}

.stack-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--lab-ink);
}

.stack-role {
  font-size: 12px;
  color: var(--lab-ink-faint);
}

.notice {
  padding: 18px 22px;
}

.notice-text {
  margin: 0;
  font-size: 13.5px;
  color: var(--lab-ink-dim);
  line-height: 1.9;
}

.notice-tag {
  color: var(--lab-accent);
  margin-right: 10px;
  font-size: 11px;
  letter-spacing: 0.14em;
}
</style>
