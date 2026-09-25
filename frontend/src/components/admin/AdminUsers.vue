<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue';
import { Search, Loader2, Ban, RotateCcw } from 'lucide-vue-next';
import adminApi, { errorMessage } from '../../api/admin';
import { useAuthStore } from '../../stores/auth';
import PaginationBar from './PaginationBar.vue';
import ConfirmDialog from './ConfirmDialog.vue';
import { formatDate, ROLE_LABELS, ROLE_BADGES } from './format';

const authStore = useAuthStore();
const currentUserId = computed(() => authStore.user?.id);

const filters = reactive({ q: '', role: '', page: 1 });
const users = ref([]);
const pagination = ref(null);
const isLoading = ref(false);
const error = ref('');
const notice = ref('');

// Pending confirmation: { type: 'role' | 'suspend' | 'restore', user, role? }
const pending = ref(null);
const isBusy = ref(false);
const actionError = ref('');

const load = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const params = { page: filters.page, per_page: 20 };
    if (filters.q) params.q = filters.q;
    if (filters.role) params.role = filters.role;
    const res = await adminApi.getUsers(params);
    users.value = res.users;
    pagination.value = res.pagination;
  } catch (e) {
    error.value = errorMessage(e, 'Impossible de charger les utilisateurs');
  } finally {
    isLoading.value = false;
  }
};

let searchTimer;
watch(() => filters.q, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { filters.page = 1; load(); }, 300);
});
watch(() => filters.role, () => { filters.page = 1; load(); });

onMounted(load);

const changePage = (page) => { filters.page = page; load(); };

const askRoleChange = (user, event) => {
  const role = event.target.value;
  event.target.value = user.role; // revert until confirmed
  if (role !== user.role) pending.value = { type: 'role', user, role };
};

const dialog = computed(() => {
  const p = pending.value;
  if (!p) return null;
  if (p.type === 'role') {
    return {
      title: 'Changer le rôle',
      message: `${p.user.username} passera de « ${ROLE_LABELS[p.user.role]} » à « ${ROLE_LABELS[p.role]} ».`,
      confirmLabel: 'Changer le rôle',
      danger: p.role === 'admin'
    };
  }
  if (p.type === 'suspend') {
    return {
      title: 'Suspendre le compte',
      message: `${p.user.username} ne pourra plus se connecter jusqu'à ce que le compte soit rétabli.`,
      confirmLabel: 'Suspendre',
      danger: true
    };
  }
  return {
    title: 'Rétablir le compte',
    message: `${p.user.username} pourra de nouveau se connecter.`,
    confirmLabel: 'Rétablir',
    danger: false
  };
});

const confirm = async () => {
  const p = pending.value;
  isBusy.value = true;
  actionError.value = '';
  try {
    if (p.type === 'role') {
      await adminApi.updateUserRole(p.user.id, p.role);
      p.user.role = p.role;
      notice.value = `Rôle de ${p.user.username} mis à jour.`;
    } else if (p.type === 'suspend') {
      await adminApi.suspendUser(p.user.id);
      p.user.suspended = true;
      notice.value = `${p.user.username} a été suspendu.`;
    } else {
      await adminApi.restoreUser(p.user.id);
      p.user.suspended = false;
      notice.value = `${p.user.username} a été rétabli.`;
    }
    pending.value = null;
  } catch (e) {
    actionError.value = errorMessage(e);
  } finally {
    isBusy.value = false;
  }
};

const cancel = () => { pending.value = null; actionError.value = ''; };
</script>

<template>
  <div>
    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <label class="relative flex-grow">
        <span class="sr-only">Rechercher</span>
        <Search class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          v-model.trim="filters.q"
          type="search"
          placeholder="Nom d'utilisateur ou e-mail"
          class="w-full pl-9 pr-3 py-2 rounded-md border border-gray-300 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </label>
      <select
        v-model="filters.role"
        class="rounded-md border border-gray-300 text-sm px-3 py-2 focus:ring-2 focus:ring-primary-500"
        aria-label="Filtrer par rôle"
      >
        <option value="">Tous les rôles</option>
        <option v-for="(label, role) in ROLE_LABELS" :key="role" :value="role">{{ label }}</option>
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
              <th class="px-4 py-3 font-medium">Utilisateur</th>
              <th class="px-4 py-3 font-medium">Rôle</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">Localisation</th>
              <th class="px-4 py-3 font-medium text-right hidden sm:table-cell">Annonces</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">Inscrit le</th>
              <th class="px-4 py-3 font-medium hidden sm:table-cell">Statut</th>
              <th class="px-4 py-3 font-medium text-right"><span class="sr-only sm:not-sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="isLoading && !users.length">
              <td colspan="7" class="px-4 py-10 text-center"><Loader2 class="w-6 h-6 animate-spin text-primary-600 inline" /></td>
            </tr>
            <tr v-else-if="!users.length">
              <td colspan="7" class="px-4 py-10 text-center text-gray-500">Aucun utilisateur trouvé.</td>
            </tr>
            <tr v-for="u in users" :key="u.id" :class="{ 'opacity-60': isLoading }">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ u.username }}</div>
                <div class="text-gray-500">{{ u.email }}</div>
                <div v-if="u.phone" class="text-gray-400 text-xs">{{ u.phone }}</div>
                <span v-if="u.suspended" class="sm:hidden inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Suspendu</span>
              </td>
              <td class="px-4 py-3">
                <span v-if="u.id === currentUserId" class="px-2 py-0.5 rounded-full text-xs font-medium" :class="ROLE_BADGES[u.role]">
                  {{ ROLE_LABELS[u.role] }} (vous)
                </span>
                <select
                  v-else
                  :value="u.role"
                  class="rounded-md border border-gray-200 text-xs px-2 py-1 focus:ring-2 focus:ring-primary-500"
                  :aria-label="`Rôle de ${u.username}`"
                  @change="askRoleChange(u, $event)"
                >
                  <option v-for="(label, role) in ROLE_LABELS" :key="role" :value="role">{{ label }}</option>
                </select>
              </td>
              <td class="px-4 py-3 text-gray-600 hidden md:table-cell">{{ u.location || '—' }}</td>
              <td class="px-4 py-3 text-right tabular-nums hidden sm:table-cell">{{ u.product_count }}</td>
              <td class="px-4 py-3 text-gray-600 hidden md:table-cell whitespace-nowrap">{{ formatDate(u.created_at) }}</td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span v-if="u.suspended" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  <Ban class="w-3 h-3" /> Suspendu
                </span>
                <span v-else class="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">Actif</span>
              </td>
              <td class="px-4 py-3 text-right whitespace-nowrap">
                <template v-if="u.id !== currentUserId">
                  <button
                    v-if="!u.suspended"
                    class="inline-flex items-center gap-1 text-red-600 hover:text-red-800 font-medium"
                    :aria-label="`Suspendre ${u.username}`"
                    @click="pending = { type: 'suspend', user: u }"
                  >
                    <Ban class="w-4 h-4" /> <span class="hidden sm:inline">Suspendre</span>
                  </button>
                  <button
                    v-else
                    class="inline-flex items-center gap-1 text-primary-700 hover:text-primary-900 font-medium"
                    :aria-label="`Rétablir ${u.username}`"
                    @click="pending = { type: 'restore', user: u }"
                  >
                    <RotateCcw class="w-4 h-4" /> <span class="hidden sm:inline">Rétablir</span>
                  </button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :pagination="pagination" @change="changePage" />
    </div>

    <ConfirmDialog
      :open="!!pending"
      :title="dialog?.title || ''"
      :message="dialog?.message"
      :confirm-label="dialog?.confirmLabel"
      :danger="dialog?.danger"
      :busy="isBusy"
      :error="actionError"
      @confirm="confirm"
      @cancel="cancel"
    />
  </div>
</template>
