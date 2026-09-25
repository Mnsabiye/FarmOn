<script setup>
import { ref, computed, onMounted } from 'vue';
import { Users, Package, Coins, MessageCircle, Loader2, RefreshCw } from 'lucide-vue-next';
import adminApi, { errorMessage } from '../../api/admin';
import StatCard from './StatCard.vue';
import DailyBarChart from './DailyBarChart.vue';
import { formatNumber, formatFbu, formatDate, ROLE_LABELS, ROLE_BADGES } from './format';

const emit = defineEmits(['navigate']);

const data = ref(null);
const isLoading = ref(false);
const error = ref('');

const load = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    data.value = await adminApi.getOverview();
  } catch (e) {
    error.value = errorMessage(e, 'Impossible de charger les statistiques');
  } finally {
    isLoading.value = false;
  }
};

onMounted(load);

const maxCategory = computed(() =>
  Math.max(1, ...(data.value?.products.by_category || []).map(c => c.count))
);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p v-if="data" class="text-sm text-gray-500">Mis à jour {{ formatDate(data.generated_at) }}</p>
      <span v-else />
      <button
        class="flex items-center gap-1.5 text-sm font-medium text-primary-700 hover:text-primary-800 disabled:opacity-50"
        :disabled="isLoading"
        @click="load"
      >
        <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
        Actualiser
      </button>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 border border-red-200 rounded-md p-4 mb-6">{{ error }}</div>

    <div v-if="isLoading && !data" class="flex justify-center py-16">
      <Loader2 class="w-8 h-8 animate-spin text-primary-600" />
    </div>

    <template v-if="data">
      <!-- Headline numbers -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Utilisateurs"
          :value="formatNumber(data.users.total)"
          :hint="`+${data.users.new_7d} cette semaine`"
          :icon="Users"
        />
        <StatCard
          label="Annonces"
          :value="formatNumber(data.products.total)"
          :hint="`${data.products.out_of_stock} en rupture de stock`"
          :icon="Package"
        />
        <StatCard
          label="Valeur du stock"
          :value="formatFbu(data.products.stock_value)"
          :hint="`${formatNumber(data.products.stock_kg)} kg disponibles`"
          :icon="Coins"
        />
        <StatCard
          label="Questions à l'assistant"
          :value="formatNumber(data.chatbot.questions_7d)"
          :hint="`${formatNumber(data.chatbot.questions_30d)} sur 30 jours`"
          :icon="MessageCircle"
        />
      </div>

      <!-- Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <DailyBarChart title="Nouvelles inscriptions" unit="inscriptions" :series="data.timeseries.signups" />
        <DailyBarChart title="Nouvelles annonces" unit="annonces" :series="data.timeseries.listings" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Users by role -->
        <section class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold text-gray-900 mb-4">Utilisateurs par rôle</h3>
          <ul class="space-y-3">
            <li v-for="(count, role) in data.users.by_role" :key="role" class="flex items-center justify-between">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="ROLE_BADGES[role]">{{ ROLE_LABELS[role] }}</span>
              <span class="font-semibold text-gray-900 tabular-nums">{{ formatNumber(count) }}</span>
            </li>
          </ul>
          <p class="text-xs text-gray-500 mt-4">+{{ data.users.new_30d }} inscriptions sur 30 jours</p>
        </section>

        <!-- Listings by category -->
        <section class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold text-gray-900 mb-4">Annonces par catégorie</h3>
          <p v-if="!data.products.by_category.length" class="text-sm text-gray-500">Aucune annonce.</p>
          <ul class="space-y-3">
            <li v-for="c in data.products.by_category" :key="c.category">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-700">{{ c.category }}</span>
                <span class="font-medium text-gray-900 tabular-nums">{{ c.count }}</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full">
                <div class="h-2 bg-primary-600 rounded-full" :style="{ width: `${(c.count / maxCategory) * 100}%` }" />
              </div>
            </li>
          </ul>
        </section>

        <!-- Recent activity -->
        <section class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-900">Dernières annonces</h3>
            <button class="text-sm text-primary-700 hover:underline" @click="emit('navigate', 'products')">Tout voir</button>
          </div>
          <p v-if="!data.recent_products.length" class="text-sm text-gray-500">Aucune annonce.</p>
          <ul class="divide-y divide-gray-100">
            <li v-for="p in data.recent_products" :key="p.id" class="py-2 flex justify-between gap-2 text-sm">
              <div class="min-w-0">
                <div class="font-medium text-gray-900 truncate">{{ p.name }}</div>
                <div class="text-gray-500 truncate">{{ p.farmer_name || '—' }} · {{ formatDate(p.created_at) }}</div>
              </div>
              <span class="text-gray-700 whitespace-nowrap tabular-nums">{{ formatFbu(p.price_per_kg) }}/kg</span>
            </li>
          </ul>

          <div class="flex items-center justify-between mt-5 mb-2">
            <h3 class="font-semibold text-gray-900">Nouveaux membres</h3>
            <button class="text-sm text-primary-700 hover:underline" @click="emit('navigate', 'users')">Tout voir</button>
          </div>
          <ul class="divide-y divide-gray-100">
            <li v-for="u in data.recent_users" :key="u.id" class="py-2 flex justify-between gap-2 text-sm">
              <span class="font-medium text-gray-900 truncate">{{ u.username }}</span>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap" :class="ROLE_BADGES[u.role]">{{ ROLE_LABELS[u.role] }}</span>
            </li>
          </ul>
        </section>
      </div>
    </template>
  </div>
</template>
