<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowRight } from '@element-plus/icons-vue';
import api from '../api';
import { errMessage, formatPercent, formatTime } from '../utils/format';

const router = useRouter();

const loading = ref(true);
const items = ref([]);
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

const modelNames = {
  'cat-dog': '猫狗图像二分类',
};

async function load() {
  loading.value = true;
  try {
    const resp = await api.getHistory(page.value, pageSize.value);
    items.value = (resp && resp.items) || [];
    total.value = (resp && resp.total) || 0;
  } catch (e) {
    items.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

function changePage(p) {
  page.value = p;
  load();
}

onMounted(load);
</script>

<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">识别记录</h1>
        <p class="lab-eyebrow">HISTORY // 本次账号的全部推理留痕</p>
      </div>
    </div>

    <div class="lab-panel table-panel">
      <el-table v-loading="loading" :data="items" style="width: 100%" empty-text="还没有记录，去体验一次识别吧">
        <el-table-column label="时间" width="150">
          <template #default="{ row }">
            <span class="cell-dim mono">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="模型" min-width="150">
          <template #default="{ row }">
            <span>{{ modelNames[row.model_id] || row.model_id }}</span>
            <span class="cell-id mono">{{ row.model_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="110">
          <template #default="{ row }">
            <el-tag
              v-if="row.status === 'success'"
              type="success"
              effect="plain"
              round
            >
              {{ row.result_label_cn || row.result_label }}
            </el-tag>
            <el-tag v-else type="danger" effect="plain" round>失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="170">
          <template #default="{ row }">
            <template v-if="row.status === 'success'">
              <el-progress
                :percentage="Number(((row.confidence || 0) * 100).toFixed(1))"
                :stroke-width="8"
                :show-text="false"
                color="#ff6b2c"
                class="cell-progress"
              />
              <span class="cell-confidence mono">{{ formatPercent(row.confidence) }}</span>
            </template>
            <span v-else class="cell-dim">--</span>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="90">
          <template #default="{ row }">
            <span class="cell-dim mono">{{ row.latency_ms != null ? row.latency_ms + 'ms' : '--' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row" v-if="total > pageSize">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="changePage"
        />
      </div>
    </div>

    <div class="history-cta">
      <span class="cta-text">想再试几张？</span>
      <el-button type="primary" round :icon="ArrowRight" @click="router.push('/')">
        去模型广场
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 22px;
}

.page-title {
  margin: 0 0 6px;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.table-panel {
  padding: 8px 6px;
}

.cell-dim {
  font-size: 12.5px;
  color: var(--lab-ink-dim);
}

.cell-id {
  display: block;
  font-size: 10.5px;
  color: var(--lab-ink-faint);
  letter-spacing: 0.08em;
}

.cell-progress {
  width: 90px;
  display: inline-flex;
  vertical-align: middle;
}

.cell-confidence {
  margin-left: 8px;
  font-size: 12px;
  color: var(--lab-ink);
  vertical-align: middle;
}

.pagination-row {
  display: flex;
  justify-content: center;
  padding: 16px 0 10px;
}

.history-cta {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 22px;
}

.cta-text {
  font-size: 13.5px;
  color: var(--lab-ink-dim);
}
</style>
