<script setup>
import { ref, reactive, watch, onMounted } from 'vue';
import { Search, Loader2, Trash2, Package } from 'lucide-vue-next';
import adminApi, { errorMessage } from '../../api/admin';
import PaginationBar from './PaginationBar.vue';
import ConfirmDialog from './ConfirmDialog.vue';
import { formatDate, formatFbu, formatNumber, CATEGORIES } from './format';

const filters = reactive({ q: '', category: '', stock: '', page: 1 });
const products = ref([]);
const pagination = ref(null);
const isLoading = ref(false);
const error = ref('');
const notice = ref('');

const pendingRemoval = ref(null);
const isBusy = ref(false);
const actionError = ref('');

const load = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const params = { page: filters.page, per_page: 20 };
    if (filters.q) params.q = filters.q;
    if (filters.category) params.category = filters.category;
    if (filters.stock) params.stock = filters.stock;
    const res = await adminApi.getProducts(params);
    products.value = res.products;
    pagination.value = res.pagination;
  } catch (e) {
    error.value = errorMessage(e, 'Impossible de charger les annonces');
  } finally {
    isLoading.value = false;
  }
};

let searchTimer;
watch(() => filters.q, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { filters.page = 1; load(); }, 300);
});
watch(() => [filters.category, filters.stock], () => { filters.page = 1; load(); });

onMounted(load);

const changePage = (page) => { filters.page = page; load(); };

const confirmRemoval = async (reason) => {
  const product = pendingRemoval.value;
  isBusy.value = true;
  actionError.value = '';
  try {
    await adminApi.removeProduct(product.id, reason);
    notice.value = `« ${product.name} » a été supprimée.`;
    pendingRemoval.value = null;
    // Step back a page if we just emptied the last one
    if (products.value.length === 1 && filters.page > 1) filters.page -= 1;
    await load();
  } catch (e) {
    actionError.value = errorMessage(e);
  } finally {
    isBusy.value = false;
  }
};
</script>

<template>
  <div>
    <div class="flex flex-col md:flex-row gap-3 mb-4">
      <label class="relative flex-grow">
        <span class="sr-only">Rechercher</span>
        <Search class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          v-model.trim="filters.q"
          type="search"
          placeholder="Nom du produit"
          class="w-full pl-9 pr-3 py-2 rounded-md border border-gray-300 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </label>
      <select v-model="filters.category" class="rounded-md border border-gray-300 text-sm px-3 py-2" aria-label="Catégorie">
        <option value="">Toutes les catégories</option>
        <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filters.stock" class="rounded-md border border-gray-300 text-sm px-3 py-2" aria-label="Stock">
        <option value="">Tout le stock</option>
        <option value="in">En stock</option>
        <option value="out">En rupture</option>
      </select>
    </div>

    <div v-if="notice" class="bg-primary-50 text-primary-800 border border-primary-200 rounded-md px-4 py-2 mb-4 text-sm flex justify-between">
      {{ notice }}
      <button class="text-primary-700 hover:underline" @click="notice = ''">OK</button>
    </div>
    <div v-if="error" class="bg-red-50 text-red-700 border border-red-200 rounded-md p-4 mb-4">{{ error }}</div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-left text-gray-500 uppercase text-xs tracking-wide">
            <tr>
              <th class="px-4 py-3 font-medium">Produit</th>
              <th class="px-4 py-3 font-medium hidden sm:table-cell">Agriculteur</th>
              <th class="px-4 py-3 font-medium text-right">Prix / kg</th>
              <th class="px-4 py-3 font-medium text-right">Stock</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">Publiée le</th>
              <th class="px-4 py-3 font-medium text-right"><span class="sr-only sm:not-sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="isLoading && !products.length">
              <td colspan="6" class="px-4 py-10 text-center"><Loader2 class="w-6 h-6 animate-spin text-primary-600 inline" /></td>
            </tr>
            <tr v-else-if="!products.length">
              <td colspan="6" class="px-4 py-10 text-center text-gray-500">Aucune annonce trouvée.</td>
            </tr>
            <tr v-for="p in products" :key="p.id" :class="{ 'opacity-60': isLoading }">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <img v-if="p.image_url" :src="p.image_url" :alt="p.name" class="hidden sm:block w-10 h-10 rounded object-cover flex-shrink-0" />
                  <div v-else class="hidden sm:flex w-10 h-10 rounded bg-gray-100 items-center justify-center flex-shrink-0">
                    <Package class="w-5 h-5 text-gray-400" />
                  </div>
                  <div class="min-w-0">
                    <div class="font-medium text-gray-900">{{ p.name }}</div>
                    <div class="text-gray-500 text-xs">{{ p.category }}</div>
                    <div class="text-gray-500 text-xs sm:hidden">{{ p.farmer_name || '—' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <div class="text-gray-900">{{ p.farmer_name || '—' }}</div>
                <div class="text-gray-500 text-xs">{{ p.farmer_location || p.farmer_email || '' }}</div>
              </td>
              <td class="px-4 py-3 text-right tabular-nums whitespace-nowrap">{{ formatFbu(p.price_per_kg) }}</td>
              <td class="px-4 py-3 text-right tabular-nums whitespace-nowrap">
                <span v-if="Number(p.quantity_available) > 0">{{ formatNumber(p.quantity_available) }} kg</span>
                <span v-else class="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">Rupture</span>
              </td>
              <td class="px-4 py-3 text-gray-600 hidden md:table-cell whitespace-nowrap">{{ formatDate(p.created_at) }}</td>
              <td class="px-4 py-3 text-right">
                <button
                  class="inline-flex items-center gap-1 text-red-600 hover:text-red-800 font-medium"
                  :aria-label="`Supprimer ${p.name}`"
                  @click="pendingRemoval = p; actionError = ''"
                >
                  <Trash2 class="w-4 h-4" /> <span class="hidden sm:inline">Supprimer</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :pagination="pagination" @change="changePage" />
    </div>

    <ConfirmDialog
      :open="!!pendingRemoval"
      title="Supprimer l'annonce"
      :message="pendingRemoval ? `« ${pendingRemoval.name} » de ${pendingRemoval.farmer_name || 'cet agriculteur'} sera définitivement supprimée du marché.` : ''"
      confirm-label="Supprimer"
      danger
      with-reason
      :busy="isBusy"
      :error="actionError"
      @confirm="confirmRemoval"
      @cancel="pendingRemoval = null"
    />
  </div>
</template>
