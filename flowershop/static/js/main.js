/* Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keyup', debounce(handleSearch, 300));
    }
});

function handleSearch(e) {
    const query = e.target.value.trim();
    if (query.length > 0) {
        fetch(`/products/search/?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                console.log(data);
                // Display dropdown with results
            });
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function updateCartCount() {
    fetch('/cart/count/')
        .then(r => r.json())
        .then(data => {
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = data.count;
                if (data.count === 0) {
                    badge.style.display = 'none';
                } else {
                    badge.style.display = 'block';
                }
            }
        });
}
