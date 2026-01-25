<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import ChatWidget from './components/ChatWidget.vue'
import { Sprout, Mail, Phone, MapPin, Facebook, Twitter, Instagram } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans flex flex-col">
    <NavBar />
    
    <main class="flex-grow">
      <RouterView />
    </main>
    
    <ChatWidget />
    
    <footer class="bg-primary-900 text-white pt-12 pb-8 mt-12">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <!-- Brand Column -->
          <div>
            <div class="flex items-center space-x-2 mb-4">
              <Sprout class="w-8 h-8 text-primary-400" />
              <span class="text-xl font-bold">FarmOn</span>
            </div>
            <p class="text-primary-200 text-sm mb-4">
              Connecter les agriculteurs aux marchés. Une plateforme pour une agriculture plus intelligente et plus rentable.
            </p>
            <div class="flex space-x-4">
              <a href="#" class="text-primary-300 hover:text-white transition"><Facebook class="w-5 h-5" /></a>
              <a href="#" class="text-primary-300 hover:text-white transition"><Twitter class="w-5 h-5" /></a>
              <a href="#" class="text-primary-300 hover:text-white transition"><Instagram class="w-5 h-5" /></a>
            </div>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-primary-100">Liens Rapides</h3>
            <ul class="space-y-2">
              <li><router-link to="/" class="text-primary-300 hover:text-white transition">Accueil</router-link></li>
              <li><router-link to="/marketplace" class="text-primary-300 hover:text-white transition">Marché</router-link></li>
              <li><router-link to="/login" class="text-primary-300 hover:text-white transition">Connexion</router-link></li>
              <li><router-link to="/register" class="text-primary-300 hover:text-white transition">S'inscrire</router-link></li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-primary-100">Légal</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-primary-300 hover:text-white transition">Confidentialité</a></li>
              <li><a href="#" class="text-primary-300 hover:text-white transition">Conditions d'utilisation</a></li>
              <li><a href="#" class="text-primary-300 hover:text-white transition">Politique de cookies</a></li>
            </ul>
          </div>

          <!-- Contact -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-primary-100">Contact</h3>
            <ul class="space-y-3">
              <li class="flex items-start space-x-3 text-primary-300">
                <MapPin class="w-5 h-5 mt-0.5 flex-shrink-0" />
                <span>Bujumbura, Burundi</span>
              </li>
              <li class="flex items-center space-x-3 text-primary-300">
                <Phone class="w-5 h-5 flex-shrink-0" />
                <span>+257 67 877 278</span>
              </li>
              <li class="flex items-center space-x-3 text-primary-300">
                <Mail class="w-5 h-5 flex-shrink-0" />
                <span>farmconnect.bdi@gmail.com</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="border-t border-primary-800 pt-8 text-center text-primary-400 text-sm">
          <p>&copy; {{ new Date().getFullYear() }} FarmOn. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  </div>
</template>
