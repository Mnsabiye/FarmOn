<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { LayoutDashboard, Users, Package, TrendingUp, History, ShieldCheck } from 'lucide-vue-next';
import AdminOverview from '../components/admin/AdminOverview.vue';
import AdminUsers from '../components/admin/AdminUsers.vue';
import AdminProducts from '../components/admin/AdminProducts.vue';
import AdminMarketPrices from '../components/admin/AdminMarketPrices.vue';
import AdminAuditLog from '../components/admin/AdminAuditLog.vue';

const route = useRoute();
const router = useRouter();

const tabs = [
  { id: 'overview', label: "Vue d'ensemble", icon: LayoutDashboard, component: AdminOverview },
  { id: 'users', label: 'Utilisateurs', icon: Users, component: AdminUsers },
  { id: 'products', label: 'Annonces', icon: Package, component: AdminProducts },
  { id: 'prices', label: 'Prix du marché', icon: TrendingUp, component: AdminMarketPrices },
  { id: 'activity', label: 'Journal', icon: History, component: AdminAuditLog }
];

// The active tab lives in the URL so it survives refreshes and can be linked
const activeTab = computed(() => tabs.find(t => t.id === route.query.tab) || tabs[0]);

const selectTab = (id) => {
  router.replace({ query: { ...route.query, tab: id === 'overview' ? undefined : id } });
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-primary-100 rounded-lg">
        <ShieldCheck class="w-6 h-6 text-primary-700" />
      </div>
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Administration</h1>
        <p class="text-sm text-gray-500">Gérez les membres, les annonces et les prix de FarmOn.</p>
      </div>
    </div>

    <nav class="border-b border-gray-200 mb-6 -mx-4 px-4 overflow-x-auto" aria-label="Sections d'administration">
      <ul class="flex gap-1 min-w-max">
        <li v-for="tab in tabs" :key="tab.id">
          <button
            class="flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition"
            :class="activeTab.id === tab.id
              ? 'border-primary-600 text-primary-700'
              : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'"
            :aria-current="activeTab.id === tab.id ? 'page' : undefined"
            @click="selectTab(tab.id)"
          >
            <component :is="tab.icon" class="w-4 h-4" />
            {{ tab.label }}
          </button>
        </li>
      </ul>
    </nav>

    <KeepAlive>
      <component :is="activeTab.component" :key="activeTab.id" @navigate="selectTab" />
    </KeepAlive>
  </div>
</template>
