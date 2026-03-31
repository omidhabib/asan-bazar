/**
 * search.js - Live search with debouncing and AJAX dropdown
 */

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('live-search-input');
    const dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;

    let debounceTimer;

    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const query = input.value.trim();

        if (query.length < 2) {
            dropdown.classList.add('hidden');
            dropdown.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.results.length === 0) {
                        dropdown.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500">No results found.</div>';
                    } else {
                        dropdown.innerHTML = data.results.map(ad => `
                            <a href="${ad.url}" class="flex items-center gap-3 px-4 py-3 hover:bg-indigo-50 transition border-b border-gray-50 last:border-0">
                                ${ad.image
                                    ? `<img src="${ad.image}" class="w-10 h-10 rounded-lg object-cover shrink-0">`
                                    : `<div class="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0"><span class="text-indigo-400 text-lg">📦</span></div>`
                                }
                                <div class="min-w-0">
                                    <p class="text-sm font-semibold text-gray-800 truncate">${ad.title}</p>
                                    <p class="text-xs text-gray-400">${ad.location} · <span class="text-indigo-600 font-bold">AFN ${parseFloat(ad.price).toLocaleString()}</span></p>
                                </div>
                            </a>
                        `).join('');
                    }
                    dropdown.classList.remove('hidden');
                });
        }, 280);
    });

    // Submit full search on Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && input.value.trim()) {
            window.location.href = `/?q=${encodeURIComponent(input.value.trim())}`;
        }
    });

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
});
