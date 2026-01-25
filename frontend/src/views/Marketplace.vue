<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useProductStore } from '../stores/products';
import ProductCard from '../components/ProductCard.vue';
import { Search, SlidersHorizontal, Loader2, X } from 'lucide-vue-next';

const productStore = useProductStore();
const searchQuery = ref('');
const selectedCategory = ref('');
const isFilterOpen = ref(false);

const categories = ['Tous', 'Légumes', 'Fruits', 'Céréales', 'Tubercules', 'Autres'];

onMounted(() => {
  productStore.fetchProducts();
});

const isLoading = computed(() => productStore.isLoading);
const products = computed(() => productStore.products);

// Client-side filtering for search query (demo purposes, ideally query backend)
const filteredProducts = computed(() => {
  return products.value.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          product.description?.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesCategory = selectedCategory.value === '' || selectedCategory.value === 'Tous' || product.category === selectedCategory.value;
    
    return matchesSearch && matchesCategory;
  });
});

const applyFilters = () => {
  productStore.fetchProducts({
    category: selectedCategory.value !== 'Tous' ? selectedCategory.value : undefined
  });
  // On mobile, close sidebar after applying
  if (window.innerWidth < 768) {
    isFilterOpen.value = false;
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedCategory.value = 'Tous';
  productStore.fetchProducts();
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <!-- Filter Sidebar (Mobile Toggle) -->
      <button 
        @click="isFilterOpen = !isFilterOpen"
        class="md:hidden flex items-center justify-center gap-2 bg-primary-600 text-white p-3 rounded-lg mb-4"
      >
        <SlidersHorizontal class="w-5 h-5" />
        Filtres
      </button>
      
      <!-- Filter Sidebar -->
      <aside 
        :class="[
          'md:w-1/4 bg-white p-6 rounded-lg shadow-sm h-fit border border-gray-100 transition-all duration-300 z-30',
          isFilterOpen ? 'fixed inset-0 m-4 md:static md:m-0 md:block' : 'hidden md:block'
        ]"
      >
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-800">Filtres</h2>
          <button @click="isFilterOpen = false" class="md:hidden text-gray-500">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="space-y-6">
          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Recherche</label>
            <div class="relative">
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="Haricots, Maïs..." 
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm"
              />
              <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            </div>
          </div>
          
          <!-- Categories -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
            <div class="space-y-2">
              <label 
                v-for="cat in categories" 
                :key="cat"
                class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
              >
                <input 
                  type="radio" 
                  name="category" 
                  :value="cat" 
                  v-model="selectedCategory"
                  class="text-primary-600 focus:ring-primary-500 border-gray-300"
                />
                <span class="text-gray-600 text-sm">{{ cat }}</span>
              </label>
            </div>
          </div>
          

          
          <!-- Actions -->
          <div class="pt-4 flex flex-col gap-2">
            <button 
              @click="applyFilters"
              class="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition text-sm font-medium"
            >
              Appliquer
            </button>
            <button 
              @click="clearFilters"
              class="w-full bg-white text-gray-500 border border-gray-200 py-2 rounded-lg hover:bg-gray-50 transition text-sm"
            >
              Effacer tout
            </button>
          </div>
        </div>
      </aside>
      
      <!-- Product Grid -->
      <main class="flex-1">
        <div class="mb-6 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Produits du Marché</h1>
          <p class="text-sm text-gray-500">{{ filteredProducts.length }} résultats trouvés</p>
        </div>
        
        <div v-if="isLoading" class="flex justify-center items-center h-64">
          <Loader2 class="w-10 h-10 text-primary-500 animate-spin" />
        </div>
        
        <div v-else-if="filteredProducts.length === 0" class="text-center py-20 bg-white rounded-lg border border-gray-100">
          <div class="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search class="w-8 h-8 text-gray-400" />
          </div>
          <h3 class="text-lg font-medium text-gray-900">Aucun produit trouvé</h3>
          <p class="text-gray-500 mb-6">Essayez d'ajuster votre recherche ou vos filtres.</p>
          <button @click="clearFilters" class="text-primary-600 font-medium hover:underline">Effacer les filtres</button>
        </div>
        
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <ProductCard 
            v-for="product in filteredProducts" 
            :key="product.id" 
            :product="product" 
          />
        </div>
      </main>
    </div>
  </div>
</template>
