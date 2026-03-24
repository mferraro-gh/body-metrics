<template>
  <div class="metric-card" :class="status ? `metric-card--${status}` : 'metric-card--neutral'">
    <div class="metric-label">{{ label }}</div>
    <div class="metric-value">
      <span class="metric-number">{{ displayValue }}</span>
      <span v-if="unit" class="metric-unit">{{ unit }}</span>
    </div>
    <div class="metric-status">
      <span v-if="status" class="badge" :class="badgeClass">{{ statusLabel }}</span>
      <span v-else class="metric-spacer"></span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:  { type: String, required: true },
  value:  { type: [Number, String], default: null },
  unit:   { type: String, default: '' },
  status: { type: String, default: null },
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  if (typeof props.value === 'number') {
    return Number.isInteger(props.value) ? props.value : props.value.toFixed(1)
  }
  return props.value
})

const badgeClass = computed(() => ({
  'badge-good':    props.status === 'normal',
  'badge-bad':     props.status === 'high',
  'badge-warn':    props.status === 'low',
  'badge-neutral': !props.status,
}))

const statusLabel = computed(() => {
  if (props.status === 'normal') return 'Normal'
  if (props.status === 'high')   return 'Alto'
  if (props.status === 'low')    return 'Bajo'
  return ''
})
</script>

<style scoped>
.metric-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex; flex-direction: column; gap: 4px;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  position: relative; overflow: hidden;
}
.metric-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Colored top accent bar */
.metric-card--normal::before,
.metric-card--high::before,
.metric-card--low::before,
.metric-card--neutral::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card--normal::before  { background: var(--good); }
.metric-card--high::before    { background: var(--danger); }
.metric-card--low::before     { background: var(--warn); }
.metric-card--neutral::before { background: var(--border-strong); }

.metric-label {
  font-size: 11px; font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.7px;
  margin-top: 2px;
}
.metric-value {
  display: flex; align-items: baseline; gap: 5px;
  margin-top: 4px;
}
.metric-number {
  font-size: 28px; font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -1px; line-height: 1;
}
.metric-unit { font-size: 13px; color: var(--text-muted); font-weight: 400; }
.metric-status { margin-top: 6px; min-height: 20px; }
.metric-spacer { display: block; height: 20px; }
</style>
