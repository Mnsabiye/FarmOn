<script setup>
import { ref, watch } from 'vue';
import { Loader2 } from 'lucide-vue-next';

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, required: true },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirmer' },
  danger: { type: Boolean, default: false },
  withReason: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
  error: { type: String, default: '' }
});
const emit = defineEmits(['confirm', 'cancel']);

const reason = ref('');
watch(() => props.open, (open) => { if (open) reason.value = ''; });
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    @click.self="!busy && emit('cancel')"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
      <p v-if="message" class="text-sm text-gray-600 mb-4">{{ message }}</p>

      <label v-if="withReason" class="block mb-4">
        <span class="text-sm font-medium text-gray-700">Motif (facultatif)</span>
        <textarea
          v-model="reason"
          rows="2"
          maxlength="500"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </label>

      <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>

      <div class="flex justify-end gap-3">
        <button
          class="px-4 py-2 rounded-md text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200"
          :disabled="busy"
          @click="emit('cancel')"
        >
          Annuler
        </button>
        <button
          class="px-4 py-2 rounded-md text-sm font-medium text-white flex items-center gap-2 disabled:opacity-60"
          :class="danger ? 'bg-red-600 hover:bg-red-700' : 'bg-primary-600 hover:bg-primary-700'"
          :disabled="busy"
          @click="emit('confirm', reason)"
        >
          <Loader2 v-if="busy" class="w-4 h-4 animate-spin" />
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>
