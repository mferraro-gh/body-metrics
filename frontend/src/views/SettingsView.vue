<template>
  <div class="settings-view">
    <div class="settings-header">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Manage your app configuration and data.</p>
    </div>

    <div class="settings-section card">
      <h2 class="section-title">Data</h2>

      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-name">Database location</div>
          <div class="setting-desc">
            <code>backend/data/body_metrics.db</code> — SQLite file storing all
            scan records.
          </div>
        </div>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-name">Image storage</div>
          <div class="setting-desc">
            <code>backend/data/</code> — All uploaded InBody PNG/JPG files.
          </div>
        </div>
      </div>
    </div>

    <!-- Appearance -->
    <div class="settings-section card">
      <h2 class="section-title">Appearance</h2>

      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-name">Accent color</div>
          <div class="setting-desc">
            Changes the highlight color used throughout the app — buttons, active states, charts, and badges.
          </div>
        </div>
        <div class="palette-picker">
          <button
            v-for="p in presets"
            :key="p.hex"
            class="swatch"
            :class="{ 'swatch--active': currentAccent === p.hex }"
            :style="{ background: p.hex }"
            :title="p.name"
            @click="pickAccent(p.hex)"
          ></button>
          <label class="swatch swatch--custom" title="Custom color">
            <input type="color" v-model="customColor" @input="pickAccent(customColor)" />
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
              <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
            </svg>
          </label>
          <button
            v-if="currentAccent !== '#00c9a0'"
            class="reset-accent"
            @click="pickAccent('#00c9a0')"
            title="Reset to default"
          >Reset</button>
        </div>
      </div>
    </div>

    <!-- Profile deletion -->
    <div class="danger-zone card">
      <div class="danger-zone-header">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
        <h2 class="section-title" style="margin-bottom: 0">Delete Profile</h2>
      </div>

      <div class="setting-row danger-row">
        <div class="setting-info">
          <div class="setting-name">Delete a profile</div>
          <div class="setting-desc">
            Permanently removes all scans and uploaded images for the selected
            profile. This cannot be undone.
          </div>
        </div>

        <div class="reset-action">
          <template v-if="!confirmingProfile">
            <div class="profile-delete-row">
              <select v-model="selectedDeleteProfile" class="profile-select-input">
                <option value="">— Select profile —</option>
                <option v-for="p in profiles" :key="p" :value="p">{{ p }}</option>
              </select>
              <button
                class="btn btn-danger"
                :disabled="!selectedDeleteProfile"
                @click="confirmingProfile = true"
              >
                Delete Profile
              </button>
            </div>
          </template>

          <template v-else-if="!profileDone">
            <div class="confirm-box">
              <p class="confirm-text">
                Delete <strong>{{ selectedDeleteProfile }}</strong>? All their
                scans and images will be permanently removed.
              </p>
              <div class="confirm-buttons">
                <button
                  class="btn btn-ghost"
                  @click="confirmingProfile = false"
                  :disabled="profileLoading"
                >
                  Cancel
                </button>
                <button
                  class="btn btn-danger"
                  @click="doDeleteProfile"
                  :disabled="profileLoading"
                >
                  <span v-if="profileLoading" class="spinner"></span>
                  {{ profileLoading ? "Deleting…" : "Yes, delete profile" }}
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="done-box">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Profile deleted.
            </div>
          </template>
        </div>
      </div>
    </div>

    <div class="danger-zone card">
      <div class="danger-zone-header">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <path
            d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
          />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <h2 class="section-title" style="margin-bottom: 0">Danger Zone</h2>
      </div>

      <div class="setting-row danger-row">
        <div class="setting-info">
          <div class="setting-name">Reset all data</div>
          <div class="setting-desc">
            Permanently deletes all scan records from the database and all
            uploaded images. This cannot be undone.
          </div>
        </div>

        <div class="reset-action">
          <template v-if="!confirming">
            <button class="btn btn-danger" @click="confirming = true">
              Reset Everything
            </button>
          </template>

          <template v-else-if="!done">
            <div class="confirm-box">
              <p class="confirm-text">
                Are you sure? All profiles, scans, and images will be gone.
              </p>
              <div class="confirm-buttons">
                <button
                  class="btn btn-ghost"
                  @click="confirming = false"
                  :disabled="loading"
                >
                  Cancel
                </button>
                <button
                  class="btn btn-danger"
                  @click="doReset"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner"></span>
                  {{ loading ? "Deleting…" : "Yes, delete everything" }}
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="done-box">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              All data has been cleared.
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { applyAccent } from "../utils/theme.js";

// ── Accent palette ─────────────────────────────────────────────────────────
const presets = [
  { hex: "#00c9a0", name: "Teal (default)" },
  { hex: "#58a6ff", name: "Blue" },
  { hex: "#a78bfa", name: "Purple" },
  { hex: "#f97316", name: "Orange" },
  { hex: "#f43f5e", name: "Rose" },
  { hex: "#facc15", name: "Yellow" },
  { hex: "#34d399", name: "Emerald" },
  { hex: "#e879f9", name: "Pink" },
]
const currentAccent = ref(localStorage.getItem("bm-accent") || "#00c9a0")
const customColor = ref(currentAccent.value)

function pickAccent(hex) {
  currentAccent.value = hex
  customColor.value = hex
  applyAccent(hex)
}

// ── Reset / delete ─────────────────────────────────────────────────────────
const confirming = ref(false);
const loading = ref(false);
const done = ref(false);

const profiles = ref([]);
const selectedDeleteProfile = ref("");
const confirmingProfile = ref(false);
const profileLoading = ref(false);
const profileDone = ref(false);

async function loadProfiles() {
  try {
    profiles.value = (await axios.get("/api/profiles")).data;
  } catch {}
}

async function doReset() {
  loading.value = true;
  try {
    await axios.delete("/api/reset");
    done.value = true;
    profiles.value = [];
  } catch (e) {
    alert("Reset failed: " + (e.response?.data?.detail || e.message));
  } finally {
    loading.value = false;
    confirming.value = false;
  }
}

async function doDeleteProfile() {
  profileLoading.value = true;
  try {
    await axios.delete(`/api/profiles/${encodeURIComponent(selectedDeleteProfile.value)}`);
    profileDone.value = true;
    profiles.value = profiles.value.filter((p) => p !== selectedDeleteProfile.value);
  } catch (e) {
    alert("Delete failed: " + (e.response?.data?.detail || e.message));
    confirmingProfile.value = false;
  } finally {
    profileLoading.value = false;
  }
}

onMounted(loadProfiles);
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.settings-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.page-title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.4px;
}
.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding: 18px 0;
  border-bottom: 1px solid var(--border);
}
.setting-row:first-of-type {
  padding-top: 4px;
}
.setting-row:last-of-type {
  border-bottom: none;
  padding-bottom: 4px;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.setting-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.setting-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}
.setting-desc code {
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--accent);
}

/* Danger zone */
.danger-zone {
  border-color: rgba(240, 99, 112, 0.25);
}
.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}
.danger-zone-header svg {
  width: 18px;
  height: 18px;
  color: var(--danger);
  flex-shrink: 0;
}

.danger-row {
  align-items: center;
  flex-wrap: wrap;
}

.reset-action {
  flex-shrink: 0;
}

.confirm-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--danger-dim);
  border: 1px solid rgba(240, 99, 112, 0.2);
  border-radius: var(--radius-sm);
  padding: 16px 18px;
  max-width: 380px;
}
.confirm-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}
.confirm-buttons {
  display: flex;
  gap: 8px;
}

.done-box {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--good);
  font-size: 14px;
  font-weight: 500;
}
.done-box svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Palette picker */
.palette-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
}
.swatch {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s, border-color 0.15s;
  flex-shrink: 0;
  outline: none;
}
.swatch:hover { transform: scale(1.15); }
.swatch--active { border-color: var(--text-primary); transform: scale(1.15); }
.swatch--custom {
  background: var(--bg-elevated);
  border: 2px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.swatch--custom input[type="color"] {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
  padding: 0;
  border: none;
}
.reset-accent {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-xs);
  padding: 4px 8px;
  cursor: pointer;
  font-family: inherit;
  transition: color 0.15s, border-color 0.15s;
}
.reset-accent:hover { color: var(--text-primary); border-color: var(--border-strong); }

.profile-delete-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.profile-select-input {
  min-width: 180px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(240, 99, 112, 0.3);
  border-top-color: var(--danger);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
