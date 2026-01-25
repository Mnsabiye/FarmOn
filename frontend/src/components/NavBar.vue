<script setup>
import { ref, computed } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { Menu, X, LogOut, Sprout, ShoppingBag, LayoutDashboard, LogIn } from 'lucide-vue-next';

const authStore = useAuthStore();
const router = useRouter();
const isMenuOpen = ref(false);

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

const logout = async () => {
  await authStore.logout();
  router.push('/login');
  isMenuOpen.value = false;
};

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isFarmer = computed(() => authStore.isFarmer);
const user = computed(() => authStore.user);
</script>

<template>
  <nav class="bg-primary-600 text-white shadow-lg sticky top-0 z-40">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center space-x-2 text-xl font-bold hover:text-primary-100 transition">
          <Sprout class="w-8 h-8 text-white" />
          <span>FarmOn</span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-6">
          <RouterLink to="/" class="hover:text-primary-100 transition font-medium">Accueil</RouterLink>
          <RouterLink to="/marketplace" class="hover:text-primary-100 transition font-medium flex items-center gap-1">
            <ShoppingBag class="w-4 h-4" />
            Marché
          </RouterLink>
          
          <template v-if="isAuthenticated">
            <RouterLink v-if="isFarmer" to="/dashboard" class="hover:text-primary-100 transition font-medium flex items-center gap-1">
              <LayoutDashboard class="w-4 h-4" />
              Tableau de Bord
            </RouterLink>
            
            <div class="flex items-center gap-4 ml-4 pl-4 border-l border-primary-500">
              <span class="text-sm font-medium">{{ user?.username }}</span>
              <button @click="logout" class="bg-primary-700 hover:bg-primary-800 px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-1">
                <LogOut class="w-4 h-4" />
                Déconnexion
              </button>
            </div>
          </template>
          
          <template v-else>
            <RouterLink to="/login" class="hover:text-primary-100 transition font-medium flex items-center gap-1">
              <LogIn class="w-4 h-4" />
              Connexion
            </RouterLink>
            <RouterLink to="/register" class="bg-white text-primary-600 hover:bg-primary-50 px-4 py-2 rounded-md font-medium transition shadow-sm">
              S'inscrire
            </RouterLink>
          </template>
        </div>

        <!-- Mobile Menu Button -->
        <button @click="toggleMenu" class="md:hidden p-2 rounded-md hover:bg-primary-700 focus:outline-none">
          <Menu v-if="!isMenuOpen" class="w-6 h-6" />
          <X v-else class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isMenuOpen" class="md:hidden bg-primary-700 border-t border-primary-600">
      <div class="px-4 pt-2 pb-4 space-y-1">
        <RouterLink to="/" class="block px-3 py-2 rounded-md hover:bg-primary-600 font-medium" @click="isMenuOpen = false">Accueil</RouterLink>
        <RouterLink to="/marketplace" class="block px-3 py-2 rounded-md hover:bg-primary-600 font-medium" @click="isMenuOpen = false">Marché</RouterLink>
        
        <template v-if="isAuthenticated">
          <RouterLink v-if="isFarmer" to="/dashboard" class="block px-3 py-2 rounded-md hover:bg-primary-600 font-medium" @click="isMenuOpen = false">Tableau de Bord</RouterLink>
          <div class="pt-4 mt-2 border-t border-primary-600">
            <div class="px-3 py-2 text-primary-100 text-sm">Connecté en tant que <span class="font-bold text-white">{{ user?.username }}</span></div>
            <button @click="logout" class="w-full text-left px-3 py-2 rounded-md hover:bg-primary-600 font-medium flex items-center gap-2">
              <LogOut class="w-4 h-4" />
              Déconnexion
            </button>
          </div>
        </template>
        
        <template v-else>
          <div class="pt-4 mt-2 border-t border-primary-600 grid grid-cols-2 gap-2">
            <RouterLink to="/login" class="text-center px-3 py-2 rounded-md bg-primary-800 hover:bg-primary-900 font-medium" @click="isMenuOpen = false">
              Connexion
            </RouterLink>
            <RouterLink to="/register" class="text-center px-3 py-2 rounded-md bg-white text-primary-600 hover:bg-gray-100 font-medium" @click="isMenuOpen = false">
              S'inscrire
            </RouterLink>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>
