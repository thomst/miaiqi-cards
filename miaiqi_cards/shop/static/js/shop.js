(function() {
    "use strict";

    function updateShop(html) {
        // If we got html we replace the whole shop div and reinitialize it.
        if (html) {
            const wrapper = document.createElement('div');
            wrapper.innerHTML = html.trim();
            document.querySelector('div.shop').replaceWith(wrapper.firstChild);
            init();
        }
    }

    function ajaxCall(event, data) {
        event.preventDefault();

        // Either take the url dataset of the target element or use the default
        // url set on the form element.
        const formUrl = document.querySelector('div.shop form').dataset.url;
        const url = event.target.dataset.url || formUrl;
        fetch(url, data)
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

    // We need the formset variable available thoughout the code.
    var formset;

    class Formset {
        constructor (form) {
            this.form = form;
            this.totalInput = form.querySelector('input[id$="-TOTAL_FORMS"]');
            this.total = parseInt(this.totalInput.value);
            this.form.querySelectorAll('div.form').forEach((el => {
                this.initEventHandlers(el);
            }))
        }
        initEventHandlers(row) {
            // Set event handler on remove button.
            row.querySelector("input.remove-form").addEventListener('click', actions.removeForm);

            // Set event handler on inputs and selects.
            row.querySelectorAll('input:not(.remove-form), select').forEach((el) => {
                el.addEventListener('change', actions.updateCart);
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
            this.initEventHandlers(newForm);
            lastForm.after(newForm);
            this.updateFormCount();
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
        updateCart: function(event) {
            postRequest(event);
        },
        addForm: function(event) {
            formset.addForm();
        },
        removeForm: function(event) {
            formset.removeForm(event);
            postRequest(event);
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

    function init () {
        // Init the formset.
        const form = document.querySelector('div.shop form:has(div.form)');
        if (form) formset = new Formset(form);

        // Init the Buttons.
        const buttons = document.querySelectorAll('div.shop div.row input[data-action]');
        for (const button of buttons) {
            button.addEventListener('click', actions[button.dataset.action]);
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
