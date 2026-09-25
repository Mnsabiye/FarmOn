<script setup>
import { ref, onActivated } from 'vue';
import { Loader2 } from 'lucide-vue-next';
import adminApi, { errorMessage } from '../../api/admin';
import PaginationBar from './PaginationBar.vue';
import { formatDateTime, formatFbu, ACTION_LABELS, ROLE_LABELS } from './format';

const entries = ref([]);
const pagination = ref(null);
const page = ref(1);
const isLoading = ref(false);
const error = ref('');

const load = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const res = await adminApi.getAuditLog({ page: page.value, per_page: 25 });
    entries.value = res.entries;
    pagination.value = res.pagination;
  } catch (e) {
    error.value = errorMessage(e, "Impossible de charger le journal. Avez-vous exécuté admin_setup.sql ?");
  } finally {
    isLoading.value = false;
  }
};

// Kept alive by the dashboard: refresh whenever the tab is shown so actions
// taken in other tabs appear immediately.
onActivated(load);

const changePage = (p) => { page.value = p; load(); };

const describe = (entry) => {
  const d = entry.details || {};
  switch (entry.action) {
    case 'user.role_changed':
      return `${d.username || entry.target_id} : ${ROLE_LABELS[d.from] || d.from} → ${ROLE_LABELS[d.to] || d.to}`;
    case 'user.suspended':
    case 'user.restored':
      return d.username || entry.target_id;
    case 'product.removed':
      return [d.name, d.reason && `Motif : ${d.reason}`].filter(Boolean).join(' · ');
    case 'market_price.created':
    case 'market_price.deleted':
      return `${d.crop_name} · ${d.market_location} · ${formatFbu(d.price)}`;
    default:
      return '';
  }
};
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
    <div v-if="error" class="bg-red-50 text-red-700 p-4">{{ error }}</div>
    <div class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left text-gray-500 uppercase text-xs tracking-wide">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Administrateur</th>
            <th class="px-4 py-3 font-medium">Action</th>
            <th class="px-4 py-3 font-medium">Détails</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="isLoading && !entries.length">
            <td colspan="4" class="px-4 py-10 text-center"><Loader2 class="w-6 h-6 animate-spin text-primary-600 inline" /></td>
          </tr>
          <tr v-else-if="!entries.length && !error">
            <td colspan="4" class="px-4 py-10 text-center text-gray-500">Aucune action enregistrée.</td>
          </tr>
          <tr v-for="e in entries" :key="e.id">
            <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ formatDateTime(e.created_at) }}</td>
            <td class="px-4 py-3 text-gray-900">{{ e.admin_name || '—' }}</td>
            <td class="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{{ ACTION_LABELS[e.action] || e.action }}</td>
            <td class="px-4 py-3 text-gray-600">{{ describe(e) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <PaginationBar :pagination="pagination" @change="changePage" />
  </div>
</template>
