export function hexToRgb(hex) {
  const h = hex.replace('#', '')
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  }
}

export function applyAccent(hex) {
  const { r, g, b } = hexToRgb(hex)
  const brighter = `#${[r, g, b]
    .map((c) => Math.min(255, c + 28).toString(16).padStart(2, '0'))
    .join('')}`
  const el = document.documentElement
  el.style.setProperty('--accent',       hex)
  el.style.setProperty('--accent-dim',   `rgba(${r},${g},${b},0.12)`)
  el.style.setProperty('--accent-hover', brighter)
  localStorage.setItem('bm-accent', hex)
}

export function loadSavedAccent() {
  const saved = localStorage.getItem('bm-accent')
  if (saved) applyAccent(saved)
  return saved || null
}
