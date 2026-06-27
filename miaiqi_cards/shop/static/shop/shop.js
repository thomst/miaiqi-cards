(function() {
    "use strict";

    function updateShop(html) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        document.querySelector('div.shop').replaceWith(wrapper.firstChild);
        init();
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
        const ajaxData = {
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

    var formset;

    class Formset {
        constructor (form) {
            this.form = form;
            this.totalInput = form.querySelector('input[id$="-TOTAL_FORMS"]');
            this.total = parseInt(this.totalInput.value);
            this.initRemoveButtons();
        }
        initRemoveButtons () {
            this.form.querySelectorAll("input.remove-form").forEach(element => {
                element.addEventListener('click', actions.removeForm);
            });

        }
        updateFormCount () {
            this.form.querySelectorAll('div.form').forEach((div, index) => {
                div.querySelectorAll('[name^="form-"]').forEach(element => {
                    element.name = element.name.replace(/form-\d/, `form-${index}`);
                    element.id = element.id.replace(/form-\d/, `form-${index}`);
                });
            });
        }
        addForm () {
            this.total++;
            this.totalInput.value = this.total;
            const firstForm = this.form.querySelector('div:nth-child(1 of .form)');
            const lastForm = this.form.querySelector('div:nth-last-child(1 of .form)');
            const newForm = firstForm.cloneNode(true);
            newForm.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
            lastForm.after(newForm);
            this.updateFormCount();
            this.initRemoveButtons();
        }
        removeForm (event) {
            if (this.total == 1) {
                const form = event.target.parentNode.parentNode;
                form.querySelectorAll('[name^="form-"]').forEach(element => { element.value = ''; });
                form.querySelector('input[name^="form-"]').value = '';
            } else {
                this.total--;
                this.totalInput.value = this.total;
                event.target.parentNode.parentNode.remove();
                this.updateFormCount();
            }
        }
    }


    const actions = {
        addForm: function(event) {
            formset.addForm();
        },
        removeForm: function(event) {
            formset.removeForm(event);
        },
        checkout: function(event) {
            postRequest(event);
        },
        order: function(event) {
            getRequest(event);
        },
        confirmation: function(event) {
            postRequest(event);
        }
    }

    function initButtons() {
        const buttons = document.querySelectorAll('div.row input[data-action]');
        for (const button of buttons) {
            button.addEventListener('click', actions[button.dataset.action]);
        }
    }

    function init () {
        initButtons();
        const form = document.querySelector('div.shop form:has(div.form)');
        if (form) formset = new Formset(form);
    }

    document.addEventListener('DOMContentLoaded', init);
})();
