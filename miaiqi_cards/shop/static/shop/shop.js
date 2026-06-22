document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.querySelector('div.buttons input[type="button"]');
    if (!addButton) return;

    addButton.addEventListener('click', function(event) {
        event.preventDefault();

        const form = document.querySelector('div.shop > form');
        const totalForms = form.querySelector('div.shop input[id$=-TOTAL_FORMS');
        const currentValue = parseInt(totalForms.value, 10);
        totalForms.value = currentValue + 1;

        fetch(addButton.dataset.url, {
            method: 'POST',
            credentials: 'same-origin',
            data: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(function(html) {
            document.querySelector('div.shop').replaceWith(html);
        })
        .catch(function() {
            alert('Error loading the shop html.');
        });
    });
});
