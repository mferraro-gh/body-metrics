<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <router-link to="/" class="brand">
          <svg
            class="brand-logo"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="5.5" r="2.5" fill="currentColor" />
            <path
              d="M7.5 10.5Q12 8.5 16.5 10.5L15 21H9L7.5 10.5Z"
              fill="currentColor"
            />
            <path
              d="M9 21L7.5 25M15 21L16.5 25"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
          <span class="brand-name"
            >Body<span class="brand-accent">Metrics</span></span
          >
        </router-link>

        <nav class="nav">
          <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/upload" class="nav-link">Upload</router-link>
          <router-link to="/compare" class="nav-link">Compare</router-link>
          <router-link to="/settings" class="nav-link">Settings</router-link>
        </nav>

        <button
          class="theme-toggle"
          @click="toggleTheme"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <svg
            v-if="isDark"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <circle cx="12" cy="12" r="4" />
            <path
              d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
            />
          </svg>
          <svg
            v-else
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        </button>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { loadSavedAccent } from "./utils/theme.js";

const isDark = ref(true);

function applyTheme(dark) {
  document.documentElement.classList.toggle("light", !dark);
  localStorage.setItem("bm-theme", dark ? "dark" : "light");
}

function toggleTheme() {
  isDark.value = !isDark.value;
  applyTheme(isDark.value);
}

onMounted(() => {
  const savedTheme = localStorage.getItem("bm-theme");
  isDark.value = savedTheme !== "light";
  applyTheme(isDark.value);
  loadSavedAccent();
});
</script>

<style>
/* ── Reset ── */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
a {
  text-decoration: none;
}

/* ── Dark theme (default) ── */
:root {
  --bg-base: #070d1a;
  --bg-surface: #0e1525;
  --bg-elevated: #161f33;
  --bg-hover: #1c2840;
  --border: #243049;
  --border-strong: #2e3d5a;
  --text-primary: #e8edf5;
  --text-secondary: #a8b4c8;
  --text-muted: #6b7a96;
  --accent: #00c9a0;
  --accent-dim: rgba(0, 201, 160, 0.1);
  --accent-hover: #00ddb0;
  --danger: #f06370;
  --danger-dim: rgba(240, 99, 112, 0.1);
  --warn: #e0a832;
  --warn-dim: rgba(224, 168, 50, 0.1);
  --good: #34c77b;
  --good-dim: rgba(52, 199, 123, 0.1);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
  --radius: 12px;
  --radius-sm: 8px;
  --radius-xs: 5px;
  font-family: "Inter", system-ui, sans-serif;
  color-scheme: dark;
}

/* ── Light theme ── */
:root.light {
  --bg-base: #f0f4fb;
  --bg-surface: #ffffff;
  --bg-elevated: #f5f7fc;
  --bg-hover: #eaeef7;
  --border: #dce3f0;
  --border-strong: #c4cfe4;
  --text-primary: #0f1623;
  --text-secondary: #3d4f6e;
  --text-muted: #7585a2;
  --accent: #0099a0;
  --accent-dim: rgba(0, 153, 160, 0.08);
  --accent-hover: #00b5be;
  --danger: #d93b4a;
  --danger-dim: rgba(217, 59, 74, 0.08);
  --warn: #b87a00;
  --warn-dim: rgba(184, 122, 0, 0.08);
  --good: #1e9e55;
  --good-dim: rgba(30, 158, 85, 0.08);
  --shadow-sm: 0 1px 3px rgba(15, 22, 35, 0.08);
  --shadow-md: 0 4px 16px rgba(15, 22, 35, 0.1);
  color-scheme: light;
}

html,
body {
  height: 100%;
  background: var(--bg-base);
  color: var(--text-primary);
}

/* ── App shell ── */
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Topbar ── */
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.topbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 28px;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* ── Brand ── */
.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-logo {
  width: 26px;
  height: 26px;
  color: var(--accent);
}
.brand-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.4px;
  color: var(--text-primary);
}
.brand-accent {
  color: var(--accent);
}

/* ── Nav ── */
.nav {
  display: flex;
  gap: 2px;
}
.nav-link {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition:
    color 0.15s,
    background 0.15s;
  white-space: nowrap;
}
.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}
.nav-link.router-link-active {
  color: var(--accent);
  background: var(--accent-dim);
  font-weight: 600;
}

/* ── Theme toggle ── */
.theme-toggle {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}
.theme-toggle:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-strong);
}
.theme-toggle svg {
  width: 16px;
  height: 16px;
}

/* ── Main content ── */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 36px 28px;
}

/* ── Shared cards ── */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: var(--shadow-sm);
}

/* ── Section titles ── */
.section-title {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 18px;
  color: var(--text-primary);
  letter-spacing: -0.2px;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}
.badge-good {
  background: var(--good-dim);
  color: var(--good);
}
.badge-warn {
  background: var(--warn-dim);
  color: var(--warn);
}
.badge-bad {
  background: var(--danger-dim);
  color: var(--danger);
}
.badge-neutral {
  background: var(--bg-elevated);
  color: var(--text-muted);
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
  white-space: nowrap;
  font-family: inherit;
  text-decoration: none;
}
.btn-primary {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 1px 4px rgba(0, 201, 160, 0.3);
}
.btn-primary:hover {
  background: var(--accent-hover);
}
.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}
.btn-ghost:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-strong);
}
.btn-danger {
  background: var(--danger-dim);
  color: var(--danger);
  border: 1px solid rgba(240, 99, 112, 0.2);
}
.btn-danger:hover {
  background: rgba(240, 99, 112, 0.18);
}

/* ── Inputs ── */
input,
select,
textarea {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 9px 13px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}
input:focus,
select:focus,
textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
input::placeholder,
textarea::placeholder {
  color: var(--text-muted);
}
</style>
