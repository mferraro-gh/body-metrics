<template>
  <div class="metric-card" :class="statusClass" @mouseenter="hovered = true" @mouseleave="hovered = false">
    <!-- Edit button -->
    <button v-show="hovered && !editing" class="edit-btn" @click.stop="startEdit" title="Edit value">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    </button>

    <div class="metric-label">{{ label }}</div>

    <!-- Display mode -->
    <div v-if="!editing" class="metric-value">
      <span class="metric-number">{{ displayValue }}</span>
      <span v-if="unit" class="metric-unit">{{ unit }}</span>
    </div>

    <!-- Edit mode -->
    <div v-else class="edit-mode">
      <div class="edit-row">
        <select v-if="fieldType === 'select'" v-model="editVal" class="edit-input" ref="inputEl">
          <option value="">Unknown</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
        </select>
        <input
          v-else
          ref="inputEl"
          :type="fieldType === 'number' ? 'number' : 'text'"
          :step="step"
          v-model="editVal"
          class="edit-input"
          @keydown.enter="confirm"
          @keydown.esc="cancel"
        />
        <span v-if="unit" class="edit-unit">{{ unit }}</span>
      </div>
      <div class="edit-actions">
        <button class="action-btn action-ok"     @click="confirm">✓</button>
        <button class="action-btn action-cancel" @click="cancel">✕</button>
      </div>
    </div>

    <div class="metric-status">
      <span v-if="status" class="badge" :class="badgeClass">{{ statusLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  label:     { type: String,           required: true },
  value:     { type: [Number, String], default: null },
  unit:      { type: String,           default: '' },
  status:    { type: String,           default: null },
  fieldType: { type: String,           default: 'number' }, // 'number' | 'text' | 'date' | 'select'
  step:      { type: String,           default: 'any' },
})

const emit = defineEmits(['update'])

const hovered  = ref(false)
const editing  = ref(false)
const editVal  = ref('')
const inputEl  = ref(null)

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') return '—'
  if (typeof props.value === 'number') {
    return Number.isInteger(props.value) ? props.value : props.value.toFixed(1)
  }
  return props.value
})

const statusClass = computed(() => {
  const s = props.status
  return s ? `metric-card--${s}` : 'metric-card--neutral'
})

const badgeClass = computed(() => ({
  'badge-good':    props.status === 'normal',
  'badge-bad':     props.status === 'high',
  'badge-warn':    props.status === 'low',
}))

const statusLabel = computed(() => {
  if (props.status === 'normal') return 'Normal'
  if (props.status === 'high')   return 'Alto'
  if (props.status === 'low')    return 'Bajo'
  return ''
})

async function startEdit() {
  editVal.value = props.value ?? ''
  editing.value = true
  await nextTick()
  inputEl.value?.focus()
  inputEl.value?.select?.()
}

function confirm() {
  const raw = editVal.value
  const num = parseFloat(String(raw).replace(',', '.'))
  const out = props.fieldType === 'number'
    ? (isNaN(num) ? null : num)
    : (raw === '' ? null : raw)
  emit('update', out)
  editing.value = false
}

function cancel() {
  editing.value = false
}
</script>

<style scoped>
.metric-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex; flex-direction: column; gap: 4px;
  position: relative; overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }

.metric-card--normal::before,
.metric-card--high::before,
.metric-card--low::before,
.metric-card--neutral::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card--normal::before  { background: var(--good); }
.metric-card--high::before    { background: var(--danger); }
.metric-card--low::before     { background: var(--warn); }
.metric-card--neutral::before { background: var(--border-strong); }

/* Pen button */
.edit-btn {
  position: absolute; top: 10px; right: 10px;
  width: 26px; height: 26px; border-radius: var(--radius-xs);
  background: var(--bg-hover); border: 1px solid var(--border);
  color: var(--text-muted); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; z-index: 1;
}
.edit-btn:hover { background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }
.edit-btn svg  { width: 12px; height: 12px; }

.metric-label {
  font-size: 11px; font-weight: 600; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.7px; margin-top: 2px;
}
.metric-value { display: flex; align-items: baseline; gap: 5px; margin-top: 4px; }
.metric-number {
  font-size: 28px; font-weight: 700; color: var(--text-primary);
  letter-spacing: -1px; line-height: 1;
}
.metric-unit { font-size: 13px; color: var(--text-muted); }

/* Edit mode */
.edit-mode  { display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }
.edit-row   { display: flex; align-items: center; gap: 5px; }
.edit-input {
  flex: 1; min-width: 0;
  padding: 5px 8px; font-size: 15px; font-weight: 600;
  border-radius: var(--radius-xs);
}
.edit-unit  { font-size: 12px; color: var(--text-muted); white-space: nowrap; }
.edit-actions { display: flex; gap: 4px; }
.action-btn {
  padding: 2px 8px; border-radius: var(--radius-xs);
  font-size: 12px; cursor: pointer; border: 1px solid;
  font-family: inherit; transition: all 0.12s;
}
.action-ok     { background: var(--good-dim); color: var(--good); border-color: rgba(52,199,123,.25); }
.action-ok:hover { background: rgba(52,199,123,.2); }
.action-cancel { background: var(--bg-hover); color: var(--text-muted); border-color: var(--border); }

.metric-status { margin-top: 6px; min-height: 20px; }
</style>
