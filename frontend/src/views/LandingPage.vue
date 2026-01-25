<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ArrowRight, Sprout, ShoppingBag, ShieldCheck, Users, Heart, Handshake, Globe } from 'lucide-vue-next';
import PriceTicker from '../components/PriceTicker.vue';

const router = useRouter();
const authStore = useAuthStore();

const handleStartSelling = () => {
  if (authStore.isAuthenticated && authStore.isFarmer) {
    router.push('/dashboard');
  } else if (authStore.isAuthenticated) {
    router.push('/marketplace'); // Buyers go to marketplace
  } else {
    router.push('/login');
  }
};
</script>

<template>
  <div class="flex flex-col">
    <!-- Price Ticker -->
    <PriceTicker />
    
    <!-- Hero Section -->
    <section class="relative bg-earth-100 overflow-hidden">
      <!-- Background Pattern/Image -->
      <div class="absolute inset-0 z-0 opacity-20 bg-[url('https://images.unsplash.com/photo-1595841696677-6489b3f8aed1?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80')] bg-cover bg-center"></div>
      
      <div class="container mx-auto px-4 py-16 md:py-24 relative z-10">
        <div class="max-w-3xl mx-auto text-center">
          <h1 class="text-4xl md:text-6xl font-extrabold text-primary-900 mb-6 leading-tight">
            Connecter. Cultiver. <span class="text-primary-600">Prospérer.</span>
          </h1>
          <p class="text-xl md:text-2xl text-earth-800 mb-10 leading-relaxed">
            La première plateforme numérique du Burundi connectant les agriculteurs directement aux marchés et aux informations vitales.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              @click="handleStartSelling" 
              class="bg-primary-600 hover:bg-primary-700 text-white text-lg font-bold py-3 px-8 rounded-full shadow-lg transition transform hover:scale-105 flex items-center justify-center gap-2 cursor-pointer"
            >
              Commencer à Vendre
              <ArrowRight class="w-5 h-5" />
            </button>
            <RouterLink 
              to="/marketplace" 
              class="bg-white hover:bg-gray-50 text-primary-700 border-2 border-primary-100 text-lg font-bold py-3 px-8 rounded-full shadow-md transition transform hover:scale-105 flex items-center justify-center gap-2"
            >
              Voir le Marché
              <ShoppingBag class="w-5 h-5" />
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center text-primary-900 mb-4">Pourquoi Choisir FarmOn?</h2>

        <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">Autonomiser la communauté agricole avec une technologie conçue pour les besoins réels.</p>
        
        <div class="grid md:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="bg-primary-50 p-8 rounded-2xl transition hover:shadow-lg border border-primary-100">
            <div class="bg-primary-200 w-14 h-14 rounded-full flex items-center justify-center mb-6 text-primary-700">
              <ShoppingBag class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-primary-800 mb-3">Marché Direct</h3>
            <p class="text-gray-700">Éliminez les intermédiaires. Les agriculteurs vendent directement aux acheteurs, assurant des prix équitables et des produits plus frais pour tous.</p>
          </div>
          
          <!-- Feature 2 -->
          <div class="bg-earth-50 p-8 rounded-2xl transition hover:shadow-lg border border-earth-100">
            <div class="bg-earth-200 w-14 h-14 rounded-full flex items-center justify-center mb-6 text-earth-700">
              <Sprout class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-earth-800 mb-3">Assistant Intelligent</h3>
            <p class="text-gray-700">Obtenez des mises à jour météo et des conseils agricoles via notre assistant bilingue (Français & Kirundi) à portée de main.</p>
          </div>
          
          <!-- Feature 3 -->
          <div class="bg-blue-50 p-8 rounded-2xl transition hover:shadow-lg border border-blue-100">
            <div class="bg-blue-200 w-14 h-14 rounded-full flex items-center justify-center mb-6 text-blue-700">
              <ShieldCheck class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-blue-800 mb-3">Confiance Vérifiée</h3>
            <p class="text-gray-700">Des transactions sûres et des profils vérifiés construisent une communauté de confiance entre producteurs et consommateurs.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- About Us Section -->
    <section class="py-20 bg-earth-50 relative overflow-hidden">
      <!-- Decorative Elements -->
      <div class="absolute top-0 left-0 w-64 h-64 bg-earth-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 -translate-x-1/2 -translate-y-1/2"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-primary-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 translate-x-1/3 translate-y-1/3"></div>

      <div class="container mx-auto px-4 relative z-10">
        <div class="text-center mb-16">
          <span class="text-primary-600 font-bold tracking-wider uppercase text-sm mb-2 block">Notre Histoire</span>
          <h2 class="text-3xl md:text-5xl font-extrabold text-primary-900 mb-6">À Propos de FarmOn</h2>

          <div class="w-24 h-1.5 bg-primary-500 mx-auto rounded-full"></div>
        </div>

        <!-- Mission & Vision -->
        <div class="grid md:grid-cols-2 gap-12 mb-20">
          <div class="bg-white p-8 md:p-10 rounded-3xl shadow-lg border-l-8 border-primary-500 transform hover:-translate-y-1 transition duration-300">
            <h3 class="text-2xl font-bold text-primary-800 mb-4 flex items-center gap-3">
              <Sprout class="w-8 h-8 text-primary-600" />
              Notre Mission
            </h3>
            <p class="text-xl font-medium text-earth-700 italic mb-4">"Connecter les agriculteurs. Nourrir l’avenir."</p>
            <p class="text-gray-600 leading-relaxed">
              FarmOn est né pour briser les barrières qui maintiennent les agriculteurs dans la précarité et ralentissent l'innovation rurale. Nous sommes une plateforme numérique qui redonne aux agriculteurs le pouvoir d’agir.

            </p>
          </div>
          
          <div class="bg-white p-8 md:p-10 rounded-3xl shadow-lg border-l-8 border-earth-500 transform hover:-translate-y-1 transition duration-300">
            <h3 class="text-2xl font-bold text-primary-800 mb-4 flex items-center gap-3">
              <ArrowRight class="w-8 h-8 text-earth-600" /> 
              Notre Vision
            </h3>
            <p class="text-gray-600 leading-relaxed">
              En Afrique, l’agriculture est plus qu’un secteur économique — c’est une identité, un héritage. Cependant, l'isolement numérique et le manque d'accès aux marchés freinent ce potentiel. Nous avons créé un espace unique où chaque agriculteur peut apprendre, comparer, décider et prospérer. Plus qu'une simple aide, FarmOn construit un écosystème durable et autonome.

            </p>
          </div>
        </div>

        <!-- Values -->
        <div class="mb-20">
          <h3 class="text-2xl md:text-3xl font-bold text-center text-primary-900 mb-10">Nos Valeurs Fondamentales</h3>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl hover:bg-white transition shadow-sm hover:shadow-md text-center group">
              <div class="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-primary-600 transition duration-300">
                <Heart class="w-8 h-8 text-primary-600 group-hover:text-white transition duration-300" />
              </div>
              <h4 class="text-xl font-bold text-gray-800 mb-3">L'Agriculteur au Cœur</h4>
              <p class="text-gray-600">Contrairement à d’autres initiatives, nous plaçons les agriculteurs au cœur de nos priorités, avant le profit.</p>
            </div>

            <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl hover:bg-white transition shadow-sm hover:shadow-md text-center group">
              <div class="bg-earth-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-earth-600 transition duration-300">
                <Handshake class="w-8 h-8 text-earth-600 group-hover:text-white transition duration-300" />
              </div>
              <h4 class="text-xl font-bold text-gray-800 mb-3">Collaboration</h4>
              <p class="text-gray-600">Nous relions agriculteurs, acheteurs, coopératives et institutions pour créer un véritable écosystème collaboratif.</p>
            </div>

            <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl hover:bg-white transition shadow-sm hover:shadow-md text-center group">
              <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-blue-600 transition duration-300">
                <Globe class="w-8 h-8 text-blue-600 group-hover:text-white transition duration-300" />
              </div>
              <h4 class="text-xl font-bold text-gray-800 mb-3">Inclusion</h4>
              <p class="text-gray-600">Nous prônons une approche humaine et inclusive, accessible à tous les niveaux technologiques.</p>
            </div>
          </div>
        </div>

        <!-- Team & Impact -->
        <div class="grid md:grid-cols-12 gap-8 items-start">
          <!-- Team -->
          <div class="md:col-span-5 bg-primary-800 text-white p-8 rounded-3xl shadow-xl">
            <h3 class="text-2xl font-bold mb-6 border-b border-primary-600 pb-4">L'Équipe</h3>
            <p class="mb-6 text-primary-100">Derrière cette innovation se trouve une équipe passionnée par l'agriculture et la technologie :</p>
            
            <div class="space-y-6">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center font-bold text-xl">A</div>
                <div>
                  <div class="font-bold text-lg">Ange Brunella IYOKWIZERA</div>
                  <div class="text-primary-300 text-sm uppercase tracking-wide">Innovatrice</div>
                </div>
              </div>
              
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center font-bold text-xl">S</div>
                <div>
                  <div class="font-bold text-lg">S. Omraam KILANYOSSI</div>
                  <div class="text-primary-300 text-sm uppercase tracking-wide">Mentor</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Impact -->
          <div class="md:col-span-7 bg-white p-8 md:p-12 rounded-3xl shadow-lg flex flex-col justify-center h-full">
            <h3 class="text-2xl font-bold text-primary-900 mb-6">Notre Impact</h3>
            <p class="text-lg text-gray-700 leading-relaxed mb-6">
              Nous œuvrons pour plus de transparence dans la vente des produits, une hausse des revenus pour les producteurs, et la création d'un réseau d'apprentissage résilient.
            </p>
            <div class="flex gap-4 flex-wrap">
               <span class="px-4 py-2 bg-green-100 text-green-700 rounded-full font-bold text-sm">Transparence</span>
               <span class="px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-bold text-sm">Revenus Équitables</span>
               <span class="px-4 py-2 bg-earth-100 text-earth-700 rounded-full font-bold text-sm">Réseau Résilient</span>
            </div>
          </div>
        </div>

      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-20 bg-primary-800 text-white relative overflow-hidden">
      <!-- Decorational circles -->
      <div class="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-primary-700 opacity-50"></div>
      <div class="absolute bottom-0 left-0 -ml-20 -mb-20 w-60 h-60 rounded-full bg-primary-600 opacity-50"></div>
      
      <div class="container mx-auto px-4 text-center relative z-10">
        <h2 class="text-3xl md:text-4xl font-bold mb-6">Prêt à Transformer Votre Récolte?</h2>
        <p class="text-xl text-primary-100 mb-10 max-w-2xl mx-auto">Rejoignez des milliers d'agriculteurs burundais qui participent à la révolution agricole numérique.</p>
        <RouterLink 
          to="/register" 
          class="inline-flex items-center gap-2 bg-white text-primary-700 hover:bg-primary-50 font-bold py-3 px-8 rounded-full shadow-lg transition text-lg"
        >
          <Users class="w-5 h-5" />
          Rejoindre la Communauté
        </RouterLink>
      </div>
    </section>
  </div>
</template>
