import api from './axios';

export default {
    sendMessage(message, language) {
        return api.post('/chatbot/ask', { message, language });
    },
    getHistory(limit = 50) {
        return api.get('/chatbot/history', { params: { limit } });
    }
};
