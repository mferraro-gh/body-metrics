<template>
  <div class="upload-view">

    <!-- ── Step 1: Form ── -->
    <template v-if="step === 'form'">
      <div class="page-header">
        <h1 class="page-title">Upload InBody Reports</h1>
        <p class="page-subtitle">
          Select one or more PNG / JPG scans — metrics are extracted
          automatically via OCR.
        </p>
      </div>

      <div class="card upload-card">
        <form @submit.prevent="handleSubmit">
          <!-- Drop zone -->
          <div
            class="drop-zone"
            :class="{
              'drop-zone--active': isDragging,
              'drop-zone--filled': selectedFiles.length > 0,
            }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".png,.jpg,.jpeg"
              multiple
              style="display: none"
              @change="onFileChange"
            />

            <div v-if="selectedFiles.length === 0" class="drop-placeholder">
              <div class="drop-icon">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <p class="drop-main">Drag &amp; drop InBody images here</p>
              <p class="drop-hint">or click to browse · PNG / JPG · multiple files OK</p>
            </div>

            <div v-else class="drop-filled-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
              </svg>
              {{ selectedFiles.length }} file{{ selectedFiles.length !== 1 ? 's' : '' }} selected
              <span class="drop-change">click to change</span>
            </div>
          </div>

          <!-- File list -->
          <ul v-if="selectedFiles.length > 0" class="file-list">
            <li v-for="(f, i) in selectedFiles" :key="i" class="file-item">
              <span class="file-thumb-wrap">
                <img :src="previewUrls[i]" class="file-thumb" alt="" />
              </span>
              <span class="file-name">{{ f.name }}</span>
              <span class="file-size">{{ formatSize(f.size) }}</span>
              <button
                type="button"
                class="file-remove"
                @click.stop="removeFile(i)"
                title="Remove"
              >✕</button>
            </li>
          </ul>

          <!-- Profile selector -->
          <div class="form-group">
            <label class="form-label">Profile</label>
            <div class="profile-row">
              <select
                v-model="profileSelection"
                class="form-input profile-select"
                :class="{ dimmed: profileSelection === '__new__' }"
              >
                <option value="" disabled>— Select a profile —</option>
                <option v-for="p in profiles" :key="p" :value="p">{{ p }}</option>
                <option value="__new__">＋ New profile…</option>
              </select>
              <input
                v-if="profileSelection === '__new__'"
                v-model="newProfileName"
                type="text"
                class="form-input profile-new-input"
                placeholder="Enter profile name"
                autofocus
              />
            </div>
          </div>

          <div v-if="error" class="alert alert-error">{{ error }}</div>

          <button
            type="submit"
            class="btn btn-primary submit-btn"
            :disabled="selectedFiles.length === 0 || !resolvedProfile"
          >
            Upload &amp; Extract{{ selectedFiles.length > 1 ? ` (${selectedFiles.length} scans)` : '' }}
          </button>
        </form>
      </div>
    </template>

    <!-- ── Step 2: Uploading progress ── -->
    <template v-if="step === 'uploading'">
      <div class="page-header">
        <h1 class="page-title">Extracting Metrics…</h1>
        <p class="page-subtitle">OCR may take 10–30 s on first run.</p>
      </div>

      <div class="card upload-card">
        <div class="progress-header">
          <span class="progress-label">
            {{ doneCount }} of {{ results.length }} complete
          </span>
          <span class="progress-pct">{{ Math.round(doneCount / results.length * 100) }}%</span>
        </div>
        <div class="progress-bar-track">
          <div
            class="progress-bar-fill"
            :style="{ width: (doneCount / results.length * 100) + '%' }"
          ></div>
        </div>

        <ul class="upload-status-list">
          <li v-for="r in results" :key="r.filename" class="upload-status-item">
            <img :src="r.previewUrl" class="status-thumb" alt="" />
            <span class="status-name">{{ r.filename }}</span>
            <span
              class="status-badge"
              :class="{
                'badge-wait': r.status === 'pending',
                'badge-active': r.status === 'uploading',
                'badge-done': r.status === 'done',
                'badge-error': r.status === 'error',
              }"
            >
              <span v-if="r.status === 'uploading'" class="spinner-sm"></span>
              {{ statusLabel(r.status) }}
            </span>
          </li>
        </ul>
      </div>
    </template>

    <!-- ── Step 3: Batch review ── -->
    <template v-if="step === 'review'">
      <div class="page-header">
        <div>
          <h1 class="page-title">Review Extracted Metrics</h1>
          <p class="page-subtitle">
            Expand any scan to correct values before saving.
          </p>
        </div>
        <div class="success-pill">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          {{ successCount }} of {{ results.length }} extracted
        </div>
      </div>

      <div
        v-for="(r, i) in results"
        :key="r.filename"
        class="scan-review-card card"
        :class="{ 'card--error': r.status === 'error' }"
      >
        <!-- Collapsed header -->
        <div class="scan-review-header" @click="toggleExpand(i)">
          <img :src="r.previewUrl" class="review-thumb" alt="" />
          <div class="scan-review-meta">
            <div class="scan-review-profile">{{ r.draft.profile_name }}</div>
            <div class="scan-review-date">
              {{ formatDate(r.draft.scan_date) || r.filename }}
            </div>
            <div v-if="r.status === 'error'" class="scan-review-err">
              OCR failed: {{ r.error }}
            </div>
            <div v-else class="scan-review-chips">
              <span v-if="r.draft.weight" class="chip">{{ r.draft.weight }} kg</span>
              <span v-if="r.draft.skeletal_muscle_mass" class="chip">{{ r.draft.skeletal_muscle_mass }} kg músculo</span>
              <span v-if="r.draft.body_fat_percent" class="chip">{{ r.draft.body_fat_percent }}% grasa</span>
              <span v-if="r.draft.inbody_score" class="chip chip-score">Score {{ r.draft.inbody_score }}/100</span>
            </div>
          </div>
          <button type="button" class="expand-btn" :class="{ expanded: r.expanded }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>

        <!-- Expanded editable grid -->
        <div v-if="r.expanded && r.status !== 'error'" class="scan-review-body">
          <div class="metrics-grid">
            <EditableMetricCard
              v-for="f in metricFields"
              :key="f.key"
              :label="f.label"
              :value="r.draft[f.key]"
              :unit="f.unit"
              :field-type="f.type"
              :step="f.step"
              @update="r.draft[f.key] = $event"
            />
          </div>
        </div>
      </div>

      <div v-if="saveError" class="alert alert-error">{{ saveError }}</div>

      <div class="review-actions">
        <button class="btn btn-ghost" @click="step = 'form'">← Back</button>
        <button class="btn btn-primary" @click="saveAllAndGo" :disabled="saving">
          <span v-if="saving" class="spinner"></span>
          {{ saving ? "Saving…" : `Save All & Go to Dashboard` }}
        </button>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import EditableMetricCard from "../components/EditableMetricCard.vue";

const router = useRouter();

const step = ref("form");
const fileInput = ref(null);
const selectedFiles = ref([]);
const previewUrls = ref([]);
const profileSelection = ref("");
const newProfileName = ref("");
const isDragging = ref(false);
const error = ref("");
const saving = ref(false);
const saveError = ref("");
const profiles = ref([]);
const results = ref([]); // [{filename, previewUrl, scanId, draft, status, error, expanded}]

const resolvedProfile = computed(() =>
  profileSelection.value === "__new__"
    ? newProfileName.value.trim()
    : profileSelection.value,
);

const doneCount = computed(() =>
  results.value.filter((r) => r.status === "done" || r.status === "error").length,
);
const successCount = computed(() =>
  results.value.filter((r) => r.status === "done").length,
);

const metricFields = [
  { key: "scan_date", label: "Scan Date", unit: "", type: "date", step: "" },
  { key: "weight", label: "Peso", unit: "kg", type: "number", step: "0.1" },
  { key: "skeletal_muscle_mass", label: "Masa Muscular", unit: "kg", type: "number", step: "0.1" },
  { key: "body_fat_mass", label: "Masa Grasa", unit: "kg", type: "number", step: "0.1" },
  { key: "body_fat_percent", label: "Grasa Corporal", unit: "%", type: "number", step: "0.1" },
  { key: "total_body_water", label: "Agua Corporal", unit: "L", type: "number", step: "0.1" },
  { key: "minerals", label: "Minerales", unit: "kg", type: "number", step: "0.01" },
  { key: "bmi", label: "IMC", unit: "", type: "number", step: "0.1" },
  { key: "visceral_fat_level", label: "Grasa Visceral", unit: "lvl", type: "number", step: "1" },
  { key: "waist_hip_ratio", label: "Cintura-Cadera", unit: "", type: "number", step: "0.01" },
  { key: "inbody_score", label: "InBody Score", unit: "/ 100", type: "number", step: "1" },
  { key: "height", label: "Altura", unit: "cm", type: "number", step: "1" },
  { key: "age", label: "Edad", unit: "años", type: "number", step: "1" },
  { key: "gender", label: "Género", unit: "", type: "select", step: "" },
];

function formatDate(dateStr) {
  if (!dateStr) return dateStr;
  const [y, m, d] = dateStr.split("-");
  if (!y || !m || !d) return dateStr;
  return `${m}/${d}/${y}`;
}

function formatSize(bytes) {
  return bytes < 1024 * 1024
    ? (bytes / 1024).toFixed(0) + " KB"
    : (bytes / 1024 / 1024).toFixed(1) + " MB";
}

function statusLabel(s) {
  return { pending: "Waiting", uploading: "Extracting…", done: "Done", error: "Failed" }[s];
}

function triggerFileInput() {
  fileInput.value?.click();
}

function onFileChange(e) {
  addFiles(Array.from(e.target.files));
  e.target.value = "";
}

function onDrop(e) {
  isDragging.value = false;
  addFiles(Array.from(e.dataTransfer.files));
}

function addFiles(files) {
  error.value = "";
  for (const f of files) {
    if (!f.type.match(/image\/(png|jpe?g)/)) {
      error.value = `"${f.name}" is not a PNG or JPG — skipped.`;
      continue;
    }
    // Avoid duplicates by name
    if (selectedFiles.value.some((x) => x.name === f.name)) continue;
    selectedFiles.value.push(f);
    previewUrls.value.push(URL.createObjectURL(f));
  }
}

function removeFile(i) {
  URL.revokeObjectURL(previewUrls.value[i]);
  selectedFiles.value.splice(i, 1);
  previewUrls.value.splice(i, 1);
}

function toggleExpand(i) {
  results.value[i].expanded = !results.value[i].expanded;
}

async function loadProfiles() {
  try {
    profiles.value = (await axios.get("/api/profiles")).data;
  } catch {}
}

async function handleSubmit() {
  if (selectedFiles.value.length === 0 || !resolvedProfile.value) return;
  error.value = "";

  // Build results array
  results.value = selectedFiles.value.map((f, i) => ({
    filename: f.name,
    previewUrl: previewUrls.value[i],
    file: f,
    scanId: null,
    draft: {},
    status: "pending",
    error: "",
    expanded: false,
  }));

  step.value = "uploading";

  // Upload sequentially
  for (const r of results.value) {
    r.status = "uploading";
    try {
      const form = new FormData();
      form.append("file", r.file);
      form.append("profile_name", resolvedProfile.value);
      const res = await axios.post("/api/scans/upload", form);
      const scan = res.data;
      r.scanId = scan.id;
      r.draft = {
        profile_name: scan.profile_name,
        scan_date: scan.scan_date ?? "",
        weight: scan.weight ?? null,
        skeletal_muscle_mass: scan.skeletal_muscle_mass ?? null,
        body_fat_mass: scan.body_fat_mass ?? null,
        body_fat_percent: scan.body_fat_percent ?? null,
        total_body_water: scan.total_body_water ?? null,
        minerals: scan.minerals ?? null,
        bmi: scan.bmi ?? null,
        visceral_fat_level: scan.visceral_fat_level ?? null,
        waist_hip_ratio: scan.waist_hip_ratio ?? null,
        inbody_score: scan.inbody_score ?? null,
        height: scan.height ?? null,
        age: scan.age ?? null,
        gender: scan.gender ?? "",
      };
      r.status = "done";
    } catch (err) {
      r.status = "error";
      r.error = err.response?.data?.detail || err.message;
    }
  }

  step.value = "review";
}

async function saveAllAndGo() {
  saving.value = true;
  saveError.value = "";
  try {
    const successful = results.value.filter((r) => r.status === "done");
    await Promise.all(
      successful.map((r) => axios.patch(`/api/scans/${r.scanId}`, r.draft)),
    );
    const profile = resolvedProfile.value || successful[0]?.draft?.profile_name;
    router.push({ path: "/dashboard", query: { profile } });
  } catch (err) {
    saveError.value = err.response?.data?.detail || "Save failed.";
  } finally {
    saving.value = false;
  }
}

onMounted(loadProfiles);
</script>

<style scoped>
.upload-view {
  max-width: 820px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}
.page-title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.4px;
  margin-bottom: 4px;
}
.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

.success-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--good-dim);
  color: var(--good);
  border: 1px solid rgba(52, 199, 123, 0.25);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  align-self: flex-start;
}
.success-pill svg {
  width: 14px;
  height: 14px;
}

/* ── Upload card ── */
.upload-card {
  padding: 28px;
}

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 44px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  margin-bottom: 22px;
}
.drop-zone:hover,
.drop-zone--active {
  border-color: var(--accent);
  background: var(--accent-dim);
}
.drop-zone--filled {
  padding: 20px 24px;
  border-style: solid;
  border-color: var(--accent);
}

.drop-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.drop-icon svg {
  width: 40px;
  height: 40px;
  color: var(--text-muted);
}
.drop-main {
  font-size: 15px;
  color: var(--text-primary);
}
.drop-hint {
  font-size: 13px;
  color: var(--text-muted);
}

.drop-filled-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
}
.drop-filled-label svg {
  width: 20px;
  height: 20px;
}
.drop-change {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-muted);
}

/* File list */
.file-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 22px;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
}
.file-thumb-wrap {
  flex-shrink: 0;
}
.file-thumb {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border);
}
.file-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-size {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}
.file-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
  font-family: inherit;
}
.file-remove:hover {
  color: var(--danger);
  background: var(--danger-dim);
}

/* Profile row */
.form-group {
  margin-bottom: 18px;
}
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
}
.profile-row {
  display: flex;
  gap: 10px;
}
.profile-select {
  flex: 1;
}
.profile-new-input {
  flex: 1;
}
.profile-select.dimmed {
  color: var(--text-muted);
}

.alert {
  padding: 11px 15px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  margin-bottom: 16px;
}
.alert-error {
  background: var(--danger-dim);
  border: 1px solid rgba(240, 99, 112, 0.25);
  color: var(--danger);
}

.submit-btn {
  width: 100%;
  justify-content: center;
  padding: 12px;
  font-size: 15px;
}

/* ── Upload progress ── */
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-muted);
}
.progress-pct {
  font-weight: 600;
  color: var(--accent);
}
.progress-bar-track {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 24px;
}
.progress-bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.upload-status-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.upload-status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
}
.status-thumb {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border);
  flex-shrink: 0;
}
.status-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.status-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 12px;
  flex-shrink: 0;
}
.badge-wait  { background: var(--bg-base); color: var(--text-muted); border: 1px solid var(--border); }
.badge-active{ background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(0,201,160,0.25); }
.badge-done  { background: var(--good-dim); color: var(--good); border: 1px solid rgba(52,199,123,0.25); }
.badge-error { background: var(--danger-dim); color: var(--danger); border: 1px solid rgba(240,99,112,0.25); }

/* ── Batch review ── */
.scan-review-card {
  overflow: hidden;
}
.card--error {
  border-color: rgba(240, 99, 112, 0.3);
}

.scan-review-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
}
.scan-review-header:hover {
  background: var(--bg-elevated);
}
.review-thumb {
  width: 52px;
  height: 64px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  flex-shrink: 0;
}
.scan-review-meta {
  flex: 1;
  min-width: 0;
}
.scan-review-profile {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 2px;
}
.scan-review-date {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  margin-bottom: 6px;
}
.scan-review-err {
  font-size: 12px;
  color: var(--danger);
}
.scan-review-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.chip {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 2px 9px;
  border-radius: 20px;
  font-size: 11px;
  color: var(--text-muted);
}
.chip-score {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
.expand-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  flex-shrink: 0;
  transition: color 0.15s;
}
.expand-btn svg {
  width: 18px;
  height: 18px;
  transition: transform 0.2s;
  display: block;
}
.expand-btn.expanded svg {
  transform: rotate(180deg);
}

.scan-review-body {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border);
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
  padding-top: 16px;
}

.review-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 4px;
}

/* Spinners */
.spinner {
  width: 15px;
  height: 15px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
.spinner-sm {
  width: 10px;
  height: 10px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
