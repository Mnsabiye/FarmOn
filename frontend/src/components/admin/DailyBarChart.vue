<script setup>
import { computed, ref } from 'vue';
import { formatDate } from './format';

// Single-series daily column chart (e.g. sign-ups per day).
const props = defineProps({
  title: { type: String, required: true },
  series: { type: Array, required: true }, // [{ date, count }]
  unit: { type: String, default: '' }
});

const WIDTH = 600;
const HEIGHT = 160;
const PAD = { top: 12, right: 8, bottom: 22, left: 28 };
const plotW = WIDTH - PAD.left - PAD.right;
const plotH = HEIGHT - PAD.top - PAD.bottom;

const hovered = ref(null);

const niceMax = computed(() => {
  const max = Math.max(1, ...props.series.map(d => d.count));
  if (max <= 5) return max;
  const step = Math.pow(10, Math.floor(Math.log10(max)));
  return Math.ceil(max / step) * step;
});

const ticks = computed(() => {
  const max = niceMax.value;
  return max <= 4 ? Array.from({ length: max + 1 }, (_, i) => i) : [0, max / 2, max].map(Math.round);
});

const band = computed(() => plotW / Math.max(props.series.length, 1));
const barW = computed(() => Math.min(24, Math.max(band.value - 2, 1)));

const bars = computed(() => props.series.map((d, i) => {
  const h = (d.count / niceMax.value) * plotH;
  return {
    ...d,
    x: PAD.left + i * band.value + (band.value - barW.value) / 2,
    y: PAD.top + plotH - h,
    h,
    hitX: PAD.left + i * band.value
  };
}));

const yFor = (v) => PAD.top + plotH - (v / niceMax.value) * plotH;

// Column path with a 4px rounded top and a square baseline
const barPath = (b) => {
  if (b.h <= 0) return '';
  const r = Math.min(4, b.h, barW.value / 2);
  const x = b.x, y = b.y, w = barW.value, base = y + b.h;
  return `M${x},${base} V${y + r} Q${x},${y} ${x + r},${y} H${x + w - r} Q${x + w},${y} ${x + w},${y + r} V${base} Z`;
};

const total = computed(() => props.series.reduce((s, d) => s + d.count, 0));
const firstLabel = computed(() => props.series[0] && formatDate(props.series[0].date));
const lastLabel = computed(() => props.series.length && formatDate(props.series[props.series.length - 1].date));
</script>

<template>
  <figure class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
    <figcaption class="flex items-baseline justify-between mb-3">
      <span class="font-semibold text-gray-900">{{ title }}</span>
      <span class="text-sm text-gray-500 tabular-nums">{{ total }} {{ unit }} · 30 j</span>
    </figcaption>

    <div class="relative">
      <svg :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" class="w-full h-auto" role="img" :aria-label="`${title} : ${total} ${unit} sur 30 jours`">
        <g v-for="t in ticks" :key="t">
          <line :x1="PAD.left" :x2="WIDTH - PAD.right" :y1="yFor(t)" :y2="yFor(t)" stroke="#e5e7eb" stroke-width="1" />
          <text :x="PAD.left - 6" :y="yFor(t)" text-anchor="end" dominant-baseline="middle" class="fill-gray-400" font-size="10">{{ t }}</text>
        </g>

        <path v-for="b in bars" :key="b.date" :d="barPath(b)" fill="#059669" :opacity="hovered && hovered.date !== b.date ? 0.45 : 1" />

        <!-- Hit targets span the full band so thin bars are easy to hover -->
        <rect
          v-for="b in bars"
          :key="`hit-${b.date}`"
          :x="b.hitX"
          :y="PAD.top"
          :width="band"
          :height="plotH"
          fill="transparent"
          @mouseenter="hovered = b"
          @mouseleave="hovered = null"
        />

        <text :x="PAD.left" :y="HEIGHT - 4" class="fill-gray-400" font-size="10">{{ firstLabel }}</text>
        <text :x="WIDTH - PAD.right" :y="HEIGHT - 4" text-anchor="end" class="fill-gray-400" font-size="10">{{ lastLabel }}</text>
      </svg>

      <div
        v-if="hovered"
        class="absolute pointer-events-none bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap -translate-x-1/2 -translate-y-full"
        :style="{ left: `${((hovered.x + barW / 2) / WIDTH) * 100}%`, top: `${(hovered.y / HEIGHT) * 100}%` }"
      >
        {{ formatDate(hovered.date) }} · <strong>{{ hovered.count }}</strong> {{ unit }}
      </div>
    </div>
  </figure>
</template>
