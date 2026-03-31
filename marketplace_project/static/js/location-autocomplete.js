document.addEventListener('DOMContentLoaded', function() {
    const cityInputs = document.querySelectorAll('.city-autocomplete');
    
    cityInputs.forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative w-100';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const dropdown = document.createElement('div');
        dropdown.className = 'dropdown-menu w-100 shadow-sm border-0 mt-1';
        dropdown.style.maxHeight = '200px';
        dropdown.style.overflowY = 'auto';
        wrapper.appendChild(dropdown);

        let locations = [];
        let debounceTimer;

        // Fetch locations once
        fetch('/static/data/locations.json')
            .then(res => res.json())
            .then(data => {
                locations = data;
            });

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.toLowerCase().trim();
                dropdown.innerHTML = '';
                
                if (query.length < 1) {
                    dropdown.classList.remove('show');
                    return;
                }

                const filtered = locations.filter(item => 
                    item.city.toLowerCase().includes(query)
                );

                if (filtered.length > 0) {
                    filtered.forEach(item => {
                        const btn = document.createElement('button');
                        btn.type = 'button';
                        btn.className = 'dropdown-item py-2 px-3';
                        btn.textContent = item.city;
                        btn.addEventListener('click', () => {
                            input.value = item.city;
                            dropdown.classList.remove('show');
                        });
                        dropdown.appendChild(btn);
                    });
                    dropdown.classList.add('show');
                } else {
                    dropdown.classList.remove('show');
                }
            }, 300);
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });
});
