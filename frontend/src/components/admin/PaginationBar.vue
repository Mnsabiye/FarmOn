<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = defineProps({
  pagination: { type: Object, default: null }
});
const emit = defineEmits(['change']);

const go = (page) => {
  if (!props.pagination) return;
  if (page < 1 || page > props.pagination.pages) return;
  emit('change', page);
};
</script>

<template>
  <div v-if="pagination && pagination.total > 0" class="flex items-center justify-between px-4 py-3 border-t border-gray-100 text-sm text-gray-600">
    <span>
      {{ (pagination.page - 1) * pagination.per_page + 1 }}–{{ Math.min(pagination.page * pagination.per_page, pagination.total) }}
      sur {{ pagination.total }}
    </span>
    <div class="flex items-center gap-2">
      <button
        class="p-1.5 rounded-md border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="pagination.page <= 1"
        aria-label="Page précédente"
        @click="go(pagination.page - 1)"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <span class="tabular-nums">{{ pagination.page }} / {{ pagination.pages }}</span>
      <button
        class="p-1.5 rounded-md border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="pagination.page >= pagination.pages"
        aria-label="Page suivante"
        @click="go(pagination.page + 1)"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
