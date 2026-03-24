<template>
  <div class="compare-view">
    <div class="compare-header">
      <div>
        <h1 class="page-title">Compare Profiles</h1>
        <p class="page-subtitle">
          Select profiles and choose which scan to compare for each one.
        </p>
      </div>
    </div>

    <!-- Profile multi-select + scan pickers -->
    <div class="card selector-card">
      <div class="selector-header">
        <span class="section-title" style="margin-bottom: 0">Select Profiles</span>
      </div>

      <div v-if="allProfiles.length === 0" class="no-profiles">
        No profiles available.
        <router-link to="/upload">Upload a scan</router-link> first.
      </div>

      <div v-else class="profile-chips">
        <label
          v-for="p in allProfiles"
          :key="p"
          class="profile-chip"
          :class="{ 'profile-chip--selected': selectedProfiles.includes(p) }"
        >
          <input
            type="checkbox"
            :value="p"
            v-model="selectedProfiles"
            @change="onProfileToggle(p)"
            style="display: none"
          />
          {{ p }}
        </label>
      </div>

      <!-- Per-profile scan selectors -->
      <div v-if="selectedProfiles.length > 0" class="scan-selectors">
        <div v-for="p in selectedProfiles" :key="p" class="scan-selector-row">
          <span class="scan-selector-name">{{ p }}</span>
          <div class="scan-selector-right">
            <span v-if="loadingScans[p]" class="scan-loading">
              <span class="spinner-xs"></span> Loading…
            </span>
            <select
              v-else-if="profileScans[p]?.length"
              v-model="selectedScanIds[p]"
              class="scan-select"
              @change="buildComparison"
            >
              <option v-for="s in profileScans[p]" :key="s.id" :value="s.id">
                {{ formatDate(s.scan_date) || `Scan #${s.id}` }}
                {{ s.inbody_score ? `· Score ${s.inbody_score}` : "" }}
                {{ s.weight ? `· ${s.weight} kg` : "" }}
              </option>
            </select>
            <span v-else class="scan-loading">No scans found</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <span class="spinner"></span> Loading comparison…
    </div>

    <template v-else-if="selectedProfiles.length >= 1 && Object.keys(comparisonData).length > 0">

      <!-- ── Metrics Comparison ── -->
      <div class="card table-card">
        <div class="card-toolbar">
          <h2 class="section-title" style="margin-bottom:0">Metrics Comparison</h2>
          <div class="view-tabs">
            <button class="view-tab" :class="{ active: compView === 'table' }" @click="compView = 'table'">
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M0 2a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V2zm0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V7zm0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1v-2z"/></svg>
              Table
            </button>
            <button class="view-tab" :class="{ active: compView === 'chart' }" @click="compView = 'chart'">
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M0 13a.5.5 0 0 0 .5.5h15a.5.5 0 0 0 0-1H1V1.5a.5.5 0 0 0-1 0v11.5zm3-2h2a.5.5 0 0 0 .5-.5V7a.5.5 0 0 0-.5-.5H3a.5.5 0 0 0-.5.5v3.5a.5.5 0 0 0 .5.5zm4 0h2a.5.5 0 0 0 .5-.5V4a.5.5 0 0 0-.5-.5H7a.5.5 0 0 0-.5.5v6.5a.5.5 0 0 0 .5.5zm4 0h2a.5.5 0 0 0 .5-.5V2a.5.5 0 0 0-.5-.5h-2a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 .5.5z"/></svg>
              Chart
            </button>
          </div>
        </div>

        <div v-if="compView === 'table'" class="table-scroll">
          <table class="compare-table">
            <thead>
              <tr>
                <th class="metric-col">Metric</th>
                <th v-for="(p, i) in selectedProfiles" :key="p" class="profile-col">
                  <div class="profile-th">
                    <span class="profile-dot" :style="{ background: profileColor(i) }"></span>
                    <span class="profile-name">{{ p }}</span>
                    <span class="scan-date-sub">{{ formatDate(comparisonData[p]?.scan_date) || "—" }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in metricRows" :key="row.key">
                <td class="metric-name">{{ row.label }}</td>
                <td
                  v-for="p in selectedProfiles"
                  :key="p"
                  class="metric-val"
                  :class="cellClass(row.key, comparisonData[p]?.[row.key], comparisonData[p]?.gender)"
                >
                  <span class="val-text">
                    {{ formatVal(comparisonData[p]?.[row.key]) }}
                    <span v-if="row.unit && comparisonData[p]?.[row.key] != null" class="val-unit">{{ row.unit }}</span>
                  </span>
                  <span
                    v-if="getStatus(row.key, comparisonData[p]?.[row.key], comparisonData[p]?.gender)"
                    class="badge"
                    :class="statusBadgeClass(getStatus(row.key, comparisonData[p]?.[row.key], comparisonData[p]?.gender))"
                  >
                    {{ statusLabel(getStatus(row.key, comparisonData[p]?.[row.key], comparisonData[p]?.gender)) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="chart-area">
          <Bar :data="compChartData" :options="compChartOptions" />
        </div>
      </div>

      <!-- ── Tendencies ── -->
      <div class="card table-card" v-if="hasTendencies">
        <div class="card-toolbar">
          <h2 class="section-title" style="margin-bottom:0">Tendencies vs Previous Scan</h2>
          <div class="view-tabs">
            <button class="view-tab" :class="{ active: tendView === 'table' }" @click="tendView = 'table'">
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M0 2a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V2zm0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V7zm0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1v-2z"/></svg>
              Table
            </button>
            <button class="view-tab" :class="{ active: tendView === 'chart' }" @click="tendView = 'chart'">
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M0 13a.5.5 0 0 0 .5.5h15a.5.5 0 0 0 0-1H1V1.5a.5.5 0 0 0-1 0v11.5zm3-2h2a.5.5 0 0 0 .5-.5V7a.5.5 0 0 0-.5-.5H3a.5.5 0 0 0-.5.5v3.5a.5.5 0 0 0 .5.5zm4 0h2a.5.5 0 0 0 .5-.5V4a.5.5 0 0 0-.5-.5H7a.5.5 0 0 0-.5.5v6.5a.5.5 0 0 0 .5.5zm4 0h2a.5.5 0 0 0 .5-.5V2a.5.5 0 0 0-.5-.5h-2a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 .5.5z"/></svg>
              Chart
            </button>
          </div>
        </div>

        <div v-if="tendView === 'table'" class="table-scroll">
          <table class="compare-table">
            <thead>
              <tr>
                <th class="metric-col">Metric</th>
                <th v-for="(p, i) in selectedProfiles" :key="p" class="profile-col">
                  <div class="profile-th">
                    <span class="profile-dot" :style="{ background: profileColor(i) }"></span>
                    <span class="profile-name">{{ p }}</span>
                    <span class="scan-date-sub" v-if="previousScans[p]">
                      {{ formatDate(previousScans[p].scan_date) }} → {{ formatDate(comparisonData[p]?.scan_date) }}
                    </span>
                    <span class="scan-date-sub no-prev" v-else>No previous scan</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in numericMetricRows" :key="row.key">
                <td class="metric-name">{{ row.label }}</td>
                <td v-for="p in selectedProfiles" :key="p" class="metric-val">
                  <template v-if="getDelta(p, row.key) !== null">
                    <div class="delta-cell">
                      <span
                        class="delta-pill"
                        :class="{
                          'delta-up': getDelta(p, row.key) > 0,
                          'delta-down': getDelta(p, row.key) < 0,
                          'delta-flat': getDelta(p, row.key) === 0,
                        }"
                      >
                        <span class="delta-arrow">{{ getDelta(p, row.key) > 0 ? "▲" : getDelta(p, row.key) < 0 ? "▼" : "—" }}</span>
                        {{ formatDelta(getDelta(p, row.key)) }}
                        <span v-if="row.unit" class="val-unit">{{ row.unit }}</span>
                      </span>
                      <span
                        v-if="getPct(p, row.key) !== null"
                        class="delta-pct"
                        :class="{
                          'delta-up': getDelta(p, row.key) > 0,
                          'delta-down': getDelta(p, row.key) < 0,
                          'delta-flat': getDelta(p, row.key) === 0,
                        }"
                      >{{ formatPct(getPct(p, row.key)) }}</span>
                    </div>
                  </template>
                  <span v-else class="no-delta">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="chart-area">
          <Bar :data="tendChartData" :options="tendChartOptions" />
        </div>
      </div>

      <!-- Body composition -->
      <div class="card chart-card">
        <h2 class="section-title">Body Composition</h2>
        <div class="bar-chart-grid">
          <div v-for="p in selectedProfiles" :key="p" class="composition-block">
            <div class="composition-title">{{ p }}</div>
            <div v-if="comparisonData[p]" class="composition-bars">
              <div
                v-for="seg in getCompositionSegments(comparisonData[p])"
                :key="seg.key"
                class="comp-seg"
                :style="{ background: seg.color, flex: seg.value || 0 }"
                :title="`${seg.label}: ${seg.value} kg`"
              ></div>
            </div>
            <div class="composition-legend">
              <div v-for="seg in getCompositionSegments(comparisonData[p])" :key="seg.key" class="legend-item">
                <span class="legend-dot" :style="{ background: seg.color }"></span>
                <span>{{ seg.label }}: <strong>{{ seg.value ?? "—" }}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="selectedProfiles.length === 0" class="empty-state">
      <div class="empty-icon">⚖️</div>
      <p>Select two or more profiles above to compare them.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import axios from "axios";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

// ── State ─────────────────────────────────────────────────────────────────────
const allProfiles   = ref([]);
const selectedProfiles = ref([]);
const profileScans  = reactive({});
const selectedScanIds = reactive({});
const loadingScans  = reactive({});
const previousScans = reactive({});
const comparisonData = ref({});
const loading = ref(false);
const compView = ref("table");
const tendView = ref("table");

// ── Metric definitions ────────────────────────────────────────────────────────
const numericMetricRows = [
  { key: "weight",               label: "Peso",           unit: "kg"    },
  { key: "skeletal_muscle_mass", label: "Masa Muscular",  unit: "kg"    },
  { key: "body_fat_mass",        label: "Masa Grasa",     unit: "kg"    },
  { key: "body_fat_percent",     label: "Grasa Corporal", unit: "%"     },
  { key: "total_body_water",     label: "Agua Corporal",  unit: "L"     },
  { key: "minerals",             label: "Minerales",      unit: "kg"    },
  { key: "bmi",                  label: "IMC",            unit: ""      },
  { key: "visceral_fat_level",   label: "Grasa Visceral", unit: ""      },
  { key: "inbody_score",         label: "InBody Score",   unit: "/ 100" },
];

const metricRows = [
  ...numericMetricRows,
  { key: "waist_hip_ratio", label: "Cintura-Cadera", unit: ""     },
  { key: "height",          label: "Altura",         unit: "cm"   },
  { key: "age",             label: "Edad",           unit: "años" },
  { key: "gender",          label: "Género",         unit: ""     },
];

// ── Profile color palette ─────────────────────────────────────────────────────
const PALETTE = ["#00c9a0", "#58a6ff", "#ffa657", "#d2a8ff", "#ff7b72", "#3fb950"];
function profileColor(i) { return PALETTE[i % PALETTE.length]; }

// ── Formatters ────────────────────────────────────────────────────────────────
function formatDate(s) {
  if (!s) return s;
  const [y, m, d] = s.split("-");
  if (!y || !m || !d) return s;
  return `${m}/${d}/${y}`;
}
function formatVal(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return Number.isInteger(v) ? v : v.toFixed(1);
  return v;
}
function formatDelta(val) {
  if (val === null) return "—";
  const sign = val > 0 ? "+" : "";
  return sign + (Number.isInteger(val) ? val : val.toFixed(1));
}
function formatPct(val) {
  if (val === null) return null;
  return (val > 0 ? "+" : "") + val.toFixed(1) + "%";
}

// ── Status helpers ────────────────────────────────────────────────────────────
function getStatus(key, value, gender) {
  if (value == null) return null;
  if (key === "bmi") return value < 18.5 ? "low" : value < 25 ? "normal" : "high";
  if (key === "body_fat_percent") return value < (gender === "M" ? 25 : 32) ? "normal" : "high";
  if (key === "visceral_fat_level") return value <= 9 ? "normal" : "high";
  if (key === "inbody_score") return value >= 80 ? "normal" : "low";
  return null;
}
function cellClass(key, value, gender) {
  const s = getStatus(key, value, gender);
  return s === "normal" ? "cell-good" : s === "high" ? "cell-bad" : s === "low" ? "cell-warn" : "";
}
function statusBadgeClass(s) {
  return s === "normal" ? "badge-good" : s === "high" ? "badge-bad" : "badge-warn";
}
function statusLabel(s) {
  return s === "normal" ? "Normal" : s === "high" ? "Alto" : "Bajo";
}

// ── Delta helpers ─────────────────────────────────────────────────────────────
function getDelta(p, key) {
  const curr = comparisonData.value[p]?.[key];
  const prev = previousScans[p]?.[key];
  if (curr == null || prev == null || typeof curr !== "number") return null;
  return curr - prev;
}
function getPct(p, key) {
  const prev = previousScans[p]?.[key];
  const delta = getDelta(p, key);
  if (delta == null || !prev) return null;
  return (delta / prev) * 100;
}
const hasTendencies = computed(() =>
  selectedProfiles.value.some((p) => previousScans[p] != null),
);

// ── Chart shared config ───────────────────────────────────────────────────────
function makeChartOptions(tooltipCallback) {
  return {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: "#8b949e", font: { size: 12 }, padding: 16 } },
      tooltip: {
        backgroundColor: "#1c2230",
        borderColor: "#30363d",
        borderWidth: 1,
        titleColor: "#e6edf3",
        bodyColor: "#8b949e",
        callbacks: { label: tooltipCallback },
      },
    },
    scales: {
      x: { ticks: { color: "#8b949e", font: { size: 11 } }, grid: { color: "#30363d" } },
      y: { ticks: { color: "#8b949e", font: { size: 11 } }, grid: { color: "#1e2736" } },
    },
  };
}

// ── Comparison chart ──────────────────────────────────────────────────────────
const compChartData = computed(() => ({
  labels: numericMetricRows.map((r) => r.label),
  datasets: selectedProfiles.value.map((p, i) => ({
    label: `${p} (${formatDate(comparisonData.value[p]?.scan_date) || "—"})`,
    data: numericMetricRows.map((r) => comparisonData.value[p]?.[r.key] ?? null),
    backgroundColor: profileColor(i) + "99",
    borderColor: profileColor(i),
    borderWidth: 1,
    borderRadius: 4,
  })),
}));

const compChartOptions = makeChartOptions((ctx) => {
  const row = numericMetricRows[ctx.dataIndex];
  const v = ctx.raw;
  if (v == null) return `${ctx.dataset.label}: —`;
  const display = typeof v === "number" && !Number.isInteger(v) ? v.toFixed(1) : v;
  return `${ctx.dataset.label}: ${display}${row?.unit ? " " + row.unit : ""}`;
});

// ── Tendencies chart ──────────────────────────────────────────────────────────
const tendChartData = computed(() => ({
  labels: numericMetricRows.map((r) => r.label),
  datasets: selectedProfiles.value
    .filter((p) => previousScans[p] != null)
    .map((p) => {
      const deltas = numericMetricRows.map((r) => getDelta(p, r.key));
      return {
        label: p,
        data: deltas,
        backgroundColor: deltas.map((d) =>
          d == null ? "#30363d44" : d > 0 ? "#f8514966" : "#3fb95066",
        ),
        borderColor: deltas.map((d) =>
          d == null ? "#30363d" : d > 0 ? "#f85149" : "#3fb950",
        ),
        borderWidth: 1,
        borderRadius: 4,
      };
    }),
}));

const tendChartOptions = makeChartOptions((ctx) => {
  const profilesWithPrev = selectedProfiles.value.filter((p) => previousScans[p] != null);
  const p = profilesWithPrev[ctx.datasetIndex];
  const row = numericMetricRows[ctx.dataIndex];
  const delta = ctx.raw;
  if (delta === null) return `${p}: no data`;
  const pct = getPct(p, row.key);
  const sign = delta > 0 ? "+" : "";
  const display = typeof delta === "number" && !Number.isInteger(delta) ? delta.toFixed(1) : delta;
  const pctStr = pct !== null ? ` (${sign}${pct.toFixed(1)}%)` : "";
  return `${p}: ${sign}${display}${row?.unit ? " " + row.unit : ""}${pctStr}`;
});

// ── Composition ───────────────────────────────────────────────────────────────
function getCompositionSegments(scan) {
  return [
    { key: "water",  label: "Agua",      value: scan?.total_body_water,    color: "#58a6ff" },
    { key: "muscle", label: "Músculo",   value: scan?.skeletal_muscle_mass, color: "#00c9a0" },
    { key: "fat",    label: "Grasa",     value: scan?.body_fat_mass,        color: "#f85149" },
    { key: "min",    label: "Minerales", value: scan?.minerals,             color: "#d2a8ff" },
  ];
}

// ── Data loading ──────────────────────────────────────────────────────────────
async function loadProfiles() {
  const res = await axios.get("/api/profiles");
  allProfiles.value = res.data;
}

async function onProfileToggle(profile) {
  if (!selectedProfiles.value.includes(profile)) {
    delete profileScans[profile];
    delete selectedScanIds[profile];
    delete previousScans[profile];
    buildComparison();
    return;
  }
  loadingScans[profile] = true;
  try {
    const res = await axios.get("/api/scans", { params: { profile } });
    profileScans[profile] = res.data;
    if (res.data.length > 0) selectedScanIds[profile] = res.data[0].id;
    buildComparison();
  } finally {
    loadingScans[profile] = false;
  }
}

function buildComparison() {
  const result = {};
  for (const p of selectedProfiles.value) {
    const scans = profileScans[p];
    if (!scans) continue;
    const idx = scans.findIndex((s) => s.id === selectedScanIds[p]);
    if (idx !== -1) {
      result[p] = scans[idx];
      previousScans[p] = scans[idx + 1] ?? null;
    }
  }
  comparisonData.value = result;
}

onMounted(loadProfiles);
</script>

<style scoped>
.compare-view { display: flex; flex-direction: column; gap: 28px; }
.compare-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-title { font-size: 26px; font-weight: 700; margin-bottom: 4px; }
.page-subtitle { color: var(--text-muted); font-size: 14px; }

/* Selector card */
.selector-card { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.selector-header { display: flex; justify-content: space-between; align-items: center; }
.profile-chips { display: flex; gap: 10px; flex-wrap: wrap; }
.profile-chip {
  padding: 7px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;
  border: 1px solid var(--border); cursor: pointer; background: var(--bg-elevated);
  color: var(--text-muted); transition: all 0.15s;
}
.profile-chip--selected { background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }
.profile-chip:hover:not(.profile-chip--selected) { border-color: var(--text-muted); color: var(--text-primary); }
.no-profiles { color: var(--text-muted); font-size: 14px; }
.no-profiles a { color: var(--accent); }

/* Scan selectors */
.scan-selectors { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--border); padding-top: 16px; }
.scan-selector-row { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.scan-selector-name { font-size: 13px; font-weight: 600; color: var(--text-primary); min-width: 100px; }
.scan-selector-right { display: flex; align-items: center; gap: 8px; flex: 1; }
.scan-select { flex: 1; max-width: 380px; font-size: 13px; }
.scan-loading { font-size: 13px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.spinner-xs {
  width: 12px; height: 12px; border: 2px solid var(--border);
  border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}

/* Card toolbar */
.table-card { padding: 24px; overflow: hidden; }
.card-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; gap: 12px; flex-wrap: wrap;
}
.view-tabs {
  display: flex; gap: 2px; background: var(--bg-elevated);
  border: 1px solid var(--border); border-radius: var(--radius-xs); padding: 3px;
}
.view-tab {
  display: flex; align-items: center; gap: 5px; padding: 5px 10px; border: none;
  border-radius: 4px; background: transparent; color: var(--text-muted);
  font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.15s; font-family: inherit;
}
.view-tab:hover { color: var(--text-primary); }
.view-tab.active { background: var(--bg-base); color: var(--accent); box-shadow: 0 1px 3px rgba(0,0,0,0.2); }

/* Chart */
.chart-area { position: relative; height: 420px; width: 100%; }

/* Table */
.table-scroll { overflow-x: auto; }
.compare-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.compare-table th,
.compare-table td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); }
.compare-table th { color: var(--text-muted); font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-col { width: 200px; }
.profile-col { min-width: 200px; }
.profile-th { display: flex; flex-direction: column; gap: 3px; }
.profile-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.profile-name { font-size: 14px; font-weight: 600; color: var(--text-primary); text-transform: none; letter-spacing: 0; }
.scan-date-sub { font-size: 11px; color: var(--accent); font-weight: 500; letter-spacing: 0; text-transform: none; }
.metric-name { color: var(--text-muted); }
.metric-val { vertical-align: middle; }
.val-text { display: flex; align-items: baseline; gap: 4px; }
.val-unit { font-size: 12px; color: var(--text-muted); }
.cell-good { background: #3fb95008; }
.cell-bad  { background: #f8514908; }
.cell-warn { background: #d2992208; }
.compare-table tr:hover td { background: var(--bg-elevated) !important; }
.badge { display: inline-block; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 10px; margin-left: 6px; vertical-align: middle; }
.badge-good { background: var(--good-dim); color: var(--good); }
.badge-bad  { background: var(--danger-dim); color: var(--danger); }
.badge-warn { background: rgba(210,153,34,0.15); color: #d29922; }

/* Tendencies */
.no-prev { opacity: 0.5; }
.delta-cell { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.delta-pill { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; padding: 3px 9px; border-radius: 12px; }
.delta-arrow { font-size: 10px; }
.delta-pct { font-size: 12px; font-weight: 500; }
.delta-up   { color: var(--danger); background: var(--danger-dim); }
.delta-down { color: var(--good);   background: var(--good-dim); }
.delta-flat { color: var(--text-muted); background: var(--bg-elevated); }
.delta-pct.delta-up   { color: var(--danger); background: none; }
.delta-pct.delta-down { color: var(--good);   background: none; }
.delta-pct.delta-flat { color: var(--text-muted); background: none; }
.no-delta { color: var(--text-muted); font-size: 13px; }

/* Body composition */
.chart-card { padding: 24px; }
.bar-chart-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px; margin-top: 4px; }
.composition-block { display: flex; flex-direction: column; gap: 10px; }
.composition-title { font-weight: 600; font-size: 15px; }
.composition-bars { display: flex; height: 32px; border-radius: var(--radius-sm); overflow: hidden; gap: 2px; }
.comp-seg { min-width: 4px; transition: flex 0.4s ease; }
.composition-legend { display: flex; flex-direction: column; gap: 4px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* Empty / loading */
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 24px; color: var(--text-muted); text-align: center; }
.empty-icon { font-size: 40px; }
.loading-row { display: flex; align-items: center; gap: 10px; color: var(--text-muted); padding: 24px 0; }
.spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
