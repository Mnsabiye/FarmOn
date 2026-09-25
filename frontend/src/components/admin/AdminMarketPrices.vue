<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Loader2, Plus, Trash2 } from 'lucide-vue-next';
import adminApi, { errorMessage } from '../../api/admin';
import ConfirmDialog from './ConfirmDialog.vue';
import { formatDateTime, formatFbu } from './format';

const prices = ref([]);
const isLoading = ref(false);
const error = ref('');

const form = reactive({ crop_name: '', market_location: '', price: '' });
const isSaving = ref(false);
const formError = ref('');

const pendingDelete = ref(null);
const isBusy = ref(false);
const actionError = ref('');

const load = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const res = await adminApi.getMarketPrices({ limit: 100 });
    prices.value = res.prices;
  } catch (e) {
    error.value = errorMessage(e, 'Impossible de charger les prix');
  } finally {
    isLoading.value = false;
  }
};

onMounted(load);

const submit = async () => {
  formError.value = '';
  if (!form.crop_name.trim() || !form.market_location.trim() || !(Number(form.price) > 0)) {
    formError.value = 'Renseignez le produit, le marché et un prix supérieur à 0.';
    return;
  }
  isSaving.value = true;
  try {
    const res = await adminApi.createMarketPrice({
      crop_name: form.crop_name.trim(),
      market_location: form.market_location.trim(),
      price: Number(form.price)
    });
    if (res.price) prices.value.unshift(res.price);
    form.price = '';
  } catch (e) {
    formError.value = errorMessage(e);
  } finally {
    isSaving.value = false;
  }
};

const confirmDelete = async () => {
  isBusy.value = true;
  actionError.value = '';
  try {
    await adminApi.deleteMarketPrice(pendingDelete.value.id);
    prices.value = prices.value.filter(p => p.id !== pendingDelete.value.id);
    pendingDelete.value = null;
  } catch (e) {
    actionError.value = errorMessage(e);
  } finally {
    isBusy.value = false;
  }
};
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- New price -->
    <form class="bg-white rounded-lg shadow-sm border border-gray-100 p-5 h-fit" @submit.prevent="submit">
      <h3 class="font-semibold text-gray-900 mb-1">Ajouter un prix</h3>
      <p class="text-sm text-gray-500 mb-4">Utilisé par le bandeau des prix et l'assistant.</p>

      <label class="block mb-3">
        <span class="text-sm font-medium text-gray-700">Produit</span>
        <input v-model="form.crop_name" maxlength="100" placeholder="ex. Haricots" class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500" />
      </label>
      <label class="block mb-3">
        <span class="text-sm font-medium text-gray-700">Marché</span>
        <input v-model="form.market_location" maxlength="100" placeholder="ex. Bujumbura Central" class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500" />
      </label>
      <label class="block mb-4">
        <span class="text-sm font-medium text-gray-700">Prix (FBu / kg)</span>
        <input v-model="form.price" type="number" min="1" step="1" class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500" />
      </label>

      <p v-if="formError" class="text-sm text-red-600 mb-3">{{ formError }}</p>

      <button type="submit" class="w-full bg-primary-600 hover:bg-primary-700 text-white rounded-md py-2 text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-60" :disabled="isSaving">
        <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
        <Plus v-else class="w-4 h-4" />
        Enregistrer
      </button>
    </form>

    <!-- History -->
    <div class="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="error" class="bg-red-50 text-red-700 p-4">{{ error }}</div>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-left text-gray-500 uppercase text-xs tracking-wide">
            <tr>
              <th class="px-4 py-3 font-medium">Produit</th>
              <th class="px-4 py-3 font-medium">Marché</th>
              <th class="px-4 py-3 font-medium text-right">Prix / kg</th>
              <th class="px-4 py-3 font-medium hidden sm:table-cell">Relevé le</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="isLoading && !prices.length">
              <td colspan="5" class="px-4 py-10 text-center"><Loader2 class="w-6 h-6 animate-spin text-primary-600 inline" /></td>
            </tr>
            <tr v-else-if="!prices.length">
              <td colspan="5" class="px-4 py-10 text-center text-gray-500">Aucun prix enregistré.</td>
            </tr>
            <tr v-for="p in prices" :key="p.id">
              <td class="px-4 py-3 font-medium text-gray-900">{{ p.crop_name }}</td>
              <td class="px-4 py-3 text-gray-600">{{ p.market_location }}</td>
              <td class="px-4 py-3 text-right tabular-nums whitespace-nowrap">{{ formatFbu(p.price) }}</td>
              <td class="px-4 py-3 text-gray-600 hidden sm:table-cell whitespace-nowrap">{{ formatDateTime(p.date_recorded) }}</td>
              <td class="px-4 py-3 text-right">
                <button class="text-gray-400 hover:text-red-600" :aria-label="`Supprimer le prix ${p.crop_name}`" @click="pendingDelete = p; actionError = ''">
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ConfirmDialog
      :open="!!pendingDelete"
      title="Supprimer ce prix"
      :message="pendingDelete ? `${pendingDelete.crop_name} à ${pendingDelete.market_location} (${formatFbu(pendingDelete.price)}) sera supprimé.` : ''"
      confirm-label="Supprimer"
      danger
      :busy="isBusy"
      :error="actionError"
      @confirm="confirmDelete"
      @cancel="pendingDelete = null"
    />
  </div>
</template>
