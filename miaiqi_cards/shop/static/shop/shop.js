(function() {
    "use strict";

    function updateShop(html) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        document.querySelector('div.shop').replaceWith(wrapper.firstChild);
        initButtons();
    }

    function ajaxCall(event, data) {
        event.preventDefault();

        fetch(event.target.dataset.url, data)
        .then(function(response) {
            if (!response.ok) throw new Error(response.text());
            return response.text();
        })
        .then(updateShop)
        .catch(function() {
            alert('Error reloading the formset.');
        });
    }

    function getRequest(event) {
        ajaxData = {
            method: "GET",
            credentials: 'same-origin',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        }
        ajaxCall(event, ajaxData)
    }

    function postRequest(event) {
        const form = document.querySelector('div.shop > form');
        const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        const ajaxData = {
            method: "POST",
            credentials: 'same-origin',
            body: new FormData(form),
            headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken}
        }
        ajaxCall(event, ajaxData)
    }

    const actions = {
        addForm: function(event) {
            event.preventDefault();
            const totalForms = document.querySelector('div.shop input[id$=-TOTAL_FORMS');
            const currentValue = parseInt(totalForms.value, 10);
            totalForms.value = currentValue + 1;
            postRequest(event)

        }
    }

    function initButtons() {
        const buttons = document.querySelectorAll('div.buttons > input');
        for (const button of buttons) {
            button.addEventListener('click', actions[button.dataset.action]);
        }
    }

    document.addEventListener('DOMContentLoaded', initButtons);
})();
