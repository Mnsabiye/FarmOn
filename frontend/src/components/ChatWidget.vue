<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { MessageCircle, X, Send, Minimize2 } from 'lucide-vue-next';
import chatbotApi from '../api/chatbot';

const isOpen = ref(false);
const message = ref('');
const messages = ref([]);
const isLoading = ref(false);
const language = ref('fr');
const messagesContainer = ref(null);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value && messages.value.length === 0) {
    // Add initial greeting in French
    messages.value.push({
      id: Date.now(),
      sender: 'bot',
      message_text: "Bonjour! Je suis votre assistant agricole. Comment puis-je vous aider aujourd'hui? (Météo, Prix, Conseils)"
    });
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!message.value.trim() || isLoading.value) return;
  
  const userMsg = message.value.trim();
  message.value = '';
  
  // Add user message
  messages.value.push({
    id: Date.now(),
    sender: 'user',
    message_text: userMsg
  });
  
  await scrollToBottom();
  isLoading.value = true;
  
  try {
    const response = await chatbotApi.sendMessage(userMsg, language.value);
    
    // Add bot response
    messages.value.push({
      id: Date.now() + 1,
      sender: 'bot',
      message_text: response.data.response
    });
  } catch (error) {
    messages.value.push({
      id: Date.now() + 1,
      sender: 'bot',
      message_text: "Désolé, je ne peux pas répondre pour le moment. Veuillez réessayer plus tard."
    });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col items-end">
    <!-- Chat Window -->
    <div 
      v-if="isOpen"
      class="bg-white rounded-lg shadow-xl w-80 sm:w-96 mb-4 overflow-hidden border border-gray-100 flex flex-col transition-all duration-300 ease-in-out transform origin-bottom-right h-[500px]"
    >
      <!-- Header -->
      <div class="bg-primary-600 text-white p-3 flex justify-between items-center shadow-sm">
        <div class="flex items-center gap-2">
          <div class="bg-white p-1 rounded-full">
            <MessageCircle class="w-4 h-4 text-primary-600" />
          </div>
          <h3 class="font-bold text-sm">Assistant Intelligent</h3>
        </div>
        <div class="flex items-center gap-2">
          <select 
            v-model="language" 
            class="bg-primary-700 text-xs rounded px-2 py-1 border-none focus:ring-1 focus:ring-white cursor-pointer"
          >
            <option value="fr">Français</option>
            <option value="rn">Kirundi</option>
          </select>
          <button @click="toggleChat" class="hover:bg-primary-700 p-1 rounded transition">
            <Minimize2 class="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <!-- Messages Area -->
      <div 
        ref="messagesContainer"
        class="flex-1 p-4 overflow-y-auto bg-gray-50 flex flex-col gap-3"
      >
        <div 
          v-for="msg in messages" 
          :key="msg.id"
          :class="[
            'max-w-[80%] rounded-lg p-3 text-sm shadow-sm',
            msg.sender === 'user' 
              ? 'bg-primary-600 text-white self-end rounded-br-none' 
              : 'bg-white text-gray-800 self-start rounded-bl-none border border-gray-100'
          ]"
        >
          {{ msg.message_text }}
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="isLoading" class="bg-white text-gray-500 self-start rounded-lg p-3 text-xs shadow-sm border border-gray-100 flex items-center gap-1">
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-75"></span>
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-150"></span>
        </div>
      </div>
      
      <!-- Input Area -->
      <div class="p-3 bg-white border-t border-gray-100">
        <form @submit.prevent="sendMessage" class="flex items-center gap-2">
          <input 
            v-model="message"
            type="text" 
            :placeholder="language === 'fr' ? 'Posez une question...' : 'Baza ikibazo...'"
            class="flex-1 border-gray-300 rounded-full focus:ring-primary-500 focus:border-primary-500 text-sm py-2 px-4 shadow-sm"
          />
          <button 
            type="submit" 
            :disabled="!message.trim() || isLoading"
            class="bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-full shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send class="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>

    <!-- Toggle Button -->
    <button 
      @click="toggleChat"
      class="bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-lg transition-all duration-300 hover:scale-105 active:scale-95 flex items-center justify-center group"
    >
      <X v-if="isOpen" class="w-6 h-6" />
      <MessageCircle v-else class="w-6 h-6 group-hover:animate-pulse" />
    </button>
  </div>
</template>
