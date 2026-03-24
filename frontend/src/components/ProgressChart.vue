<template>
  <div class="chart-wrapper">
    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
    <div v-else class="chart-empty">Not enough data to display a chart.</div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

const props = defineProps({
  // Array of scan objects sorted oldest→newest
  scans: { type: Array, required: true },
  // Array of metric keys to plot, e.g. ['weight','body_fat_percent']
  metrics: {
    type: Array,
    default: () => ["weight", "skeletal_muscle_mass", "body_fat_percent"],
  },
});

const METRIC_META = {
  weight: { label: "Peso (kg)", color: "#00c9a0" },
  skeletal_muscle_mass: { label: "Masa Muscular (kg)", color: "#58a6ff" },
  body_fat_mass: { label: "Masa Grasa (kg)", color: "#f85149" },
  body_fat_percent: { label: "Grasa Corporal (%)", color: "#ffa657" },
  bmi: { label: "IMC", color: "#d2a8ff" },
  total_body_water: { label: "Agua Corporal (L)", color: "#79c0ff" },
  inbody_score: { label: "InBody Score", color: "#3fb950" },
  visceral_fat_level: { label: "Grasa Visceral", color: "#ff7b72" },
};

const labels = computed(() =>
  props.scans.map((s) => s.scan_date || `Scan ${s.id}`),
);

const chartData = computed(() => {
  if (props.scans.length < 1) return null;
  return {
    labels: labels.value,
    datasets: props.metrics.map((key) => {
      const meta = METRIC_META[key] || { label: key, color: "#8b949e" };
      return {
        label: meta.label,
        data: props.scans.map((s) => s[key] ?? null),
        borderColor: meta.color,
        backgroundColor: meta.color + "22",
        pointBackgroundColor: meta.color,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.35,
        fill: false,
        spanGaps: true,
      };
    }),
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index", intersect: false },
  plugins: {
    legend: {
      labels: { color: "#8b949e", font: { size: 12 }, padding: 16 },
    },
    tooltip: {
      backgroundColor: "#1c2230",
      borderColor: "#30363d",
      borderWidth: 1,
      titleColor: "#e6edf3",
      bodyColor: "#8b949e",
    },
  },
  scales: {
    x: {
      ticks: { color: "#8b949e", font: { size: 11 } },
      grid: { color: "#30363d" },
    },
    y: {
      ticks: { color: "#8b949e", font: { size: 11 } },
      grid: { color: "#30363d" },
    },
  },
};
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  height: 320px;
  width: 100%;
}
.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
  font-size: 14px;
}
</style>
