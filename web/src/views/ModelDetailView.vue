<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { UploadFilled, Clock, Coin, DataLine } from '@element-plus/icons-vue';
import api from '../api';
import { isLoggedIn } from '../stores/auth';
import { formatPercent } from '../utils/format';

const route = useRoute();
const router = useRouter();

const modelId = route.params.id;
const model = ref(null);
const loading = ref(true);
const loadError = ref('');

const predicting = ref(false);
const previewUrl = ref('');
const previewName = ref('');
const previewSize = ref(0);
const result = ref(null);
const predictError = ref('');
const fileInput = ref(null);
const scanTimer = ref(null);
const scanOffset = ref(0);

const maxUploadMb = computed(() => (model.value && model.value.max_upload_mb) || 5);
const supportedTypes = computed(
  () => (model.value && model.value.supported_types_label) || 'JPG / PNG / WEBP'
);

const metaRows = computed(() => {
  if (!model.value) return [];
  return [
    { k: 'MODEL_ID', v: model.value.model_id },
    { k: 'TASK', v: model.value.task_type },
    { k: 'INPUT', v: model.value.input_type },
    { k: 'MAX_SIZE', v: maxUploadMb.value + ' MB' },
  ];
});

const probabilityRows = computed(() => {
  if (!result.value || !result.value.probabilities) return [];
  return Object.entries(result.value.probabilities)
    .map(([label, p]) => ({ label, p: Number(p) || 0 }))
    .sort((a, b) => b.p - a.p);
});

function typeLabel(label) {
  const map = { cat: '猫', dog: '狗' };
  return (result.value && result.value.label_cn) || map[label] || label;
}

async function loadModel() {
  loading.value = true;
  loadError.value = '';
  try {
    model.value = await api.getModelDetail(modelId);
    model.value.supported_types_label = (model.value.supported_file_types || [])
      .map((t) => t.replace('image/', '').toUpperCase())
      .join(' / ');
  } catch (e) {
    loadError.value = (e && e.message) || '模型信息加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadModel);
onBeforeUnmount(stopScan);

function beforeUpload(file) {
  const ok = /\.(jpe?g|png|webp)$/i.test(file.name || '');
  if (!ok) {
    ElMessage.error('仅支持 JPG、PNG、WEBP 图片');
    return false;
  }
  if (file.size > maxUploadMb.value * 1024 * 1024) {
    ElMessage.error(`图片不能超过 ${maxUploadMb.value}MB`);
    return false;
  }
  return true;
}

function triggerUpload() {
  if (!isLoggedIn()) {
    router.push({
      path: '/login',
      query: { redirect: route.fullPath },
    });
    return;
  }
  if (predicting.value) return;
  fileInput.value && fileInput.value.click();
}

async function handleUpload(file) {
  if (!beforeUpload(file)) return;
  await runPredict(file);
}

function onFileChanged(event) {
  const file = event.target.files && event.target.files[0];
  event.target.value = ''; // 允许重复选择同一张图
  if (file) handleUpload(file);
}

async function onDrop(event) {
  if (!isLoggedIn()) {
    router.push({ path: '/login', query: { redirect: route.fullPath } });
    return;
  }
  const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
  if (!file) return;
  handleUpload(file);
}

async function runPredict(file) {
  previewUrl.value = URL.createObjectURL(file);
  previewName.value = file.name;
  previewSize.value = file.size;
  result.value = null;
  predictError.value = '';
  predicting.value = true;
  startScan();
  try {
    result.value = await api.predict(modelId, file);
  } catch (e) {
    predictError.value = (e && e.message) || '识别失败，请稍后重试';
  } finally {
    predicting.value = false;
    stopScan();
  }
}

function startScan() {
  stopScan();
  scanOffset.value = 0;
  scanTimer.value = setInterval(() => {
    scanOffset.value = (scanOffset.value + 1.5) % 100;
  }, 24);
}

function stopScan() {
  if (scanTimer.value) {
    clearInterval(scanTimer.value);
    scanTimer.value = null;
  }
}

function resetPreview() {
  URL.revokeObjectURL && previewUrl.value && URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = '';
  result.value = null;
  predictError.value = '';
}
</script>

<template>
  <div>
    <el-skeleton v-if="loading" :rows="6" animated class="lab-panel detail-skeleton" />

    <el-alert
      v-else-if="loadError"
      type="error"
      :title="loadError"
      show-icon
      :closable="false"
    >
      <el-button size="small" type="primary" plain @click="loadModel">重试</el-button>
    </el-alert>

    <template v-else>
      <div class="detail-head">
        <router-link to="/" class="back-link mono">← BACK TO REGISTRY</router-link>
        <h1 class="detail-title">{{ model.name }}</h1>
        <p class="detail-en mono">{{ model.name_en }} · {{ model.model_id }}</p>
      </div>

      <div class="detail-grid">
        <!-- 左：上传与预览 -->
        <section
          class="lab-panel lab-panel--crossed upload-panel"
          @dragover.prevent
          @drop.prevent="onDrop"
        >
          <div class="panel-label mono">INPUT // 上传图片</div>

          <div
            v-if="!previewUrl"
            class="dropzone"
            role="button"
            tabindex="0"
            @click="triggerUpload"
            @keydown.enter="triggerUpload"
          >
            <el-icon class="dropzone-icon"><UploadFilled /></el-icon>
            <p class="dropzone-main">点击选择或拖拽图片到此处</p>
            <p class="dropzone-sub mono">{{ supportedTypes }} · ≤ {{ maxUploadMb }}MB</p>
          </div>

          <template v-else>
            <div class="preview-wrap">
              <img :src="previewUrl" class="preview-img" alt="待识别图片" />
              <div v-if="predicting" class="scanline" :style="{ top: scanOffset + '%' }"></div>
              <div v-if="predicting" class="preview-mask mono">INFERRING…</div>
            </div>
            <div class="preview-meta mono">
              <span class="preview-name">{{ previewName }}</span>
              <button class="reset-btn mono" type="button" @click="resetPreview">RESET</button>
            </div>
          </template>

          <input
            ref="fileInput"
            type="file"
            accept=".jpg,.jpeg,.png,.webp"
            style="display: none"
            @change="onFileChanged"
          />
        </section>

        <!-- 右：模型信息 + 结果 -->
        <section class="side-column">
          <div class="lab-panel info-panel">
            <div class="panel-label mono">MODEL // 模型信息</div>
            <dl class="meta-list mono">
              <div v-for="row in metaRows" :key="row.k" class="meta-row">
                <dt>{{ row.k }}</dt>
                <dd>{{ row.v }}</dd>
              </div>
            </dl>
            <p class="info-desc">{{ model.description }}</p>
          </div>

          <div class="lab-panel lab-panel--crossed result-panel">
            <div class="panel-label mono">OUTPUT // 推理结果</div>

            <div v-if="!result && !predicting && !predictError" class="result-empty">
              <el-icon><DataLine /></el-icon>
              <p>上传图片后，推理结果会显示在这里</p>
            </div>

            <div v-else-if="predicting" class="result-empty">
              <el-icon class="is-loading spinner"><Clock /></el-icon>
              <p class="mono">RUNNING INFERENCE…</p>
            </div>

            <el-alert
              v-else-if="predictError"
              type="error"
              :title="predictError"
              show-icon
              :closable="false"
            />

            <template v-else>
              <div class="result-headline">
                <span class="result-label">{{ typeLabel(result.label) }}</span>
                <el-tag type="success" effect="dark" round class="mono">
                  {{ formatPercent(result.confidence) }}
                </el-tag>
              </div>

              <div class="prob-list">
                <div v-for="row in probabilityRows" :key="row.label" class="prob-row">
                  <span class="prob-name mono">{{ row.label }}</span>
                  <el-progress
                    :percentage="Number((row.p * 100).toFixed(1))"
                    :stroke-width="10"
                    :show-text="false"
                    :color="row.label === result.label ? '#ff6b2c' : '#58a6ff'"
                    class="prob-bar"
                  />
                  <span class="prob-value mono">{{ formatPercent(row.p) }}</span>
                </div>
              </div>

              <div class="result-foot mono">
                <span class="foot-item">
                  <el-icon><Clock /></el-icon>
                  {{ result.latency_ms }}ms
                </span>
                <span class="foot-item">
                  <el-icon><Coin /></el-icon>
                  {{ result.label }} @ {{ formatPercent(result.confidence) }}
                </span>
              </div>
            </template>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-head {
  margin-bottom: 24px;
}

.back-link {
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--lab-ink-faint);
  text-decoration: none;
  display: inline-block;
  margin-bottom: 12px;
}

.back-link:hover {
  color: var(--lab-accent);
}

.detail-title {
  margin: 0 0 6px;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.detail-en {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.14em;
  color: var(--lab-ink-faint);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 22px;
  align-items: start;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.panel-label {
  font-size: 11px;
  letter-spacing: 0.14em;
  color: var(--lab-accent);
  margin-bottom: 16px;
}

.detail-skeleton {
  padding: 28px;
}

/* 上传面板 */
.upload-panel {
  padding: 22px;
  min-height: 380px;
  display: flex;
  flex-direction: column;
}

.dropzone {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1.5px dashed var(--lab-line-strong);
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
  padding: 48px 20px;
  outline: none;
}

.dropzone:hover,
.dropzone:focus-visible {
  border-color: var(--lab-accent);
  background: var(--lab-accent-soft);
}

.dropzone-icon {
  font-size: 46px;
  color: var(--lab-ink-faint);
}

.dropzone:hover .dropzone-icon {
  color: var(--lab-accent);
}

.dropzone-main {
  margin: 0;
  font-size: 15px;
  color: var(--lab-ink);
}

.dropzone-sub {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--lab-ink-faint);
}

.preview-wrap {
  position: relative;
  flex: 1;
  display: grid;
  place-items: center;
  border-radius: 12px;
  overflow: hidden;
  background: #0b0d11;
  min-height: 280px;
}

.preview-img {
  max-width: 100%;
  max-height: 360px;
  object-fit: contain;
}

.scanline {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--lab-accent), transparent);
  box-shadow: 0 0 18px 2px rgba(255, 107, 44, 0.55);
}

.preview-mask {
  position: absolute;
  bottom: 10px;
  left: 12px;
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--lab-accent);
  animation: blink 1.1s steps(2, start) infinite;
}

@keyframes blink {
  to {
    visibility: hidden;
  }
}

.preview-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
  font-size: 12px;
  color: var(--lab-ink-dim);
}

.preview-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reset-btn {
  border: 1px solid var(--lab-line-strong);
  background: transparent;
  color: var(--lab-ink-dim);
  font-size: 11px;
  letter-spacing: 0.12em;
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
}

.reset-btn:hover {
  border-color: var(--lab-accent);
  color: var(--lab-accent);
}

/* 信息面板 */
.info-panel {
  padding: 20px 22px;
}

.meta-list {
  margin: 0 0 12px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 7px 0;
  border-bottom: 1px dashed var(--lab-line);
  font-size: 12px;
}

.meta-row:last-child {
  border-bottom: none;
}

.meta-row dt {
  color: var(--lab-ink-faint);
  letter-spacing: 0.1em;
}

.meta-row dd {
  margin: 0;
  color: var(--lab-ink);
  text-align: right;
  word-break: break-all;
}

.info-desc {
  margin: 0;
  font-size: 13px;
  color: var(--lab-ink-dim);
  line-height: 1.8;
}

/* 结果面板 */
.result-panel {
  padding: 20px 22px;
  min-height: 220px;
}

.result-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 30px 0;
  color: var(--lab-ink-faint);
  font-size: 13px;
}

.result-empty .el-icon {
  font-size: 30px;
}

.spinner {
  color: var(--lab-accent);
}

.result-headline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.result-label {
  font-size: 34px;
  font-weight: 900;
  letter-spacing: 0.06em;
  color: var(--lab-ink);
}

.prob-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.prob-row {
  display: grid;
  grid-template-columns: 52px 1fr 56px;
  align-items: center;
  gap: 10px;
}

.prob-name {
  font-size: 12px;
  color: var(--lab-ink-dim);
}

.prob-bar {
  flex: 1;
}

.prob-value {
  font-size: 12px;
  color: var(--lab-ink);
  text-align: right;
}

.result-foot {
  display: flex;
  gap: 18px;
  padding-top: 12px;
  border-top: 1px dashed var(--lab-line);
  font-size: 11px;
  color: var(--lab-ink-faint);
}

.foot-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

@media (max-width: 860px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .detail-title {
    font-size: 26px;
  }
}
</style>
