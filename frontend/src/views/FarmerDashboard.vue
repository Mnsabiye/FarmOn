<script setup>
import { ref, onMounted, computed } from 'vue';
import { useProductStore } from '../stores/products';
import { useAuthStore } from '../stores/auth';
import { storageService } from '../services/storage';
import { Plus, Pencil, Trash2, X, Upload, Loader2, Package } from 'lucide-vue-next';

const productStore = useProductStore();
const authStore = useAuthStore();

const isModalOpen = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const isLoading = computed(() => productStore.isLoading);
const user = computed(() => authStore.user);
const selectedFile = ref(null);
const uploadError = ref(null);
const submitError = ref(null);

// Filter products to show only current farmer's products
const farmerProducts = computed(() => {
  return productStore.products.filter(p => p.farmer_id === user.value?.id) || [];
});

const formData = ref({
  name: '',
  category: 'Légumes',
  price_per_kg: '',
  quantity_available: '',
  description: '',
  image_url: ''
});

const categories = ['Légumes', 'Fruits', 'Céréales', 'Tubercules', 'Autres'];

onMounted(() => {
  productStore.fetchProducts();
});

const openModal = (product = null) => {
  selectedFile.value = null;
  uploadError.value = null;
  submitError.value = null;
  
  if (product) {
    isEditing.value = true;
    editingId.value = product.id;
    formData.value = { ...product };
  } else {
    isEditing.value = false;
    editingId.value = null;
    formData.value = {
      name: '',
      category: 'Légumes',
      price_per_kg: '',
      quantity_available: '',
      description: '',
      image_url: ''
    };
  }
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedFile.value = null;
  uploadError.value = null;
  submitError.value = null;
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      uploadError.value = "L'image ne doit pas dépasser 5MO";
      return;
    }
    selectedFile.value = file;
    uploadError.value = null;
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      formData.value.image_url = e.target.result; // Temporary preview
    };
    reader.readAsDataURL(file);
  }
};

const handleSubmit = async () => {
  submitError.value = null;
  try {
    let imageUrl = formData.value.image_url;

    // Upload image if a new file is selected
    if (selectedFile.value) {
      // If we are editing and replacing an image, we might want to delete the old one, 
      // but let's just upload the new one for now.
      // We need a cleaner way to generate IDs, using timestamp is simple enough.
      const productId = isEditing.value ? editingId.value : `new-${Date.now()}`;
      try {
        imageUrl = await storageService.uploadProductImage(selectedFile.value, productId);
      } catch (e) {
        console.error("Upload failed", e);
        uploadError.value = "Échec du téléchargement de l'image. Vérifiez votre connexion.";
        throw new Error("L'upload de l'image a échoué.");
      }
    }

    const productData = {
      ...formData.value,
      image_url: imageUrl
    };

    if (isEditing.value) {
      await productStore.updateProduct(editingId.value, productData);
    } else {
      await productStore.createProduct(productData);
    }
    closeModal();
  } catch (error) {
    console.error('Operation failed', error);
    submitError.value = error.message || "Une erreur s'est produite lors de la création du produit.";
  }
};

const handleDelete = async (id) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce produit?')) {
    await productStore.deleteProduct(id);
  }
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Mon Tableau de Bord</h1>
        <p class="text-gray-600">Gérez vos produits et votre inventaire</p>
      </div>
      
      <button 
        @click="openModal()"
        class="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-full font-bold shadow-lg transition flex items-center gap-2"
      >
        <Plus class="w-5 h-5" />
        Ajouter un Produit
      </button>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="bg-primary-100 p-3 rounded-full text-primary-600">
          <Package class="w-8 h-8" />
        </div>
        <div>
          <p class="text-gray-500 text-sm">Total Produits</p>
          <p class="text-2xl font-bold text-gray-900">{{ farmerProducts.length }}</p>
        </div>
      </div>
    </div>
    
    <!-- Products Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-xl font-bold text-gray-800">Vos Annonces</h2>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-gray-500 text-sm uppercase">
            <tr>
              <th class="px-6 py-3 font-medium">Produit</th>
              <th class="px-6 py-3 font-medium">Catégorie</th>
              <th class="px-6 py-3 font-medium">Prix/kg</th>
              <th class="px-6 py-3 font-medium">Stock</th>
              <th class="px-6 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="farmerProducts.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                Vous n'avez pas encore ajouté de produits.
              </td>
            </tr>
            <tr v-for="product in farmerProducts" :key="product.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <img 
                    :src="product.image_url || 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=40'" 
                    class="w-10 h-10 rounded-lg object-cover bg-gray-200"
                  />
                  <span class="font-medium text-gray-900">{{ product.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">{{ product.category }}</span>
              </td>
              <td class="px-6 py-4 font-medium text-primary-600">{{ product.price_per_kg }} FBu</td>
              <td class="px-6 py-4">{{ product.quantity_available }} kg</td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openModal(product)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition" title="Editer">
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button @click="handleDelete(product.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition" title="Supprimer">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div @click="closeModal" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
      
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg relative z-10 p-6 animate-fade-in-up max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-900">{{ isEditing ? 'Modifier le Produit' : 'Ajouter un Produit' }}</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nom du Produit</label>
            <input v-model="formData.name" type="text" required class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-primary-500 focus:border-primary-500" placeholder="Ex: Haricots rouges" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
              <select v-model="formData.category" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-primary-500 focus:border-primary-500">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Quantité (kg)</label>
              <input v-model.number="formData.quantity_available" type="number" min="1" required class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-primary-500 focus:border-primary-500" />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Prix par kg (FBu)</label>
            <input v-model.number="formData.price_per_kg" type="number" min="1" required class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-primary-500 focus:border-primary-500" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="formData.description" rows="3" class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-primary-500 focus:border-primary-500" placeholder="Description courte (qualité, origine...)"></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Image du Produit</label>
            <div class="relative border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:bg-gray-50 transition cursor-pointer" @click="$refs.fileInput.click()">
              <input 
                ref="fileInput"
                type="file" 
                accept="image/*" 
                class="hidden" 
                @change="handleFileSelect"
              />
              <div v-if="formData.image_url" class="relative">
                <img :src="formData.image_url" class="mx-auto h-48 object-cover rounded-md" />
                <div class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 hover:opacity-100 transition rounded-md">
                  <span class="text-white font-medium">Changer l'image</span>
                </div>
              </div>
              <div v-else class="flex flex-col items-center py-4">
                <Upload class="w-8 h-8 text-gray-400 mb-2" />
                <span class="text-sm text-gray-500">Cliquez pour ajouter une photo</span>
              </div>
            </div>
            <p v-if="uploadError" class="text-red-500 text-xs mt-1">{{ uploadError }}</p>
          </div>
          
          <div v-if="submitError" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm mb-4">
            {{ submitError }}
          </div>

          <div class="pt-4 flex gap-3">
            <button type="button" @click="closeModal" class="flex-1 bg-white border border-gray-300 text-gray-700 py-2.5 rounded-lg hover:bg-gray-50 font-medium">Annuler</button>
            <button type="submit" :disabled="isLoading" class="flex-1 bg-primary-600 text-white py-2.5 rounded-lg hover:bg-primary-700 font-bold flex justify-center items-center gap-2 disabled:opacity-50">
              <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
              {{ isEditing ? 'Mettre à jour' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
