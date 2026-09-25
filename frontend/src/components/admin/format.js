const numberFormat = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
const dateFormat = new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
const dateTimeFormat = new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
});

export const formatNumber = (value) => numberFormat.format(Number(value) || 0);
export const formatFbu = (value) => `${formatNumber(value)} FBu`;
export const formatDate = (value) => (value ? dateFormat.format(new Date(value)) : '—');
export const formatDateTime = (value) => (value ? dateTimeFormat.format(new Date(value)) : '—');

export const ROLE_LABELS = {
    farmer: 'Agriculteur',
    buyer: 'Acheteur',
    admin: 'Administrateur'
};

export const ROLE_BADGES = {
    farmer: 'bg-primary-100 text-primary-800',
    buyer: 'bg-blue-100 text-blue-800',
    admin: 'bg-earth-200 text-earth-900'
};

export const CATEGORIES = ['Légumes', 'Fruits', 'Céréales', 'Tubercules', 'Autres'];

export const ACTION_LABELS = {
    'user.role_changed': 'Rôle modifié',
    'user.suspended': 'Utilisateur suspendu',
    'user.restored': 'Utilisateur rétabli',
    'product.removed': 'Annonce supprimée',
    'market_price.created': 'Prix ajouté',
    'market_price.deleted': 'Prix supprimé'
};
