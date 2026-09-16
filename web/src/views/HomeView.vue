<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowRight, Refresh } from '@element-plus/icons-vue';
import api from '../api';
import { errMessage } from '../utils/format';

const router = useRouter();

const loading = ref(true);
const error = ref('');
const models = ref([]);

const CARD_ART = [
  { emoji: '🐱🐶', from: '#ff6b2c', to: '#b3400f' },
  { emoji: '🧪', from: '#58a6ff', to: '#1f4f8f' },
  { emoji: '🔬', from: '#3fb950', to: '#1f6f38' },
];

function artOf(index) {
  return CARD_ART[index % CARD_ART.length];
}

function taskLabel(taskType) {
  const map = {
    image_classification: 'IMAGE · CLASSIFICATION',
    text_classification: 'TEXT · CLASSIFICATION',
  };
  return map[taskType] || String(taskType || 'MODEL').toUpperCase();
}

async function loadModels() {
  loading.value = true;
  error.value = '';
  try {
    const resp = await api.getModels();
    models.value = (resp && resp.items) || [];
  } catch (e) {
    models.value = [];
    error.value = errMessage(e, '模型列表加载失败');
  } finally {
    loading.value = false;
  }
}

onMounted(loadModels);
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="hero">
      <p class="lab-eyebrow hero-eyebrow">// MODELSCOPE MINILAB · AI MODEL LAB_</p>
      <h1 class="hero-title">
        智模工坊<span class="hero-cursor mono" aria-hidden="true">▍</span>
      </h1>
      <p class="hero-sub">
        个人 AI 模型实验室。在这里上传一张图片，看一个真正跑在服务器 GPU→CPU
        推理管线上的模型如何思考——每一次预测都留下可追溯的记录。
      </p>
      <div class="hero-actions">
        <el-button
          type="primary"
          size="large"
          round
          :icon="ArrowRight"
          :disabled="!models.length"
          @click="models.length && router.push('/models/' + models[0].model_id)"
        >
          进入实验台
        </el-button>
        <router-link to="/about">
          <el-button size="large" round plain>了解实验室</el-button>
        </router-link>
      </div>
      <div class="hero-stats mono">
        <div class="stat">
          <span class="stat-value">{{ models.length || '–' }}</span>
          <span class="stat-label">在线模型</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">PyTorch</span>
          <span class="stat-label">推理引擎</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">REST API</span>
          <span class="stat-label">服务接口</span>
        </div>
      </div>
    </section>

    <!-- 模型列表 -->
    <section class="models-section">
      <div class="section-head">
        <h2 class="section-title">模型广场</h2>
        <span class="lab-eyebrow">REGISTRY // 可扩展模型注册表</span>
      </div>

      <el-skeleton v-if="loading" :rows="4" animated class="models-skeleton" />

      <el-alert
        v-else-if="error"
        type="error"
        :title="error"
        show-icon
        :closable="false"
      >
        <el-button size="small" type="primary" plain :icon="Refresh" @click="loadModels">
          重试
        </el-button>
      </el-alert>

      <el-empty v-else-if="!models.length" description="暂无上线模型" />

      <div v-else class="models-grid">
        <article
          v-for="(m, i) in models"
          :key="m.model_id"
          class="model-card lab-panel lab-panel--crossed"
          @click="router.push('/models/' + m.model_id)"
        >
          <div
            class="card-art"
            :style="{ background: `linear-gradient(135deg, ${artOf(i).from}22, ${artOf(i).to}44)` }"
          >
            <span class="card-emoji">{{ artOf(i).emoji }}</span>
            <span class="card-task mono">{{ taskLabel(m.task_type) }}</span>
          </div>
          <div class="card-body">
            <div class="card-title-row">
              <h3 class="card-title">{{ m.name }}</h3>
              <span class="card-id mono">{{ m.model_id }}</span>
            </div>
            <p class="card-en mono">{{ m.name_en }}</p>
            <p class="card-desc">{{ m.description }}</p>
            <div class="card-footer">
              <span class="card-cta mono">RUN MODEL →</span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  padding: 56px 0 48px;
  max-width: 640px;
}

.hero-eyebrow {
  margin: 0 0 14px;
}

.hero-title {
  margin: 0 0 18px;
  font-size: 56px;
  font-weight: 900;
  letter-spacing: 0.04em;
  line-height: 1.1;
  color: var(--lab-ink);
}

.hero-cursor {
  color: var(--lab-accent);
  animation: blink 1.1s steps(2, start) infinite;
  margin-left: 4px;
}

@keyframes blink {
  to {
    visibility: hidden;
  }
}

.hero-sub {
  margin: 0 0 28px;
  font-size: 16px;
  color: var(--lab-ink-dim);
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  gap: 14px;
  align-items: center;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-top: 40px;
  padding: 18px 24px;
  border: 1px solid var(--lab-line);
  border-radius: 12px;
  background: rgba(23, 28, 36, 0.6);
  width: fit-content;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--lab-ink);
}

.stat-label {
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--lab-ink-faint);
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--lab-line-strong);
}

.models-section {
  padding-bottom: 24px;
}

.section-head {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 22px;
}

.section-title {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.models-skeleton {
  padding: 24px;
  border: 1px solid var(--lab-line);
  border-radius: 14px;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 22px;
}

.model-card {
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
}

.model-card:hover {
  transform: translateY(-4px);
  border-color: var(--lab-accent-line);
  box-shadow: 0 14px 40px rgba(255, 107, 44, 0.12);
}

.card-art {
  position: relative;
  height: 120px;
  display: grid;
  place-items: center;
  border-bottom: 1px solid var(--lab-line);
}

.card-emoji {
  font-size: 44px;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.4));
}

.card-task {
  position: absolute;
  top: 10px;
  left: 12px;
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--lab-ink-dim);
}

.card-body {
  padding: 18px 20px 20px;
}

.card-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.card-id {
  font-size: 11px;
  color: var(--lab-accent);
  background: var(--lab-accent-soft);
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
}

.card-en {
  margin: 4px 0 10px;
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--lab-ink-faint);
}

.card-desc {
  margin: 0 0 16px;
  font-size: 13.5px;
  color: var(--lab-ink-dim);
  line-height: 1.75;
  min-height: 48px;
}

.card-cta {
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--lab-accent);
}

@media (max-width: 720px) {
  .hero-title {
    font-size: 40px;
  }
  .hero-stats {
    gap: 14px;
    padding: 14px 16px;
  }
}
</style>
