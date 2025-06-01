document.addEventListener('DOMContentLoaded', function() {
    if (typeof jQuery !== 'undefined') {
        alert('jQuery fonctionne et le thème JS est chargé !');
    } else {
        console.log('jQuery n\'est pas encore disponible.');
    }
});