<script setup>
import { ref } from 'vue';
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next';

// Mock data - in a real app this would come from an API
const marketPrices = ref([
  { id: 1, crop: 'Haricots', market: 'Bujumbura', price: 1800, change: 'up' },
  { id: 2, crop: 'Maïs', market: 'Gitega', price: 1200, change: 'down' },
  { id: 3, crop: 'Tomates', market: 'Ngozi', price: 800, change: 'stable' },
  { id: 4, crop: 'Riz', market: 'Bujumbura', price: 2200, change: 'up' },
  { id: 5, crop: 'Pommes de terre', market: 'Kayanza', price: 600, change: 'down' },
  { id: 6, crop: 'Oignons', market: 'Cibitoke', price: 1500, change: 'stable' },
]);
</script>

<template>
  <div class="bg-earth-600 text-white overflow-hidden py-2 shadow-inner">
    <div class="flex animate-scroll whitespace-nowrap">
      <!-- First copy of data -->
      <div class="flex items-center space-x-8 px-4">
        <div v-for="item in marketPrices" :key="item.id" class="flex items-center space-x-2 text-sm">
          <span class="font-bold text-earth-100">{{ item.crop }}</span>
          <span class="text-earth-200">({{ item.market }})</span>
          <span class="font-bold">{{ item.price }} FBu</span>
          
          <TrendingUp v-if="item.change === 'up'" class="w-4 h-4 text-green-300" />
          <TrendingDown v-if="item.change === 'down'" class="w-4 h-4 text-red-300" />
          <Minus v-if="item.change === 'stable'" class="w-4 h-4 text-gray-300" />
        </div>
      </div>
      
      <!-- Duplicate for seamless scrolling -->
      <div class="flex items-center space-x-8 px-4">
        <div v-for="item in marketPrices" :key="'dup-' + item.id" class="flex items-center space-x-2 text-sm">
          <span class="font-bold text-earth-100">{{ item.crop }}</span>
          <span class="text-earth-200">({{ item.market }})</span>
          <span class="font-bold">{{ item.price }} FBu</span>
          
          <TrendingUp v-if="item.change === 'up'" class="w-4 h-4 text-green-300" />
          <TrendingDown v-if="item.change === 'down'" class="w-4 h-4 text-red-300" />
          <Minus v-if="item.change === 'stable'" class="w-4 h-4 text-gray-300" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.animate-scroll {
  animation: scroll 20s linear infinite;
}

.animate-scroll:hover {
  animation-play-state: paused;
}
</style>
