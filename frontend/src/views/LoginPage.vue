<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { LogIn, Loader2, KeyRound, Mail } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const error = ref('');

const isLoading = computed(() => authStore.isLoading);

const handleLogin = async () => {
  error.value = '';
  try {
    await authStore.login({
      email: email.value,
      password: password.value
    });
    router.push(authStore.isFarmer ? '/dashboard' : '/marketplace');
  } catch (err) {
    error.value = err.response?.data?.error || 'Échec de la connexion. Veuillez vérifier vos identifiants.';
  }
};
</script>

<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
      <div>
        <div class="mx-auto h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
          <LogIn class="w-6 h-6 text-primary-600" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">Bienvenue</h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Connectez-vous à votre compte FarmConnect
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail class="h-5 w-5 text-gray-400" />
            </div>
            <label for="email-address" class="sr-only">Adresse Email</label>
            <input 
              id="email-address" 
              name="email" 
              type="email" 
              autocomplete="email" 
              required 
              v-model="email"
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Adresse Email" 
            />
          </div>
          <div class="relative">
             <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <KeyRound class="h-5 w-5 text-gray-400" />
            </div>
            <label for="password" class="sr-only">Mot de passe</label>
            <input 
              id="password" 
              name="password" 
              type="password" 
              autocomplete="current-password" 
              required 
              v-model="password"
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Mot de passe" 
            />
          </div>
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-md border border-red-100">
          {{ error }}
        </div>

        <div>
          <button 
            type="submit" 
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <Loader2 class="h-5 w-5 text-primary-500 animate-spin group-hover:text-primary-400" />
            </span>
            <span v-else class="absolute left-0 inset-y-0 flex items-center pl-3">
              <LogIn class="h-5 w-5 text-primary-500 group-hover:text-primary-400" />
            </span>
            {{ isLoading ? 'Connexion en cours...' : 'Se connecter' }}
          </button>
        </div>
      </form>
      
      <div class="text-center">
        <p class="text-sm text-gray-600">
          Pas encore inscrit? 
          <RouterLink to="/register" class="font-medium text-primary-600 hover:text-primary-500">
            Créer un compte
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
