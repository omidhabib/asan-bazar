/**
 * favorites.js - Toggle favorite ads with AJAX
 * Includes CSRF handling and heart animation
 */

function toggleFavorite(event, adId, btn) {
    event.preventDefault();
    event.stopPropagation();
    
    console.log('[DEBUG] toggleFavorite called - adId:', adId);
    
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (!csrfMeta) {
        console.error('[ERROR] CSRF token meta tag not found');
        alert('Güvenlik hatası: CSRF token bulunamadı');
        return;
    }
    
    const csrfToken = csrfMeta.getAttribute('content');
    const url = btn.dataset.url;
    
    console.log('[DEBUG] CSRF Token found:', !!csrfToken);
    console.log('[DEBUG] Fetch URL:', url);
    
    if (!url) {
        console.error('[ERROR] data-url attribute missing on button');
        alert('Hata: URL bulunamadı');
        return;
    }

    fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(res => {
        console.log('[DEBUG] Response status:', res.status);
        if (res.status === 401) {
            console.log('[DEBUG] Not authenticated - redirecting to login');
            window.location.href = '/login/';
            return null;
        }
        if (res.status === 302 || res.redirected) {
            window.location.href = '/login/';
            return null;
        }
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        console.log('[DEBUG] Response data:', data);
        if (!data) return;
        const icon = btn.querySelector('svg') || btn.querySelector('i');
        if (data.is_favorited) {
            btn.classList.add('active');
            if (icon && icon.tagName === 'SVG') {
                icon.classList.remove('text-gray-400', 'stroke-current');
                icon.classList.add('fill-red-500', 'stroke-red-500');
            } else if (icon) {
                btn.classList.remove('text-muted');
                btn.classList.add('text-danger');
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
            }
        } else {
            btn.classList.remove('active');
            if (icon && icon.tagName === 'SVG') {
                icon.classList.add('text-gray-400', 'stroke-current');
                icon.classList.remove('fill-red-500', 'stroke-red-500');
            } else if (icon) {
                btn.classList.add('text-muted');
                btn.classList.remove('text-danger');
                icon.classList.add('bi-heart');
                icon.classList.remove('bi-heart-fill');
            }
        }
        const countEl = document.getElementById('fav-count');
        if (countEl) countEl.textContent = data.count;

        if (icon) {
            icon.style.transform = 'scale(1.3)';
            setTimeout(() => { icon.style.transform = 'scale(1)'; }, 150);
        }
    })
    .catch(err => {
        console.error('[ERROR] Favorite error:', err);
        alert('Beğeni hatası: ' + err.message);
    });
}
