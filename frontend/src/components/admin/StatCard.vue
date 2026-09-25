<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  hint: { type: String, default: '' },
  icon: { type: [Object, Function], default: null }
});
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
    <div class="flex items-center justify-between mb-2">
      <span class="text-sm font-medium text-gray-500">{{ label }}</span>
      <component :is="icon" v-if="icon" class="w-5 h-5 text-primary-600" aria-hidden="true" />
    </div>
    <div class="text-2xl font-bold text-gray-900 tabular-nums">{{ value }}</div>
    <div v-if="hint" class="text-xs text-gray-500 mt-1">{{ hint }}</div>
  </div>
</template>
