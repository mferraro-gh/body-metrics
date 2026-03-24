<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Track your body composition over time.</p>
      </div>
      <router-link to="/upload" class="btn btn-primary"
        >+ Upload Scan</router-link
      >
    </div>

    <!-- Profile selector -->
    <div class="profile-bar">
      <label class="form-label">Profile</label>
      <select
        v-model="selectedProfile"
        class="profile-select"
        @change="loadScans"
      >
        <option value="">— Select a profile —</option>
        <option v-for="p in profiles" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <!-- Empty states -->
    <div v-if="profiles.length === 0" class="welcome-screen">
      <div class="watermark-bg">
        <span class="wm-word">BODY</span>
        <span class="wm-word">METRICS</span>
      </div>
      <div class="welcome-content">
        <p class="welcome-tagline">Track your body composition over time.</p>
        <div class="steps">
          <div class="step">
            <div class="step-number">01</div>
            <div class="step-body">
              <div class="step-title">Upload a scan</div>
              <div class="step-desc">Drop any InBody PNG or JPG report — metrics are extracted automatically via OCR.</div>
            </div>
          </div>
          <div class="step-divider"></div>
          <div class="step">
            <div class="step-number">02</div>
            <div class="step-body">
              <div class="step-title">Review & correct</div>
              <div class="step-desc">Check the extracted values and fix anything the OCR got wrong before saving.</div>
            </div>
          </div>
          <div class="step-divider"></div>
          <div class="step">
            <div class="step-number">03</div>
            <div class="step-body">
              <div class="step-title">Track progress</div>
              <div class="step-desc">Compare metrics across scans with charts, filters, and side-by-side profile views.</div>
            </div>
          </div>
        </div>
        <router-link to="/upload" class="btn btn-primary welcome-cta">
          Upload your first scan
        </router-link>
      </div>
    </div>

    <div v-else-if="!selectedProfile" class="empty-state">
      <div class="empty-icon">👤</div>
      <p>Select a profile above to view their progress.</p>
    </div>

    <template v-else>
      <!-- Loading -->
      <div v-if="loading" class="loading-row">
        <span class="spinner"></span> Loading scans…
      </div>

      <template v-else-if="scans.length > 0">
        <!-- Latest metrics summary -->
        <section>
          <h2 class="section-title">
            Latest Results — {{ formatDate(latestScan.scan_date) }}
          </h2>
          <div class="metrics-grid">
            <MetricCard
              label="InBody Score"
              :value="latestScan.inbody_score"
              unit="/ 100"
              :status="scoreStatus(latestScan.inbody_score)"
            />
            <MetricCard label="Peso" :value="latestScan.weight" unit="kg" />
            <MetricCard
              label="Masa Muscular"
              :value="latestScan.skeletal_muscle_mass"
              unit="kg"
            />
            <MetricCard
              label="Masa Grasa"
              :value="latestScan.body_fat_mass"
              unit="kg"
            />
            <MetricCard
              label="Grasa Corporal"
              :value="latestScan.body_fat_percent"
              unit="%"
              :status="
                bfpStatus(latestScan.body_fat_percent, latestScan.gender)
              "
            />
            <MetricCard
              label="IMC"
              :value="latestScan.bmi"
              :status="bmiStatus(latestScan.bmi)"
            />
            <MetricCard
              label="Grasa Visceral"
              :value="latestScan.visceral_fat_level"
              :status="visceralStatus(latestScan.visceral_fat_level)"
            />
            <MetricCard
              label="Agua Corporal"
              :value="latestScan.total_body_water"
              unit="L"
            />
          </div>
        </section>

        <!-- Progress chart -->
        <section class="card chart-section">
          <div class="chart-header">
            <h2 class="section-title" style="margin-bottom: 0">
              Progress Over Time
            </h2>
            <div class="chart-metric-toggles">
              <label
                v-for="m in availableMetrics"
                :key="m.key"
                class="toggle-label"
              >
                <input
                  type="checkbox"
                  v-model="selectedMetrics"
                  :value="m.key"
                />
                <span
                  class="toggle-dot"
                  :style="{ background: m.color }"
                ></span>
                {{ m.label }}
              </label>
            </div>
          </div>
          <ProgressChart :scans="sortedScans" :metrics="selectedMetrics" />
        </section>

        <!-- Scan history -->
        <section>
          <div class="history-header">
            <h2 class="section-title" style="margin-bottom: 0">Scan History</h2>
            <div class="date-filter">
              <button
                v-for="r in dateRanges"
                :key="r.key"
                class="range-btn"
                :class="{ active: dateRange === r.key }"
                @click="dateRange = r.key"
              >
                {{ r.label }}
              </button>
              <div class="date-inputs">
                <input
                  type="date"
                  v-model="dateFrom"
                  class="date-input"
                  title="From"
                />
                <span class="date-sep">–</span>
                <input
                  type="date"
                  v-model="dateTo"
                  class="date-input"
                  title="To"
                />
              </div>
            </div>
          </div>
          <div class="scan-list">
            <div
              v-for="scan in filteredScans"
              :key="scan.id"
              class="scan-item card"
            >
              <div class="scan-item-left">
                <div class="scan-date">
                  {{ formatDate(scan.scan_date) || `Scan #${scan.id}` }}
                </div>
                <div class="scan-chips">
                  <span v-if="scan.inbody_score" class="chip chip-score">
                    Score: {{ scan.inbody_score }}/100
                  </span>
                  <span v-if="scan.weight" class="chip"
                    >{{ scan.weight }} kg</span
                  >
                  <span v-if="scan.body_fat_percent" class="chip"
                    >{{ scan.body_fat_percent }}% grasa</span
                  >
                  <span v-if="scan.bmi" class="chip">IMC {{ scan.bmi }}</span>
                </div>
              </div>
              <div class="scan-item-right">
                <a
                  v-if="scan.image_filename"
                  :href="`/data/${scan.image_filename}`"
                  target="_blank"
                  class="btn btn-ghost btn-sm"
                  >View Image</a
                >
                <button
                  class="btn btn-danger btn-sm"
                  @click="deleteScan(scan.id)"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </section>
      </template>

      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>
          No scans found for <strong>{{ selectedProfile }}</strong
          >. <router-link to="/upload">Upload one now.</router-link>
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const route = useRoute();
import MetricCard from "../components/MetricCard.vue";
import ProgressChart from "../components/ProgressChart.vue";

function formatDate(dateStr) {
  if (!dateStr) return dateStr;
  const [y, m, d] = dateStr.split("-");
  if (!y || !m || !d) return dateStr;
  return `${m}/${d}/${y}`;
}

const profiles = ref([]);
const selectedProfile = ref("");
const scans = ref([]);
const loading = ref(false);

const availableMetrics = [
  { key: "weight", label: "Peso", color: "#00c9a0" },
  { key: "skeletal_muscle_mass", label: "Músculo", color: "#58a6ff" },
  { key: "body_fat_percent", label: "Grasa %", color: "#ffa657" },
  { key: "bmi", label: "IMC", color: "#d2a8ff" },
];
const selectedMetrics = ref([
  "weight",
  "skeletal_muscle_mass",
  "body_fat_percent",
]);

const dateRange = ref("all");
const dateFrom = ref("");
const dateTo = ref("");

watch([dateFrom, dateTo], () => {
  if (dateFrom.value || dateTo.value) dateRange.value = "all";
});

const dateRanges = [
  { key: "all", label: "All" },
  { key: "30d", label: "30 d" },
  { key: "3mo", label: "3 mo" },
  { key: "6mo", label: "6 mo" },
  { key: "1yr", label: "1 yr" },
];

function rangeStart(key) {
  const d = new Date();
  if (key === "30d") {
    d.setDate(d.getDate() - 30);
  } else if (key === "3mo") {
    d.setMonth(d.getMonth() - 3);
  } else if (key === "6mo") {
    d.setMonth(d.getMonth() - 6);
  } else if (key === "1yr") {
    d.setFullYear(d.getFullYear() - 1);
  } else return null;
  return d.toISOString().slice(0, 10);
}

const filteredScans = computed(() => {
  let from =
    dateRange.value !== "all"
      ? rangeStart(dateRange.value)
      : dateFrom.value || null;
  let to = dateTo.value || null;
  return scans.value.filter((s) => {
    if (!s.scan_date) return true;
    if (from && s.scan_date < from) return false;
    if (to && s.scan_date > to) return false;
    return true;
  });
});

const latestScan = computed(() => scans.value[0] || {});
const sortedScans = computed(() =>
  [...scans.value].sort((a, b) =>
    (a.scan_date || "").localeCompare(b.scan_date || ""),
  ),
);

async function loadProfiles() {
  const res = await axios.get("/api/profiles");
  profiles.value = res.data;
}

async function loadScans() {
  if (!selectedProfile.value) {
    scans.value = [];
    return;
  }
  loading.value = true;
  try {
    const res = await axios.get("/api/scans", {
      params: { profile: selectedProfile.value },
    });
    scans.value = res.data;
  } finally {
    loading.value = false;
  }
}

async function deleteScan(id) {
  if (!confirm("Delete this scan?")) return;
  await axios.delete(`/api/scans/${id}`);
  scans.value = scans.value.filter((s) => s.id !== id);
}

// Status helpers
function scoreStatus(score) {
  if (!score) return null;
  if (score >= 80) return "normal";
  if (score >= 60) return "low";
  return "low";
}
function bfpStatus(pct, gender) {
  if (!pct) return null;
  const isMale = gender === "M";
  if (isMale) return pct < 25 ? "normal" : "high";
  return pct < 32 ? "normal" : "high";
}
function bmiStatus(bmi) {
  if (!bmi) return null;
  if (bmi < 18.5) return "low";
  if (bmi < 25) return "normal";
  if (bmi < 30) return "high";
  return "high";
}
function visceralStatus(level) {
  if (!level) return null;
  return level <= 9 ? "normal" : "high";
}

onMounted(async () => {
  await loadProfiles()
  if (route.query.profile) {
    selectedProfile.value = route.query.profile
    loadScans()
  }
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.page-title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 4px;
}
.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

.profile-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}
.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
}
.profile-select {
  min-width: 220px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
}

.chart-section {
  padding: 24px;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
.chart-metric-toggles {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}
.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}
.toggle-label input {
  accent-color: var(--accent);
}
.toggle-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.date-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.range-btn {
  padding: 5px 11px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.range-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}
.range-btn.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
}
.date-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 4px;
}
.date-input {
  padding: 5px 8px;
  font-size: 12px;
  width: 130px;
}
.date-sep {
  font-size: 12px;
  color: var(--text-muted);
}

.scan-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.scan-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  flex-wrap: wrap;
  gap: 12px;
}
.scan-date {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 6px;
}
.scan-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.chip {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-muted);
}
.chip-score {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
.scan-item-right {
  display: flex;
  gap: 8px;
}
.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 24px;
  color: var(--text-muted);
  text-align: center;
}
.empty-icon {
  font-size: 40px;
}
.empty-state a {
  color: var(--accent);
}

/* ── Welcome / watermark screen ── */
.welcome-screen {
  position: relative;
  min-height: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: var(--radius);
}

.watermark-bg {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0;
  pointer-events: none;
  user-select: none;
}
.wm-word {
  font-size: clamp(72px, 16vw, 160px);
  font-weight: 900;
  letter-spacing: 0.12em;
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px var(--border);
  opacity: 0.35;
}

.welcome-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 36px;
  text-align: center;
  padding: 48px 24px;
}

.welcome-tagline {
  font-size: 15px;
  color: var(--text-muted);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 500;
}

.steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
  flex-wrap: wrap;
  justify-content: center;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: 190px;
  padding: 0 20px;
}

.step-number {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--accent);
  opacity: 0.8;
  font-variant-numeric: tabular-nums;
}

.step-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.step-divider {
  width: 32px;
  height: 1px;
  background: var(--border);
  margin-top: 24px;
  flex-shrink: 0;
}

.welcome-cta {
  padding: 11px 28px;
  font-size: 14px;
}

.loading-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  padding: 24px 0;
}
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
