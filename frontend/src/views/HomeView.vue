<template>
  <div class="home-view">

    <!-- Hero -->
    <div class="hero">
      <div class="watermark-bg" aria-hidden="true">
        <span class="wm-word">BODY</span>
        <span class="wm-word">METRICS</span>
      </div>
      <div class="hero-content">
        <div class="hero-badge">Local · Offline · Private</div>
        <h1 class="hero-title">Your body composition,<br>tracked over time.</h1>
        <p class="hero-sub">
          Upload InBody PNG reports, extract all metrics automatically via OCR,
          and compare progress across profiles and time periods — no cloud, no account, no internet required.
        </p>
        <div class="hero-actions">
          <router-link to="/upload" class="btn btn-primary hero-cta">Upload your first scan</router-link>
          <router-link to="/dashboard" class="btn btn-ghost">Go to Dashboard</router-link>
        </div>
      </div>
    </div>

    <!-- How it works -->
    <section class="section">
      <h2 class="section-title">How it works</h2>
      <div class="steps-grid">
        <div class="step-card card" v-for="s in steps" :key="s.num">
          <div class="step-num">{{ s.num }}</div>
          <div class="step-icon">{{ s.icon }}</div>
          <div class="step-title">{{ s.title }}</div>
          <p class="step-desc">{{ s.desc }}</p>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="section">
      <h2 class="section-title">What you can do</h2>
      <div class="features-grid">
        <div class="feature-item" v-for="f in features" :key="f.title">
          <div class="feature-icon">{{ f.icon }}</div>
          <div>
            <div class="feature-title">{{ f.title }}</div>
            <div class="feature-desc">{{ f.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Metrics reference -->
    <section class="section">
      <h2 class="section-title">Metrics extracted automatically</h2>
      <div class="metrics-chips">
        <span class="metric-chip" v-for="m in metrics" :key="m">{{ m }}</span>
      </div>
    </section>

    <!-- Quick start CTA -->
    <div class="cta-bar card">
      <div>
        <div class="cta-title">Ready to start?</div>
        <div class="cta-sub">Drop an InBody image and have your metrics in under 30 seconds.</div>
      </div>
      <router-link to="/upload" class="btn btn-primary">Upload a scan</router-link>
    </div>

  </div>
</template>

<script setup>
const steps = [
  {
    num: "01",
    icon: "📤",
    title: "Upload a scan",
    desc: "Drag and drop one or more InBody PNG or JPG reports. You can upload multiple scans at once for the same profile.",
  },
  {
    num: "02",
    icon: "🔍",
    title: "Automatic OCR extraction",
    desc: "The app runs EasyOCR locally on your machine — no internet, no API key. All metrics are read directly from the image.",
  },
  {
    num: "03",
    icon: "✏️",
    title: "Review & correct",
    desc: "Check every extracted value before saving. Hover any metric card and click the pen icon to fix anything the OCR got wrong.",
  },
  {
    num: "04",
    icon: "📊",
    title: "Track your progress",
    desc: "View charts and history on the Dashboard, compare profiles side-by-side on the Compare page, and filter by date range.",
  },
]

const features = [
  { icon: "👤", title: "Multiple profiles",      desc: "Track different people in the same app. Each profile keeps its own scan history." },
  { icon: "📈", title: "Progress charts",        desc: "Line charts showing how your key metrics evolve over time, with toggleable metric overlays." },
  { icon: "⚖️", title: "Side-by-side compare",  desc: "Pick any two profiles and any scan from each to compare metrics and tendencies head to head." },
  { icon: "🔄", title: "Tendency analysis",      desc: "See the absolute and % change between scans — for every metric, for every profile." },
  { icon: "📅", title: "Date filtering",         desc: "Filter scan history to the last 30 days, 3 months, 6 months, 1 year, or a custom range." },
  { icon: "🎨", title: "Custom accent color",    desc: "Personalize the app's color theme from Settings. Dark and light mode also supported." },
  { icon: "🔒", title: "Fully local & private",  desc: "All data lives in a SQLite file on your machine. Nothing is ever sent to any server." },
  { icon: "🗑️", title: "Profile & data control", desc: "Delete individual profiles or reset all data at any time from the Settings page." },
]

const metrics = [
  "InBody Score", "Peso", "Masa Muscular", "Masa Grasa", "Grasa Corporal %",
  "Agua Corporal", "Minerales", "IMC", "Grasa Visceral", "Cintura-Cadera",
  "Altura", "Edad", "Género", "Fecha del scan",
]
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 56px;
  padding-bottom: 24px;
}

/* ── Hero ── */
.hero {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  overflow: hidden;
}

.watermark-bg {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  user-select: none;
}
.wm-word {
  font-size: clamp(64px, 14vw, 148px);
  font-weight: 900;
  letter-spacing: 0.12em;
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px var(--border);
  opacity: 0.3;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 20px;
  padding: 48px 24px;
  max-width: 680px;
}

.hero-badge {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  background: var(--accent-dim);
  border: 1px solid rgba(0,201,160,0.2);
  padding: 4px 14px;
  border-radius: 20px;
}

.hero-title {
  font-size: clamp(28px, 5vw, 42px);
  font-weight: 800;
  letter-spacing: -0.8px;
  line-height: 1.15;
  color: var(--text-primary);
}

.hero-sub {
  font-size: 15px;
  color: var(--text-muted);
  line-height: 1.65;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 4px;
}
.hero-cta {
  padding: 12px 28px;
  font-size: 15px;
}

/* ── Sections ── */
.section { display: flex; flex-direction: column; gap: 20px; }

/* ── Steps ── */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.step-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 24px;
}
.step-num {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--accent);
  opacity: 0.7;
}
.step-icon { font-size: 28px; }
.step-title { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.step-desc { font-size: 13px; color: var(--text-muted); line-height: 1.6; margin: 0; }

/* ── Features ── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px 22px;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.feature-icon { font-size: 20px; flex-shrink: 0; margin-top: 1px; }
.feature-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.feature-desc { font-size: 13px; color: var(--text-muted); line-height: 1.5; }

/* ── Metrics chips ── */
.metrics-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.metric-chip {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* ── CTA bar ── */
.cta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
  flex-wrap: wrap;
  border-color: var(--accent);
  background: var(--accent-dim);
}
.cta-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.cta-sub { font-size: 13px; color: var(--text-muted); }
</style>
