/**
 * infinite-scroll.js - IntersectionObserver-based infinite scroll
 * Appends cards from /api/ads/ endpoint as the user scrolls down
 */

document.addEventListener('DOMContentLoaded', () => {
    const sentinel = document.getElementById('scroll-sentinel');
    const grid = document.getElementById('ads-grid');
    const skeletons = document.getElementById('skeleton-container');
    const endMsg = document.getElementById('end-of-feed');
    if (!sentinel || !grid) return;

    let page = parseInt(sentinel.dataset.page) || 2;
    let hasMore = sentinel.dataset.hasMore === 'true';
    let loading = false;

    const query = sentinel.dataset.query || '';
    const category = sentinel.dataset.category || '';

    const loadMore = () => {
        if (loading || !hasMore) return;
        loading = true;

        if (skeletons) skeletons.classList.remove('hidden');

        const params = new URLSearchParams({ page });
        if (query) params.set('q', query);
        if (category) params.set('category', category);

        fetch(`/api/ads/?${params}`)
            .then(res => res.json())
            .then(data => {
                if (skeletons) skeletons.classList.add('hidden');

                if (data.html) {
                    grid.insertAdjacentHTML('beforeend', data.html);
                }

                hasMore = data.has_more;
                page += 1;
                loading = false;

                if (!hasMore && endMsg) {
                    endMsg.classList.remove('hidden');
                    observer.disconnect();
                }
            })
            .catch(() => {
                loading = false;
                if (skeletons) skeletons.classList.add('hidden');
            });
    };

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            loadMore();
        }
    }, { rootMargin: '200px' });

    if (hasMore) {
        observer.observe(sentinel);
    } else if (endMsg) {
        endMsg.classList.remove('hidden');
    }
});
