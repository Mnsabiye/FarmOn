<script setup>
import { MapPin, Phone, User } from 'lucide-vue-next';

defineProps({
  product: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 border border-gray-100">
    <div class="relative h-48 bg-gray-200">
      <img 
        :src="product.image_url || 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400'" 
        :alt="product.name"
        class="w-full h-full object-cover"
        @error="$event.target.src = 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400'"
      />
      <span class="absolute top-2 right-2 bg-primary-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm">
        {{ product.category }}
      </span>
    </div>
    
    <div class="p-4">
      <div class="flex justify-between items-start mb-2">
        <h3 class="text-xl font-bold text-gray-800 line-clamp-1">{{ product.name }}</h3>
        <span class="text-lg font-bold text-primary-600 whitespace-nowrap">
          {{ product.price_per_kg }} FBu
          <span class="text-xs text-gray-500 font-normal">/kg</span>
        </span>
      </div>
      
      <p class="text-gray-600 text-sm mb-3 line-clamp-2 h-10">{{ product.description }}</p>
      
      <div class="space-y-2 text-sm text-gray-600 mb-4">
        <div class="flex items-center gap-2">
          <User class="w-4 h-4 text-earth-500" />
          <span class="truncate">{{ product.farmer_name || 'Agriculteur' }}</span>
        </div>
        <div class="flex items-center gap-2">
          <MapPin class="w-4 h-4 text-earth-500" />
          <span class="truncate">{{ product.farmer_location || 'Lieu inconnu' }}</span>
        </div>
        <div class="flex items-center gap-2" v-if="product.farmer_phone">
          <Phone class="w-4 h-4 text-earth-500" />
          <span class="truncate">{{ product.farmer_phone }}</span>
        </div>
      </div>
      
      <div class="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
        <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          Dispo: {{ product.quantity_available }} kg
        </span>
        
        <a 
          v-if="product.farmer_phone"
          :href="`tel:${product.farmer_phone}`"
          class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center gap-2"
        >
          <Phone class="w-3 h-3" />
          Contacter
        </a>
      </div>
    </div>
  </div>
</template>
