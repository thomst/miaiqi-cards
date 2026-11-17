(function() {
    "use strict";

    function update(container, html) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        container.replaceWith(wrapper.firstChild);
        init();
    }

    function request(container, url, data) {
        fetch(url, data)
        .then(function(response) {
            if (!response.ok) throw new Error(response.statusText);
            return response.text();
        })
        .then(function(html) { update(container, html); })
        .catch(function() {
            alert('Error sending the message.');
        });
    }

    function submit(event) {
        event.preventDefault();
        const form = event.target;
        const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        request(form.closest('div.contact'), form.dataset.url, {
            method: 'POST',
            credentials: 'same-origin',
            body: new FormData(form),
            headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken}
        });
    }

    function newMessage(event) {
        request(event.target.closest('div.contact'), event.target.dataset.url, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
    }

    function init() {
        document.querySelectorAll('div.contact form').forEach(function(form) {
            form.addEventListener('submit', submit);
        });
        document.querySelectorAll('div.contact input[data-action="new"]').forEach(function(button) {
            button.addEventListener('click', newMessage);
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();
