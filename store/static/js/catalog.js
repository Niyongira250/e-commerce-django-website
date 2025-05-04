document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('search-input');
    const suggestions = document.getElementById('suggestions');

    input.addEventListener('input', function () {
        const query = input.value.trim();
        if (query.length === 0) {
            suggestions.innerHTML = '';
            return;
        }

        fetch(`/search_suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                suggestions.innerHTML = '';
                data.results.forEach(item => {
                    const div = document.createElement('div');
                    div.textContent = item;
                    div.addEventListener('click', () => {
                        input.value = item;
                        suggestions.innerHTML = '';
                        document.getElementById('search-form').submit();
                    });
                    suggestions.appendChild(div);
                });
            });
    });
});
 
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const suggestionsBox = document.getElementById('suggestions');

    searchInput.addEventListener('input', function () {
        const query = this.value;

        if (query.length > 1) {
            fetch(`/autocomplete/?term=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.textContent = item;
                        div.onclick = () => {
                            searchInput.value = item;
                            suggestionsBox.innerHTML = '';
                        };
                        suggestionsBox.appendChild(div);
                    });
                });
        } else {
            suggestionsBox.innerHTML = '';
        }
    });

    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = '';
        }
    });
});

