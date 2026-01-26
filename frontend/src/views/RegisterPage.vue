<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { UserPlus, Loader2, User, Mail, KeyRound, Phone, MapPin, Check, X } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();

const formData = ref({
  username: '',
  email: '',
  password: '',
  role: 'farmer',
  phone: '',
  location: ''
});

const error = ref('');
const isLoading = computed(() => authStore.isLoading);

const passwordRequirements = computed(() => {
  const pwd = formData.value.password;
  return [
    { label: 'Au moins 8 caractères', valid: pwd.length >= 8 },
    { label: 'Au moins une majuscule', valid: /[A-Z]/.test(pwd) },
    { label: 'Au moins un chiffre', valid: /[0-9]/.test(pwd) },
    { label: 'Au moins un caractère spécial', valid: /[^A-Za-z0-9]/.test(pwd) }
  ];
});

const isPasswordValid = computed(() => {
  return passwordRequirements.value.every(req => req.valid);
});

const handleRegister = async () => {
  error.value = '';
  
  if (!isPasswordValid.value) {
    error.value = "Le mot de passe ne respecte pas les critères de sécurité.";
    return;
  }

  try {
    await authStore.register(formData.value);
    router.push(authStore.isFarmer ? '/dashboard' : '/marketplace');
  } catch (err) {
    console.log('Registration details:', err);
    error.value = err.message || err.response?.data?.error || "Échec de l'inscription. Veuillez réessayer.";
  }
};
</script>

<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
      <div>
        <div class="mx-auto h-12 w-12 bg-earth-100 rounded-full flex items-center justify-center">
          <UserPlus class="w-6 h-6 text-earth-600" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">Rejoindre FarmConnect</h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Créez votre compte aujourd'hui
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User class="h-5 w-5 text-gray-400" />
            </div>
            <input 
              v-model="formData.username"
              type="text" 
              required 
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Nom d'utilisateur" 
            />
          </div>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail class="h-5 w-5 text-gray-400" />
            </div>
            <input 
              v-model="formData.email"
              type="email" 
              required 
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Adresse Email" 
            />
          </div>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <KeyRound class="h-5 w-5 text-gray-400" />
            </div>
            <input 
              v-model="formData.password"
              type="password" 
              required 
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Mot de passe" 
            />
          </div>

          <!-- Password Strength Indicator -->
          <div v-if="formData.password" class="px-4 py-2 bg-gray-50 border border-gray-100 rounded-md">
            <p class="text-xs font-semibold text-gray-500 mb-2">Sécurité du mot de passe:</p>
            <ul class="space-y-1">
              <li v-for="(req, index) in passwordRequirements" :key="index" class="flex items-center text-xs">
                <component 
                  :is="req.valid ? 'Check' : 'X'" 
                  class="w-3 h-3 mr-2"
                  :class="req.valid ? 'text-green-500' : 'text-gray-300'"
                />
                <span :class="req.valid ? 'text-green-700' : 'text-gray-500'">{{ req.label }}</span>
              </li>
            </ul>
          </div>
          
          <!-- Role Selection -->
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-1 px-3 py-2 bg-gray-50 border-x border-gray-300">Je suis un(e):</label>
            <div class="flex border border-gray-300 border-t-0 p-2 bg-white gap-2">
              <label class="flex-1 cursor-pointer">
                <input type="radio" v-model="formData.role" value="farmer" class="sr-only peer" />
                <div class="py-2 px-4 text-center rounded-md border border-gray-200 peer-checked:bg-primary-50 peer-checked:border-primary-500 peer-checked:text-primary-700 hover:bg-gray-50 transition">
                  Agriculteur
                </div>
              </label>
              <label class="flex-1 cursor-pointer">
                <input type="radio" v-model="formData.role" value="buyer" class="sr-only peer" />
                <div class="py-2 px-4 text-center rounded-md border border-gray-200 peer-checked:bg-earth-50 peer-checked:border-earth-500 peer-checked:text-earth-700 hover:bg-gray-50 transition">
                  Acheteur
                </div>
              </label>
            </div>
          </div>
          
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Phone class="h-5 w-5 text-gray-400" />
            </div>
            <input 
              v-model="formData.phone"
              type="tel" 
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Numéro de téléphone (Optionnel)" 
            />
          </div>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MapPin class="h-5 w-5 text-gray-400" />
            </div>
            <input 
              v-model="formData.location"
              type="text" 
              class="appearance-none rounded-none relative block w-full px-10 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" 
              placeholder="Localisation (Optionnel)" 
            />
          </div>
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-md border border-red-100">
          {{ error }}
        </div>

        <div>
          <button 
            type="submit" 
            :disabled="isLoading || !isPasswordValid"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-earth-600 hover:bg-earth-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-earth-500 disabled:opacity-50 transition"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <Loader2 class="h-5 w-5 text-earth-300 animate-spin" />
            </span>
            <span v-else class="absolute left-0 inset-y-0 flex items-center pl-3">
              <UserPlus class="h-5 w-5 text-earth-300" />
            </span>
            {{ isLoading ? 'Création de compte...' : 'Créer un compte' }}
          </button>
        </div>
      </form>
      
      <div class="text-center">
        <p class="text-sm text-gray-600">
          Déjà un compte? 
          <RouterLink to="/login" class="font-medium text-earth-600 hover:text-earth-500">
            Se connecter
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
